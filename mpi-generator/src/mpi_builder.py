import json
import os
import logging
from build_config_parser import BuildConfig


class ILunaFragment:

    def toCPPSourceCode(self):
        pass


class FunctionArgumentDescriptor:
    type: str
    name: str

    def to_string(self):
        return f'{self.type} {self.name}'


class CodeFragment(ILunaFragment):
    name: str
    args: list

    def __init__(self):
        self.args = []

    def toCPPSourceCode(self):
        return f'void {self.name}();'


class CalculationFragment(ILunaFragment):
    pass


class LunaFragments:
    data_fragments: list
    code_fragments: list
    calculation_fragments: list

    def __init__(self):
        self.code_fragments = []
        self.calculation_fragments = []


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


class CPPFileHandler:
    @classmethod
    def write_empty_line(cls, file):
        file.write('\n')

    @classmethod
    def include_user_header(cls, file, header_name):
        file.write(f'#include "{header_name}"')

    @classmethod
    def include_std_header(cls, file, header_name):
        file.write(f'#include <{header_name}>')
        cls.write_empty_line(file)

    @classmethod
    def include_extern_void_func(cls, file, code_fragment):
        args = ''
        for arg in code_fragment.args:
            args += arg.to_string() + ', '
        args = args[:-2]
        file.write(f'void {code_fragment.name}({args});')
        cls.write_empty_line(file)


class MPIProgramBuilder:
    _luna_compiler_path = 'luna'
    _luna_build_dir = 'build'
    _luna_compiler_flags = ['--compile-only', f'--build-dir={_luna_build_dir}']
    build_config: BuildConfig
    args_type_mapper: ArgTypeMapper
    data: LunaFragments

    def __init__(self, build_config):
        self.build_config = build_config
        self.args_type_mapper = ArgTypeMapper()
        self.data = LunaFragments()

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

                self.data.code_fragments.append(code_fragment)

        # Parsing calculation blocks


    def _include_headers(self, file):
        CPPFileHandler.include_std_header(file, self.build_config.mpi_header)
        CPPFileHandler.write_empty_line(file)

    def _include_extern_code_blocks(self, file):
        for code_fragment in self.data.code_fragments:
            CPPFileHandler.include_extern_void_func(file, code_fragment)

        CPPFileHandler.write_empty_line(file)

    def generate_mpi_src(self):
        file = open('mpi_prog.cpp', 'w+')
        self._include_headers(file)
        self._include_extern_code_blocks(file)
        file.close()
