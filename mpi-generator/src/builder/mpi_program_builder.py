import json
import logging
import os
from handler.cpp_file_handler import CPPFileHandler
from exception.custom_exceptions import OsCommandExecutionException
from handler.program_recom_handler import ProgramRecomHandler


class MPIProgramBuilder:
    def __init__(self, build_config, luna_compiler_path='luna', luna_bundle_parser='luna-bundle-parser',
                 luna_build_dir='luna_compile_temp', build_dir='build'):
        # Passed required files and information for generating MPI src
        self.build_config = build_config

        # Required binaries from PATH
        self._luna_compiler_path = luna_compiler_path
        self._luna_bundle_parser = luna_bundle_parser

        # LuNA compiler options
        self._luna_build_dir = luna_build_dir
        self._luna_compiler_flags = ['--compile-only', f'--build-dir={self._luna_build_dir}']
        self._build_dir = build_dir

        self._luna_fragments = None
        self._program_recom_handler = ProgramRecomHandler(luna_build_dir=luna_build_dir)

        logging.debug('Working directory is ' + os.getcwd())
        self._create_build_folders()
        self._cpp_file_handler = CPPFileHandler(file_name=f'{build_dir}/luna_manual_mpi_program_src.cpp')
        self._bundle_json_file_path = f'{self._build_dir}/bundle.json'

    def build(self):
        self._compile_luna_prog()
        self._get_bundle_json()
        self._luna_fragments = self._program_recom_handler.parse_program_recom_json()
        logging.debug('Build has finished')
        # self.generate_mpi_src()
        # self.finalize()

    def _create_build_folders(self):
        if not os.path.exists(self._build_dir):
            os.mkdir(self._build_dir)
        if not os.path.exists(self._luna_build_dir):
            os.mkdir(self._luna_build_dir)

    def _clean(self):
        pass

    def _compile_luna_prog(self):
        logging.info('Getting meta information about LuNA program')

        # Example: luna --compile-only --build-dir=build program.fa
        compile_os_command = '{luna_compiler_path} {luna_compiler_flags} {luna_src_path}'.format(
            luna_compiler_path=self._luna_compiler_path,
            luna_compiler_flags=' '.join(self._luna_compiler_flags),
            luna_src_path=self.build_config.luna_src_path
        )
        error_code = os.system(compile_os_command)
        if error_code != 0:
            raise OsCommandExecutionException('Error while building LuNA program')

    def _get_bundle_json(self):
        logging.info('Converting bundle into JSON internal state')

        # Example: luna-bundle-parser bundle.bndl bundle.json
        compile_os_command = '{luna_bundle_parser} {bundle_path} {output_json_path}'.format(
            luna_bundle_parser=self._luna_bundle_parser,
            bundle_path=self.build_config.bundle_file_path,
            output_json_path=self._bundle_json_file_path,
        )
        error_code = os.system(compile_os_command)
        if error_code != 0:
            raise OsCommandExecutionException('Error while parsing bundle file')

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

    def generate_mpi_src(self):
        self._include_headers()
        self._include_extern_code_blocks()
        self._generate_main_func()

    def finalize(self):
        self._cpp_file_handler.finalize()
