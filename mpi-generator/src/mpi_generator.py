from builder.mpi_program_compiler import MPIProgramCompiler
from config.build_config_parser import *
from builder.mpi_program_builder import *

logging.basicConfig(level=logging.DEBUG, format='luna-mpi-generator: [%(levelname)-s]\t%(message)-s')


def main():
    try:
        logging.debug('Parsing arguments')
        build_config = BuildConfigParser.get_build_config()
    except (PropertyNotDefinedError, FileExistsError) as e:
        logging.error(e)
        logging.info('Launch with option -h/--help')
        exit(1)

    mpi_builder = MPIProgramBuilder(build_config=build_config)
    mpi_builder.build()

    if not build_config.buildOnly:
        mpi_program_compiler = MPIProgramCompiler()
        mpi_program_compiler.compile(build_config.output, build_config.cpp_codes_path, 'compiled_mpi_prog')


if __name__ == '__main__':
    main()
