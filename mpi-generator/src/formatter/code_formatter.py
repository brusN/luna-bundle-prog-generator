import logging
import os


class ICodeFormatter:
    def format(self, filepath):
        pass


class ClangCPPCodeFormatter(ICodeFormatter):
    clang_format_path = "clang-format"

    def format(self, filepath):
        logging.info("Formatting CPP file: " + filepath)
        if not os.path.exists(filepath):
            raise FileExistsError("File for format not exists!")

        compile_os_command = '{clang_format_path} {filepath}'.format(
            clang_format_path=self.clang_format_path,
            filepath=filepath,
        )

        logging.info('Compiling LuNA program >>> ' + compile_os_command)
        os.system(compile_os_command)
