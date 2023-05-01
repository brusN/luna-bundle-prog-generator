import json
import logging

from handler.luna_fragments import *


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

    def _register_calc_fragment(self, block):
        ref = []
        for ref_part in block['id'][1:]:
            ref.append(ref_part)
        calc_fragment = CalculationFragment(block['id'][0], ref, block['code'])
        cf_args = block['args']
        for arg in cf_args:
            if arg['type'] == 'iconst':
                calc_fragment.args.append(ConstCFArgument(arg['value']))
            elif arg['type'] == 'id':
                cf_ref = []
                for cf_ref_part in block['ref'][1:]:
                    cf_ref.append(cf_ref_part)
                var_cf_arg = VarCFArgument(arg['ref'][0], cf_ref)
                self._register_ref_if_not(var_cf_arg)
                calc_fragment.args.append(var_cf_arg)
        self._data.calculation_fragments[calc_fragment.name] = calc_fragment

    def _parse_for_context(self, block):
        pass

    def _parse_execution_context(self, context):
        for block in context:
            block_type = block['type']
            if block_type == 'dfs':
                self._register_data_fragment(block)
            if block_type == 'exec':
                self._register_calc_fragment(block)
            if block_type == 'for':
                self._parse_for_context(block)

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
        self._parse_execution_context(program_recom_json['main']['body'])

        return self._data
