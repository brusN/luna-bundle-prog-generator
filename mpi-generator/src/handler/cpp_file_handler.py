class CPPFileHandler:
    def __init__(self, fileName):
        self._file = open(fileName, 'w+')

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
            args += arg.to_string() + ', '
        args = args[:-2]
        self._file.write(f'extern "C" void {code_fragment.code}({args});')
        self.write_empty_line()

    def include_define_df(self, df_name):
        self.write_line(f'DF {df_name};')

    def include_cf_execution(self, calculation_fragment, code_fragment, rank):
        args = ''
        for arg in calculation_fragment.args:
            args += arg.toStr() + ', '
        args = args[:-2]
        self.write_line(f'if (rank == {rank}) {{ {code_fragment.code}({args});}}')

    def include_df_send(self, df_name, from_rank, to_rank):
        self.write_line(f'\
        if (rank == {from_rank}) {{ \
            void * {df_name}_buff = malloc({df_name}.get_serialization_size()); \
            {df_name}.serialize({df_name}_buff, {df_name}.get_serialization_size()); \
            MPI_Send({df_name}_buff, {df_name}.get_serialization_size(), MPI_BYTE, 1, {from_rank}, MPI_COMM_WORLD); \
            free({df_name}_buff); \
        }} else if (rank == {to_rank}) {{ \
            MPI_Status status; \
            MPI_Probe(0, 0, MPI_COMM_WORLD, &status); \
            int serializationSize; \
            MPI_Get_count(&status, MPI_BYTE, &serializationSize); \
            void * buff = malloc(x.get_serialization_size()); \
            MPI_Recv(buff, serializationSize, MPI_BYTE, 0, {from_rank}, MPI_COMM_WORLD, MPI_STATUS_IGNORE); \
            x.deserialize(buff, serializationSize); \
            free(buff); \
        }}')

    def finalize(self):
        self._file.close()

    def __del__(self):
        self._file.close()
