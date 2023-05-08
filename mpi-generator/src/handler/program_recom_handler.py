import json
import logging

from src.exception.custom_exceptions import SyntaxErrorException
from src.handler.luna_fragments import DataFragment, CalculationFragment, VarCFArgument, ConstCFArgument, CodeFragment, \
    FunctionArgumentDescriptor


# Stores parsed fragments from program_recom.ja file
class LunaFragments:
    def __init__(self):
        self.data_fragments = dict()
        self.code_fragments = dict()
        self.calculation_fragments = []


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


class CurValueIteratorDescriptor:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class IteratorDescriptor:
    def __init__(self, name, start_value, end_value):
        self.name = name
        self.start_value = start_value
        self.end_value = end_value
        self.cur_value = start_value


class IteratorContext:
    def __init__(self):
        self.iterators = dict()

    def add_iterator(self, it_desc):
        self.iterators[it_desc.name] = it_desc

    def remove_iterator(self, it_name):
        del self.iterators[it_name]

    def get_cur_iter_values(self):
        cur_values = []
        for iter in self.iterators:
            cur_values.append(CurValueIteratorDescriptor(self.iterators[iter].name, self.iterators[iter].start_value))
        return cur_values

    def update_cur_iter_values(self, cur_iter_values):
        for cur_iter_value in cur_iter_values:
            self.iterators[cur_iter_value.name].cur_value = cur_iter_value.value

    def get_cartesian_size(self):
        size = 1
        for iter in self.iterators:
            size *= self.iterators[iter].end_value - self.iterators[iter].start_value + 1
        return size


class ProgramRecomHandler:
    def __init__(self, luna_build_dir):
        self._data = None
        self._luna_build_dir = luna_build_dir

    def _register_data_fragment(self, block):
        for name in block['names']:
            data_fragment = DataFragment(name, [])
            self._data.data_fragments[name] = data_fragment

    def _register_ref_if_not(self, var_cf_arg):
        df = self._data.data_fragments[var_cf_arg.name]
        if var_cf_arg.ref not in df.refs:
            df.refs.append(var_cf_arg.ref)

    def _inc_cur_iter_values(self, iterator_context, cur_iter_values):
        cur_iter_values[-1].value += 1
        for i in reversed(range(len(cur_iter_values))):
            if cur_iter_values[i].value > iterator_context.iterators[cur_iter_values[i].name].end_value:
                cur_iter_values[i].value = 0
                if i != 0:
                    cur_iter_values[i - 1].value += 1
                else:
                    break

    def _build_cf_ref(self, block, iterator_context):
        cf_ref = []
        for cf_ref_part in block['id'][1:]:
            # If const, then get his value
            if cf_ref_part['type'] == 'iconst':
                cf_ref.append(cf_ref_part['value'])

            # If iterator, then take his cur value like const
            elif cf_ref_part['type'] == 'id':
                iter_name = cf_ref_part['ref'][0]
                if iter_name not in iterator_context.iterators:
                    raise SyntaxErrorException('Unknown iterator in cf ref')
                cf_ref.append(iterator_context.iterators[iter_name].cur_value)
        return cf_ref

    def _build_cf_args(self, block, iterator_context):
        args = []
        for arg in block['args']:
            if arg['type'] == 'iconst':
                args.append(ConstCFArgument(arg['value']))
            elif arg['type'] == 'id':
                if len(block['args']) == 1:
                    if arg['ref'][0] in iterator_context.iterators:
                        args.append(ConstCFArgument(iterator_context.iterators[arg['ref'][0]].cur_value))
                    else:
                        args.append(VarCFArgument(arg['ref'][0], []))
                else:
                    cf_arg_ref = []
                    for cf_arg_ref_part in arg['ref'][1:]:
                        if cf_arg_ref_part['type'] == 'iconst':
                            cf_arg_ref.append(cf_arg_ref_part['value'])
                        elif cf_arg_ref_part['type'] == 'id':
                            if len(cf_arg_ref_part['ref']) > 1:
                                raise SyntaxErrorException('Using inherit ref')
                            cf_arg_ref.append(iterator_context.iterators[cf_arg_ref_part['ref'][0]].cur_value)
                    args.append(VarCFArgument(arg['ref'][0], cf_arg_ref))

                    # Check if df exists
                    df_name = arg['ref'][0]
                    if df_name not in self._data.data_fragments:
                        raise SyntaxErrorException('Using no defined df ref')
                    if cf_arg_ref not in self._data.data_fragments[df_name].refs:
                        self._data.data_fragments[df_name].refs.append(cf_arg_ref)
        return args

    def _register_calc_fragment(self, block, iterator_context):
        cur_iter_values = iterator_context.get_cur_iter_values()
        for i in range(iterator_context.get_cartesian_size()):
            # string = ''
            # for value in cur_iter_values:
            #     string += f'{value.value}, '
            # print(string) <--- for debug
            iterator_context.update_cur_iter_values(cur_iter_values)

            cf = CalculationFragment(block['id'][0], self._build_cf_ref(block, iterator_context), block['code'])
            cf.args = self._build_cf_args(block, iterator_context)
            self._data.calculation_fragments.append(cf)
            self._inc_cur_iter_values(iterator_context, cur_iter_values)

    def _register_for_block(self, block, iterator_context):

        # Adding iterator with start/end values into current for block context
        it_desc = IteratorDescriptor(block['var'], block['first']['value'], block['last']['value'])
        iterator_context.add_iterator(it_desc)

        # Parse for block body
        self._parse_execution_context(block['body'], iterator_context)

        # Remove iterator from context
        iterator_context.remove_iterator(it_desc.name)

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
        self._parse_execution_context(program_recom_json['main']['body'], IteratorContext())

        return self._data
