from builder.mpi_program_compiler import MPIProgramCompiler
from config.build_config_parser import *
from builder.mpi_program_builder import *

logging.basicConfig(level=logging.DEBUG)


def main():
    logging.info('Parsing arguments')
    try:
        build_config = BuildConfigParser.get_build_config()
    except (PropertyNotDefinedError, FileExistsError) as e:
        logging.error(e)
        logging.info('Launch with option -h/--help')
        exit(1)

    mpi_builder = MPIProgramBuilder(build_config=build_config)
    mpi_builder.compile_luna_prog()
    mpi_builder.get_bundle_json()
    mpi_builder.parse_program_recom_json()
    mpi_builder.generate_mpi_src()
    mpi_builder.finalize()

    mpi_program_compiler = MPIProgramCompiler()
    mpi_program_compiler.compile(build_config.output, build_config.cpp_codes_path, 'compiled_mpi_prog')


if __name__ == '__main__':
    main()
