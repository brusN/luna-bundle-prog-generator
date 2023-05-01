import argparse
import json
import os


class PropertyNotDefinedError(RuntimeError):
    pass


class BuildConfig:
    bundle_file_path: str
    luna_src_path: str
    cpp_codes_path: str
    mpi_header: str
    output: str
    compile_only: bool


class BuildConfigParser:
    @classmethod
    def __get_configured_parser(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument('--config-file',
                            dest='config_file_path', type=str, help='Config to config JSON file', default=None)
        parser.add_argument('--bundle-file',
                            dest='bundle_file_path', type=str, help='Path to bundle file', default=None)
        parser.add_argument('--luna-src',
                            dest='luna_src_path', type=str, help='Path to LuNA program src file', default=None)
        parser.add_argument('--cpp-codes',
                            dest='cpp_codes_path', type=str, help='Path to .cpp file with code blocks', default=None)
        parser.add_argument('--mpi-header',
                            type=str, help='Including MPI header', default='mpi.h')
        parser.add_argument('-o', '--output',
                            dest='output', type=str, help='Path to built binary', default='luna_manual_mpi_program')
        parser.add_argument('--buildOnly', action='store_true',
                            help='Just generate MPI src and bundle JSON internal state')
        return parser

    @classmethod
    def __get_build_config_from_args(cls, args, build_config):
        # Checking required parameters define
        if args.bundle_file_path is None:
            raise PropertyNotDefinedError('Bundle file not defined')
        if args.luna_src_path is None:
            raise PropertyNotDefinedError('Luna src not defined')
        if args.cpp_codes_path is None:
            raise PropertyNotDefinedError('C++ code block file not defined')

        build_config.bundle_file_path = args.bundle_file_path
        build_config.luna_src_path = args.luna_src_path
        build_config.cpp_codes_path = args.cpp_codes_path
        build_config.mpi_header = args.mpi_header
        build_config.output = args.output
        build_config.buildOnly = args.buildOnly

        return build_config

    @classmethod
    def __get_build_config_from_file(cls, file, build_config):
        # Checking required parameters define
        parsed_config_file = json.load(file)
        if "bundle_file_path" not in parsed_config_file:
            raise PropertyNotDefinedError('Bundle file not defined')
        if "luna_src_path" not in parsed_config_file:
            raise PropertyNotDefinedError('Luna src file not defined')
        if "cpp_codes_path" not in parsed_config_file:
            raise PropertyNotDefinedError('File with C++ code block file not defined')

        build_config.bundle_file_path = parsed_config_file["bundle_file_path"]
        build_config.luna_src_path = parsed_config_file["luna_src_path"]
        build_config.cpp_codes_path = parsed_config_file["cpp_codes_path"]

        # Setting the default value for mpi_header
        if "mpi_header" not in parsed_config_file:
            build_config.mpi_header = 'mpi.h'
        else:
            build_config.mpi_header = parsed_config_file["mpi_header"]

        # Setting the default value for output
        if "output" not in parsed_config_file:
            build_config.output = './mpi_prog'
        else:
            build_config.output = parsed_config_file["output"]

        # Setting the default value for compile flag
        if "buildOnly" not in parsed_config_file:
            build_config.buildOnly = True
        else:
            build_config.buildOnly = parsed_config_file["buildOnly"] in ['True', 'true']

        return build_config

    @classmethod
    def get_build_config(cls):
        parser = cls.__get_configured_parser()
        args = parser.parse_args()
        build_config = BuildConfig()

        # If file not specified, then reading from passed args
        if args.config_file_path is None:
            return cls.__get_build_config_from_args(args, build_config)
        # Reading the config from the specified file
        else:
            if not os.path.isfile(args.config_file_path):
                raise FileExistsError('Config file not found! Check passed config file path')
            config_json_file = open(args.config_file_path, 'r')
            parsed_config = cls.__get_build_config_from_file(config_json_file, build_config)
            config_json_file.close()
            return parsed_config
