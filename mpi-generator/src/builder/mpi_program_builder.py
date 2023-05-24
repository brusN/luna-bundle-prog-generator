import json
import logging
import os

from exception.custom_exceptions import OsCommandExecutionException
from handler.cpp_file_handler import CPPFileHandler
from handler.program_recom_handler import IteratorContext, IteratorDescriptor, ProgramRecomHandler
from exception.custom_exceptions import MultiplyCfDescriptorsException, CfNotFoundException
from util.bundle_blocks_parser import BundleControlUnitParser
from util.ref_expr_parsers import BundleIntExpressionParser


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

        self._create_build_folders()
        self._cpp_file_handler = CPPFileHandler(file_name=f'{build_dir}/luna_manual_mpi_program_src.cpp')
        self._bundle_json_file_path = f'{self._build_dir}/bundle.json'

    def build(self):
        self._compile_luna_prog()
        self._get_bundle_json()
        self._luna_fragments = self._program_recom_handler.parse_program_recom_json()
        logging.debug('Luna fragments parsing has finished')
        self._generate_mpi_src()

    def _create_build_folders(self):
        if not os.path.exists(self._build_dir):
            os.mkdir(self._build_dir)
        if not os.path.exists(self._luna_build_dir):
            os.mkdir(self._luna_build_dir)

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
        self._cpp_file_handler.include_std_header('dfmanager.h')

    def _include_extern_code_blocks(self):
        for code_fragment in self._luna_fragments.code_fragments:
            self._cpp_file_handler.include_extern_void_func(self._luna_fragments.code_fragments[code_fragment])

    def _generate_define_df(self, df):
        self._cpp_file_handler.include_define_df(df)

    def _generate_exec_cf(self, cf, rank):
        self._cpp_file_handler.include_cf_execution(cf, self._luna_fragments.code_fragments[cf.code], rank)

    def _generate_send_df(self, df_name, from_rank, to_rank):
        self._cpp_file_handler.include_df_send(df_name, from_rank, to_rank)

    def _handle_for_loop(self, block, iterator_context):
        start_value = BundleIntExpressionParser.get_unwrapped_value(block['startValue'], iterator_context)
        end_value = BundleIntExpressionParser.get_unwrapped_value(block['endValue'], iterator_context)
        it_name = block['iterator']
        iterator_context.add_iterator(IteratorDescriptor(it_name, start_value, end_value))
        cur_iter_values = iterator_context.get_cur_iter_values()
        cartesian_size = iterator_context.get_cartesian_size()
        for i in range(start_value, end_value + 1):
            for exec_block in block['body']:
                match exec_block['type']:
                    case 'run':
                        built_cf_name = BundleControlUnitParser.build_full_cf_name(exec_block['cf'], iterator_context)
                        cf = self._luna_fragments.get_cf(built_cf_name)
                        rank = BundleIntExpressionParser.get_unwrapped_value(exec_block['rank'], iterator_context)
                        self._generate_exec_cf(cf, rank)
                    case 'send':
                        from_rank = BundleIntExpressionParser.get_unwrapped_value(exec_block['from'], iterator_context)
                        to_rank = BundleIntExpressionParser.get_unwrapped_value(exec_block['to'], iterator_context)
                        built_df_name = BundleControlUnitParser.build_full_df_name(exec_block['data'], iterator_context)
                        self._generate_send_df(built_df_name, from_rank, to_rank)
                    case 'for':
                        self._handle_for_loop(exec_block, iterator_context)
            if cartesian_size > 1:
                iterator_context.inc_cur_iter_values(cur_iter_values)
                iterator_context.update_cur_iter_values(cur_iter_values)
        iterator_context.remove_iterator(block['iterator'])

    def _handle_exec_context(self, body, iterator_context):
        for exec_block in body:
            match exec_block['type']:
                case 'df':
                    df = self._luna_fragments.get_df(exec_block['name'])
                    self._generate_define_df(df)
                case 'run':
                    built_cf_name = BundleControlUnitParser.build_full_cf_name(exec_block['cf'], iterator_context)
                    cf = self._luna_fragments.get_cf(built_cf_name)
                    rank = BundleIntExpressionParser.get_unwrapped_value(exec_block['rank'], iterator_context)
                    self._generate_exec_cf(cf, rank)
                case 'send':
                    from_rank = BundleIntExpressionParser.get_unwrapped_value(exec_block['from'], iterator_context)
                    to_rank = BundleIntExpressionParser.get_unwrapped_value(exec_block['to'], iterator_context)
                    self._generate_send_df(exec_block['data'], from_rank, to_rank)
                case 'for':
                    self._handle_for_loop(exec_block, iterator_context)


    def _generate_main_func(self):
        # Include standard MPI program pattern
        self._cpp_file_handler.write_line(f'\
            int main(int argc, char** argv) {{ \
                int rank, size; \
                MPI_Init(&argc, &argv); \
                MPI_Comm_rank(MPI_COMM_WORLD, &rank); \
                MPI_Comm_size(MPI_COMM_WORLD, &size); \
                DFManager dfManager; \
            ')

        # Open generated internal bundle state
        with open(f'{self._bundle_json_file_path}', 'r') as bundle_json_file:
            bundle = json.load(bundle_json_file)

        # Iteration of bundle with subsequent processing of control units
        self._handle_exec_context(bundle['execution'], IteratorContext())

        # Include standard MPI program finalize
        self._cpp_file_handler.write_line(f'\
                MPI_Finalize(); \
                return 0; \
            }}')

    def _generate_mpi_src(self):
        self._include_headers()
        self._include_extern_code_blocks()
        self._generate_main_func()
        self._finalize()

    def _finalize(self):
        self._cpp_file_handler.finalize()
