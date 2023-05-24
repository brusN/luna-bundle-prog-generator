import json
import logging

from exception.custom_exceptions import NoIteratorInContextException
from handler.luna_fragments import DataFragment, CalculationFragment
from util.luna_fragments_parsers import CalculationFragmentHandler, CodeFragmentHandler
from util.ref_expr_parsers import LunaExpressionParser
from exception.custom_exceptions import CfNotFoundException, MultiplyCfDescriptorsException, DfNotFoundException


# Stores parsed fragments from program_recom.ja file
class LunaFragments:
    def __init__(self):
        self.data_fragments = dict()
        self.code_fragments = dict()
        self.calculation_fragments = []

    def register_new_code_fragment(self, code_fragment):
        self.code_fragments[code_fragment.name] = code_fragment

    def register_new_df(self, data_fragment):
        self.data_fragments[data_fragment.name] = data_fragment

    def register_new_df_ref(self, df_name, ref):
        df = self.data_fragments[df_name]
        if ref not in df.refs:
            df.refs.append(ref)

    def check_if_df_exists(self, df_name):
        return df_name in self.data_fragments

    def get_cf(self, cf_name):
        filtered_list = []
        for it in self.calculation_fragments:
            if it.name == cf_name[0] and it.ref == cf_name[1:]:
                filtered_list.append(it)
        if len(filtered_list) == 0:
            raise CfNotFoundException(f'No found descriptor for cf {cf_name[0]}')
        if len(filtered_list) > 1:
            raise MultiplyCfDescriptorsException(f'Cf {cf_name} or his ref has multiply descriptors')
        return filtered_list[0]

    def get_df(self, df_name):
        if df_name not in self.data_fragments:
            raise DfNotFoundException(f'No df with name {df_name}')
        return self.data_fragments[df_name]


class ValueIteratorDescriptor:
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

    def reset_cur_values(self):
        for iter in self.iterators:
            self.iterators[iter].cur_value = self.iterators[iter].start_value

    def get_cur_iter_values(self):
        cur_values = []
        for iter in self.iterators:
            cur_values.append(ValueIteratorDescriptor(self.iterators[iter].name, self.iterators[iter].cur_value))
        return cur_values

    def get_start_iter_values(self):
        start_values = []
        for iter in self.iterators:
            start_values.append(ValueIteratorDescriptor(self.iterators[iter].name, self.iterators[iter].start_value))
        return start_values

    def update_cur_iter_values(self, cur_iter_values):
        for cur_iter_value in cur_iter_values:
            self.iterators[cur_iter_value.name].cur_value = cur_iter_value.value

    def get_cartesian_size(self):
        size = 1
        for iter in self.iterators:
            size *= self.iterators[iter].end_value - self.iterators[iter].start_value + 1
        return size

    def inc_cur_iter_values(self, cur_iter_values):
        cur_iter_values[-1].value += 1
        for i in reversed(range(len(cur_iter_values))):
            if cur_iter_values[i].value > self.iterators[cur_iter_values[i].name].end_value:
                cur_iter_values[i].value = self.iterators[cur_iter_values[i].name].start_value
                if i != 0:
                    cur_iter_values[i - 1].value += 1
                else:
                    break

    def is_contains_iterator(self, it_name):
        return it_name in self.iterators

    def get_iterator_cur_value(self, it_name):
        if not self.is_contains_iterator(it_name):
            raise NoIteratorInContextException("Context doesn't contain iterator " + it_name)
        return self.iterators[it_name].cur_value

class ProgramRecomHandler:
    def __init__(self, luna_build_dir):
        self._data = None
        self._luna_build_dir = luna_build_dir

    def _parse_data_fragment(self, block):
        for name in block['names']:
            data_fragment = DataFragment(name, [])
            self._data.register_new_df(data_fragment)

    def _register_ref_if_not(self, var_cf_arg):
        self._data.register_new_df_ref(var_cf_arg.name, var_cf_arg.ref)

    def _parse_calc_fragment(self, cf_json_block, iterator_context):
        # Creating cf's for each for-block iteration with current iterator values
        iter_values = iterator_context.get_start_iter_values()

        cartesian_size = iterator_context.get_cartesian_size()
        for i in range(cartesian_size):
            iterator_context.update_cur_iter_values(iter_values)
            cf_name = cf_json_block['id'][0]
            cf_ref = CalculationFragmentHandler.build_cf_ref(cf_json_block, iterator_context)
            cf_args = CalculationFragmentHandler.build_cf_args(cf_json_block, iterator_context, self._data)
            cf = CalculationFragment(cf_name, cf_ref, cf_json_block['code'], cf_args)
            self._data.calculation_fragments.append(cf)
            if cartesian_size > 1:
                iterator_context.inc_cur_iter_values(iter_values)
        iterator_context.reset_cur_values()

    def _parse_for_block(self, block, iterator_context):
        start_value = LunaExpressionParser.get_unwrapped_value(block['first'], iterator_context)
        end_value = LunaExpressionParser.get_unwrapped_value(block['last'], iterator_context)
        it_desc = IteratorDescriptor(block['var'], start_value, end_value)
        iterator_context.add_iterator(it_desc)
        self._parse_execution_context(block['body'], iterator_context)
        iterator_context.remove_iterator(it_desc.name)

    def _parse_execution_context(self, context, iterator_context):
        for block in context:
            match block['type']:
                case 'dfs':
                    self._parse_data_fragment(block)
                case 'exec':
                    self._parse_calc_fragment(block, iterator_context)
                case 'for':
                    self._parse_for_block(block, iterator_context)

    def _parse_include_code_fragments(self, program_recom_json):
        for block_name in program_recom_json:
            block_json = program_recom_json[block_name]
            if block_json['type'] == 'extern':
                code_fragment = CodeFragmentHandler.parse_code_fragment_from_json_struct(block_name, block_json)
                self._data.register_new_code_fragment(code_fragment)

    def parse_program_recom_json(self):
        logging.debug('Parsing luna fragments from program_recom.ja')

        with open(f'{self._luna_build_dir}/program_recom.ja', 'r') as program_recom_json_file:
            program_recom_json = json.load(program_recom_json_file)

        self._data = LunaFragments()
        self._parse_include_code_fragments(program_recom_json)
        self._parse_execution_context(program_recom_json['main']['body'], IteratorContext())

        return self._data
