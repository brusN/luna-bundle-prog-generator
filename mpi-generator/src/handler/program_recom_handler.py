import json

from builder.luna_fragments import *


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

    def _parse_execution_context(self, context):
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
        with open(f'{self._luna_build_dir}/program_recom.ja', 'r') as program_recom_json_file:
            program_recom_json = json.load(program_recom_json_file)

        self._data = LunaFragments()
        self._parse_include_code_fragments(program_recom_json)
        self._parse_execution_context(program_recom_json['main']['body'])

        return self._data
