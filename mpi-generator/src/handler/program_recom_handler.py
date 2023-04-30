from builder.luna_fragments import *


class ProgramRecomHandler:
    def parse_execution_context(self, context):
        for block in context:
            if block['type'] == 'exec':
                fragment = CalculationFragment(block['id'][0], block['code'])  # <<<<<
                cf_args = block['args']
                for arg in cf_args:
                    if arg['type'] == 'iconst':
                        fragment.args.append(ConstCFArgument(arg['value']))
                    elif arg['type'] == 'id':
                        fragment.args.append(VarCFArgument(arg['ref'][0]))
                self._data.calculation_fragments[fragment.name] = fragment
            elif block['type'] == 'df':
                self._data.calculation_fragments

    def parse_include_code_fragments(self, program_recom_json):
        for block_name in program_recom_json:
            raw = program_recom_json[block_name]
            if raw['type'] == 'extern':
                code_fragment = CodeFragment()
                code_fragment.name = block_name
                code_fragment.code = raw['code']

                arg_index = 0
                for arg in raw['args']:
                    func_arg = FunctionArgumentDescriptor()
                    func_arg.type = self._args_type_mapper.get_mapped_type(arg['type'])
                    func_arg.name = 'arg' + str(arg_index)
                    code_fragment.args.append(func_arg)
                    arg_index += 1

                self._data.code_fragments[code_fragment.name] = code_fragment