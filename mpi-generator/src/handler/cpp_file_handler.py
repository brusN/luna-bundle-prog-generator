class CPPFileHandler:
    def __init__(self, fileName):
        self.file = open(fileName, 'w+')

    def write_line(self, line):
        self.file.write(f'{line}\n')

    def write_empty_line(self):
        self.file.write('\n')

    def include_user_header(self, header_name):
        self.file.write(f'#include "{header_name}"')

    def include_std_header(self, header_name):
        self.file.write(f'#include <{header_name}>')
        self.write_empty_line()

    def include_extern_void_func(self, code_fragment):
        args = ''
        for arg in code_fragment.args:
            args += arg.to_string() + ', '
        args = args[:-2]
        self.file.write(f'void {code_fragment.name}({args});')
        self.write_empty_line()

    def include_cf_execution(self, cf, rank):
        args = ''
        for arg in cf.args:
            args += arg.toStr() + ', '
        args = args[:-2]
        self.write_line(f'if (rank == {rank}) {{ {cf.name}({args});}}')

    def __del__(self):
        self.file.close()
