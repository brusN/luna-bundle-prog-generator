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

    def include_define_df(self, df_name):
        self.write_line(f' \
            dfManager.addNewDF(new DFDescriptor("{df_name}")); \
        ')

    def include_cf_execution(self, calculation_fragment, code_fragment, rank):
        args = ''
        for arg in calculation_fragment.args:
            if arg.type == 'const':
                args += str(arg.value) + ', '
            elif arg.type == 'var':
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
        temp_ref_name = 'requiredDFForSend'
        self.write_line(f'\
        if (rank == {from_rank}) {{ \
            DF* {temp_ref_name} = dfManager.getDFByFullName({{ {cpp_list_define} }}); \
            void * {temp_ref_name}_buff = malloc({temp_ref_name}->get_serialization_size()); \
            {temp_ref_name}->serialize({temp_ref_name}_buff, {temp_ref_name}->get_serialization_size()); \
            MPI_Send({temp_ref_name}_buff, {temp_ref_name}->get_serialization_size(), MPI_BYTE, 1, {from_rank}, MPI_COMM_WORLD); \
            free({temp_ref_name}_buff); \
        }} else if (rank == {to_rank}) {{ \
            DF* {temp_ref_name} = dfManager.getDFByFullName({{ {cpp_list_define} }}); \
            MPI_Status status; \
            MPI_Probe(0, 0, MPI_COMM_WORLD, &status); \
            int serializationSize; \
            MPI_Get_count(&status, MPI_BYTE, &serializationSize); \
            void * buff = malloc({temp_ref_name}->get_serialization_size()); \
            MPI_Recv(buff, serializationSize, MPI_BYTE, 0, {from_rank}, MPI_COMM_WORLD, MPI_STATUS_IGNORE); \
            {temp_ref_name}->deserialize(buff, serializationSize); \
            free(buff); \
        }}')

    def finalize(self):
        self._file.close()

    def __del__(self):
        self._file.close()
