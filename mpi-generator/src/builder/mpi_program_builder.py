import json
import logging
import os
from handler.cpp_file_handler import CPPFileHandler
from exception.custom_exceptions import OsCommandExecutionException
from luna_fragments import *


# Stores parsed fragments from program_recom.ja file
class LunaFragments:
    data_fragments: dict
    code_fragments: dict
    calculation_fragments: dict

    def __init__(self):
        self.data_fragments = {}
        self.code_fragments = {}
        self.calculation_fragments = {}


# Converter LuNA types to C++ types
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


# MPI src generator
class MPIProgramBuilder:
    def __init__(self, build_config):
        # Passed required files and information for generating MPI src
        self.build_config = build_config

        # Required binaries from PATH
        self._luna_compiler_path = 'luna'
        self._luna_bundle_parser = 'luna-bundle-parser'

        # LuNA compiler options
        self._luna_build_dir = 'build'
        self._luna_compiler_flags = ['--compile-only', f'--build-dir={self._luna_build_dir}']

        self._args_type_mapper = ArgTypeMapper()
        self._data = LunaFragments()
        self._cpp_file_handler = CPPFileHandler(fileName=self.build_config.output)
        self._bundle_json_file_path = self._luna_build_dir + '/prog_bundle.json'

    def _compile_luna_prog(self):
        # Example: luna --compile-only --build-dir=build program.fa
        compile_os_command = '{luna_compiler_path} {luna_compiler_flags} {luna_src_path}'.format(
            luna_compiler_path=self._luna_compiler_path,
            luna_compiler_flags=' '.join(self._luna_compiler_flags),
            luna_src_path=self.build_config.luna_src_path
        )
        logging.info('Compiling LuNA program >>> ' + compile_os_command)
        error_code = os.system(compile_os_command)
        if error_code != 0:
            raise OsCommandExecutionException('Error while building LuNA program')

    def _get_bundle_json(self):
        compile_os_command = '{luna_bundle_parser} {bundle_path} {output_json_path}'.format(
            luna_bundle_parser=self._luna_bundle_parser,
            bundle_path=self.build_config.bundle_file_path,
            output_json_path=self._bundle_json_file_path,
        )
        logging.info('Parsing bundle file >>> ' + compile_os_command)
        error_code = os.system(compile_os_command)
        if error_code != 0:
            raise OsCommandExecutionException('Error while parsing bundle file')

    def _parse_program_recom_json(self):
        with open(f'{self._luna_build_dir}/program_recom.ja', 'r') as program_recom_json_file:
            program_recom_json = json.load(program_recom_json_file)

        # Parsing import code blocks statements
        for block_name in program_recom_json:
            raw = program_recom_json[block_name]
            if raw['type'] == 'extern':
                code_fragment = CodeFragment()
                code_fragment.name = block_name
                code_fragment.code = raw['code']

                arg_index = 0
                for arg in raw['args']:
                    func_arg = FunctionArgumentDescriptor()
                    func_arg.type = self._args_type_mapper.get_mapped_type(arg['type'])
                    func_arg.name = 'arg' + str(arg_index)
                    code_fragment.args.append(func_arg)
                    arg_index += 1

                self._data.code_fragments[code_fragment.name] = code_fragment

        # Parsing calculation fragments
        prog_body = program_recom_json['main']['body']
        for block in prog_body:
            if block['type'] != 'exec':
                continue
            fragment = CalculationFragment(block['id'][0], block['code'])  # <<<<<
            cf_args = block['args']
            for arg in cf_args:
                if arg['type'] == 'iconst':
                    fragment.args.append(ConstCFArgument(arg['value']))
                elif arg['type'] == 'id':
                    fragment.args.append(VarCFArgument(arg['ref'][0]))
            self._data.calculation_fragments[fragment.name] = fragment

    def _include_headers(self):
        self._cpp_file_handler.include_std_header(self.build_config.mpi_header)
        self._cpp_file_handler.include_std_header('df.h')
        self._cpp_file_handler.write_empty_line()

    def _include_extern_code_blocks(self):
        for code_fragment in self._data.code_fragments:
            self._cpp_file_handler.include_extern_void_func(self._data.code_fragments[code_fragment])
        self._cpp_file_handler.write_empty_line()

    def _init_mpi(self):
        self._cpp_file_handler.write_line("int rank, size;")
        self._cpp_file_handler.write_line("MPI_Init(&argc, &argv);")
        self._cpp_file_handler.write_line("MPI_Comm_rank(MPI_COMM_WORLD, &rank);")
        self._cpp_file_handler.write_line("MPI_Comm_size(MPI_COMM_WORLD, &size);")

    def _finalize_mpi(self):
        self._cpp_file_handler.write_line("MPI_Finalize();")

    def _generate_define_df(self, df_name):
        self._cpp_file_handler.include_define_df(df_name)

    def _generate_exec_cf(self, cf, rank):
        self._cpp_file_handler.include_cf_execution(cf, self._data.code_fragments[cf.code], rank)

    def _generate_send_df(self, df_name, from_rank, to_rank):
        self._cpp_file_handler.include_df_send(df_name, from_rank, to_rank)

    def _generate_program_body(self):
        with open(f'{self._bundle_json_file_path}', 'r') as bundle_json_file:
            bundle = json.load(bundle_json_file)

        # Defining all data fragments
        for exec_block in bundle['execute']:
            match exec_block['type']:
                case 'df':
                    self._generate_define_df(exec_block['name'])
                case 'run':
                    self._generate_exec_cf(self._data.calculation_fragments[exec_block['cfs']], exec_block['rank'])
                case 'send':
                    self._generate_send_df(exec_block['data'], exec_block['from'], exec_block['to'])

    def _generate_main_func(self):
        self._cpp_file_handler.write_line("int main(int argc, char** argv) {")

        # Main func body      <--
        self._init_mpi()
        self._generate_program_body()
        self._finalize_mpi()
        # Main func body end' <--

        self._cpp_file_handler.write_line("return 0;}")

    def _define_data_fragments(self, file):
        pass

    def generate_mpi_src(self):
        self._include_headers()
        self._include_extern_code_blocks()
        self._generate_main_func()

    def finalize(self):
        self._cpp_file_handler.finalize()
