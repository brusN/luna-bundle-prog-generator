import json
import logging

from src.handler.luna_fragments import DataFragment, CalculationFragment, VarCFArgument, ConstCFArgument, CodeFragment, \
    FunctionArgumentDescriptor


# Stores parsed fragments from program_recom.ja file
class LunaFragments:
    data_fragments: dict
    code_fragments: dict
    calculation_fragments: dict

    def __init__(self):
        self.data_fragments = {}
        self.code_fragments = {}
        self.calculation_fragments = {}


# Converter LuNA types to C++ types
class ArgTypeMapper:
    types_map = {
        'int': 'int',
        'real': 'double',
        'string': 'string',
        'name': 'DF &',
        'value': 'const DF &'
    }

    @classmethod
    def get_mapped_type(cls, arg_type):
        return cls.types_map[arg_type]


class ProgramRecomHandler:
    def __init__(self, luna_build_dir):
        self._data = None
        self._luna_build_dir = luna_build_dir

    def _register_data_fragment(self, block):
        for name in block['names']:
            data_fragment = DataFragment(name)
            self._data.data_fragments[name] = data_fragment

    def _register_ref_if_not(self, var_cf_arg):
        df = self._data.data_fragments[var_cf_arg.name]
        if var_cf_arg.ref not in df.refs:
            df.refs.append(var_cf_arg.ref)

    def _expand_for(self, cf, cur_iterator_values, iterator_context):
        pass

    def _register_calc_fragment(self, block, iterator_context):
        # Creating calc fragment, creating his ref if he has
        cf_ref = []
        for ref_part in block['id'][1:]:
            if ref_part['type'] == 'iconst':
                cf_ref.append(ref_part['value'])
            elif ref_part['type'] == 'id':
                cf_ref.append(ref_part['ref'][0])
        calc_fragment = CalculationFragment(block['id'][0], cf_ref, block['code'])

        # Handling cf args
        cf_args = block['args']
        for arg in cf_args:

            # Ref part represents const number
            if arg['type'] == 'iconst':
                calc_fragment.args.append(ConstCFArgument(arg['value']))

            # Ref part represents iterator or df with reference
            elif arg['type'] == 'id':

                # Building cf arg reference
                cf_arg_ref = []
                for cf_ref_part in arg['ref'][1:]:

                    # Const reference part, example x[0]
                    if cf_ref_part['type'] == 'iconst':
                        cf_arg_ref.append(cf_ref_part['value'])
                    # Var reference part, example x[i]
                    elif cf_ref_part['type'] == 'id':
                        cf_arg_ref.append(cf_ref_part['ref'][0])

                var_cf_arg = VarCFArgument(arg['ref'][0], cf_arg_ref)

                # Adding cf arg
                calc_fragment.args.append(var_cf_arg)

        # 1. Раскрыть i-ость в конкретные значения
        # 2. Зарегистрировать ссылочные df
        cartesian_set_size = 1
        cur_iter_values = dict()
        for iterator in iterator_context:
            it_descriptor = iterator_context[iterator]
            cur_iter_values[iterator] = it_descriptor[0]
            cartesian_set_size *= it_descriptor[1] - it_descriptor[0] + 1
        for cur_value in range(0, cartesian_set_size):



        # self._data.calculation_fragments[calc_fragment.name] = calc_fragment

    def _register_for_block(self, block, iterator_context):

        # Adding iterator with start/end values into current for block context
        iterator_context[block['var']] = [block['first']['value'], block['last']['value']]

        # Parse for body
        self._parse_execution_context(block['body'], iterator_context)

        # Remove iterator from context
        del iterator_context[block['var']]

    def _parse_execution_context(self, context, iterator_context):
        for block in context:
            block_type = block['type']
            if block_type == 'dfs':
                self._register_data_fragment(block)
            elif block_type == 'exec':
                self._register_calc_fragment(block, iterator_context)
            elif block_type == 'for':
                self._register_for_block(block, iterator_context)

    def _parse_include_code_fragments(self, program_recom_json):
        for block_name in program_recom_json:
            raw = program_recom_json[block_name]
            if raw['type'] == 'extern':
                code_fragment = CodeFragment()
                code_fragment.name = block_name
                code_fragment.code = raw['code']

                # Create args descriptor list
                arg_index = 0
                for arg in raw['args']:
                    func_arg = FunctionArgumentDescriptor()
                    func_arg.type = ArgTypeMapper.get_mapped_type(arg['type'])
                    func_arg.name = 'arg' + str(arg_index)
                    code_fragment.args.append(func_arg)
                    arg_index += 1

                # Register code fragment
                self._data.code_fragments[code_fragment.name] = code_fragment

    def parse_program_recom_json(self):
        logging.debug('Parsing luna fragments from program_recom.ja')

        with open(f'{self._luna_build_dir}/program_recom.ja', 'r') as program_recom_json_file:
            program_recom_json = json.load(program_recom_json_file)

        self._data = LunaFragments()
        self._parse_include_code_fragments(program_recom_json)
        var_context = dict()
        self._parse_execution_context(program_recom_json['main']['body'], var_context)

        return self._data
