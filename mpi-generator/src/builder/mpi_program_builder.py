import json
import logging
import os
from handler.cpp_file_handler import CPPFileHandler


class ILunaFragment:

    def to_cpp_src(self):
        pass


class FunctionArgumentDescriptor:
    type: str
    name: str

    def to_string(self):
        return f'{self.type} {self.name}'


class CalculationFragmentArgument:
    def toStr(self):
        pass


class ConstCFArgument(CalculationFragmentArgument):
    def __init__(self, value):
        self.value = value

    def toStr(self):
        return str(self.value)


class VarCFArgument(CalculationFragmentArgument):
    def __init__(self, name):
        self.name = name

    def toStr(self):
        return self.name


class CodeFragment(ILunaFragment):
    name: str
    args: list

    def __init__(self):
        self.args = []

    def to_cpp_src(self):
        return f'void {self.name}();'


class CalculationFragment(ILunaFragment):
    name: str
    code: str
    args: list

    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.args = []


class DataFragment(ILunaFragment):
    name: str

    def __init__(self, name):
        self.name = name

    def to_cpp_src(self):
        return f'DF {self.name};'


class LunaFragments:
    data_fragments: dict
    code_fragments: dict
    calculation_fragments: dict

    def __init__(self):
        self.data_fragments = {}
        self.code_fragments = {}
        self.calculation_fragments = {}


class ArgTypeMapper:
    types_map: dict

    def __init__(self):
        self.types_map = {
            'int': 'int',
            'real': 'double',
            'string': 'string',
            'name': 'DF &',
            'value': 'const DF &'
        }

    def get_mapped_type(self, arg_type):
        return self.types_map[arg_type]


class MPIProgramBuilder:
    def __init__(self, build_config):
        self.build_config = build_config

        self._luna_compiler_path = 'luna'
        self._luna_build_dir = 'build'
        self._luna_compiler_flags = ['--compile-only', f'--build-dir={self._luna_build_dir}']

        self.args_type_mapper = ArgTypeMapper()
        self.data = LunaFragments()
        self.cpp_file_handler = CPPFileHandler(fileName='mpi_prog.cpp')

    def compile_luna_prog(self):
        # Example: luna --compile-only --build-dir=build program.fa
        compile_os_command = '{luna_compiler_path} {luna_compiler_flags} {luna_src_path}'.format(
            luna_compiler_path=self._luna_compiler_path,
            luna_compiler_flags=' '.join(self._luna_compiler_flags),
            luna_src_path=self.build_config.luna_src_path
        )

        logging.info('Compiling LuNA program >>> ' + compile_os_command)
        os.system(compile_os_command)

    def parse_program_recom_json(self):
        with open(f'{self._luna_build_dir}/program_recom.ja', 'r') as program_recom_json_file:
            program_recom_json = json.load(program_recom_json_file)

        # Parsing import code blocks statements
        for block_name in program_recom_json:
            raw = program_recom_json[block_name]
            if raw['type'] == 'extern':
                code_fragment = CodeFragment()
                code_fragment.name = raw['code']

                arg_index = 0
                for arg in raw['args']:
                    func_arg = FunctionArgumentDescriptor()
                    func_arg.type = self.args_type_mapper.get_mapped_type(arg['type'])
                    func_arg.name = 'arg' + str(arg_index)
                    code_fragment.args.append(func_arg)
                    arg_index += 1

                self.data.code_fragments[code_fragment.name] = code_fragment

        # Parsing calculation fragments
        prog_body = program_recom_json['main']['body']
        for block in prog_body:
            if block['type'] != 'exec':
                continue
            fragment = CalculationFragment(block['id'][0], block['code'])
            cf_args = block['args']
            for arg in cf_args:
                if arg['type'] == 'iconst':
                    fragment.args.append(ConstCFArgument(arg['value']))
                elif arg['type'] == 'id':
                    fragment.args.append(VarCFArgument(arg['ref'][0]))
            self.data.calculation_fragments[fragment.name] = fragment

    def _include_headers(self):
        self.cpp_file_handler.include_std_header(self.build_config.mpi_header)
        self.cpp_file_handler.write_empty_line()

    def _include_extern_code_blocks(self):
        for code_fragment in self.data.code_fragments:
            self.cpp_file_handler.include_extern_void_func(self.data.code_fragments[code_fragment])
        self.cpp_file_handler.write_empty_line()

    def _init_mpi(self):
        self.cpp_file_handler.write_line("int rank, size;")
        self.cpp_file_handler.write_line("MPI_Init(&argc, &argv);")
        self.cpp_file_handler.write_line("MPI_Comm_rank(MPI_COMM_WORLD, &rank);")
        self.cpp_file_handler.write_line("MPI_Comm_size(MPI_COMM_WORLD, &size);")

    def _finalize_mpi(self):
        self.cpp_file_handler.write_line("MPI_Finalize();")

    def _generate_define_df(self, df_name):
        self.cpp_file_handler.include_define_df(df_name)

    def _generate_exec_cf(self, cf, rank):
        self.cpp_file_handler.include_cf_execution(cf['code'], rank)

    def _generate_send_df(self, df_name, from_rank, to_rank):
        self.cpp_file_handler.include_df_send(df_name, from_rank, to_rank)

    def _generate_program_body(self):
        with open(f'{self.build_config.bundle_json_file_path}', 'r') as bundle_json_file:
            bundle = json.load(bundle_json_file)

        # Defining all data fragments
        execute = bundle['execute']
        for exec_block in execute:
            match exec_block['type']:
                case 'df':
                    self._generate_define_df(exec_block['name'])
                case 'run':
                    self._generate_exec_cf(`self.data.calculation_fragments[exec_block['cfs']]:`, exec_block['rank'])
                case 'send':
                    self._generate_send_df(exec_block['data'], exec_block['from'], exec_block['to'])

    def _generate_main_func(self):
        self.cpp_file_handler.write_line("int main(int argc, char** argv) {")

        # Main func body
        self._init_mpi()
        self._generate_program_body()
        self._finalize_mpi()

        # Main func body end
        self.cpp_file_handler.write_line("return 0;}")

    def _define_data_fragments(self, file):
        pass

    def generate_mpi_src(self):
        self._include_headers()
        self._include_extern_code_blocks()
        self._generate_main_func()

    def generate_program(self):
        pass
