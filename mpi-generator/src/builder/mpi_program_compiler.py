import logging
import os

from exception.custom_exceptions import OsCommandExecutionException


class IProgramCompiler:
    def compile(self, mpi_prog_cpp, ucodes_cpp, output_name):
        pass


class MPIProgramCompiler(IProgramCompiler):

    def __init__(self):
        self._mpi_compiler = 'mpic++'
        self._luna_home_path = os.environ['LUNA_HOME']

    def compile(self, mpi_prog_cpp, ucodes_cpp, output_name):
        luna_src_headers_path = self._luna_home_path + '/include'
        luna_src_sources_path = self._luna_home_path + '/src/rts'

        # Include luna src headers
        os_command = f'{self._mpi_compiler} {mpi_prog_cpp} {ucodes_cpp} -I {luna_src_headers_path} '

        # Including luna src dependencies
        luna_source_dependencies = {'df.cpp', 'common.cpp', 'serializable.cpp'}
        for dependency in luna_source_dependencies:
            os_command += f'{luna_src_sources_path}/{dependency} '

        # Specify output name
        os_command += f'-o {output_name}'

        # Compile mpi program
        logging.info(f'Compiling MPI program >>> {os_command}')
        err_code = os.system(os_command)
        if err_code != 0:
            raise OsCommandExecutionException('Error while compiling MPI program')
