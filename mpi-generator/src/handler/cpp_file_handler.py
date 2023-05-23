class CPPFileHandler:
    def __init__(self, file_name):
        self._file = open(file_name, 'w+')

    def write_line(self, line):
        self._file.write(f'{line}\n')

    def write_empty_line(self):
        self._file.write('\n')

    def include_user_header(self, header_name):
        self._file.write(f'#include "{header_name}"')

    def include_std_header(self, header_name):
        self._file.write(f'#include <{header_name}>')
        self.write_empty_line()

    def include_extern_void_func(self, code_fragment):
        args = ''
        for arg in code_fragment.args:
            args += arg.to_str() + ', '
        args = args[:-2]
        self._file.write(f'extern "C" void {code_fragment.code}({args});')
        self.write_empty_line()

    def include_define_df(self, df):
        self.write_line(f' \
            dfManager.addNewDF(new DFDescriptor("{df.name}")); \
        ')

        # if len(df.refs) < 1:
        #     return
        #
        # for ref in df.refs:
        #     ref_list = "{ "
        #     for ref_part in ref:
        #         ref_list += f'"{ref_part}", '
        #     ref_list = ref_list[:-2]
        #     ref_list += "}"
        #     self.write_line(f' \
        #         dfManager.addRefToDF("{df.name}", {ref_list}); \
        #     ')

    def include_cf_execution(self, calculation_fragment, code_fragment, rank):
        args = ''
        for arg in calculation_fragment.args:
            match arg.type:
                case 'iconst':
                    args += str(arg.value) + ', '
                case 'rconst':
                    args += str(arg.value) + ', '
                case 'sconst':
                    args += f'\"{arg.value}\", '
                case 'var':
                    cpp_list_define = f'"{arg.name}"'
                    for cf_ref_part in arg.ref:
                        cpp_list_define += f', "{cf_ref_part}"'
                    args += f'*dfManager.getDFByFullName({{ {cpp_list_define} }}), '
        args = args[:-2]
        self.write_line(f'if (rank == {rank}) {{ \
            {code_fragment.code}({args}); \
        }}')

    def include_df_send(self, df_name, from_rank, to_rank):
        cpp_list_define = f'"{df_name[0]}" '
        for df_name_part in df_name[1:]:
            cpp_list_define += f', "{df_name_part}"'
        self.write_line(f' \
            dfManager.sendDfBetweenNodes({{ {cpp_list_define} }}, rank, {from_rank}, {to_rank}); \
        ')

    def finalize(self):
        self._file.close()

    def __del__(self):
        self._file.close()
