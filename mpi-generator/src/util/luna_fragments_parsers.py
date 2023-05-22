from handler.luna_fragments import CodeFragment, FunctionParameterDescriptor
from handler.program_recom_handler import ArgTypeMapper
from exception.custom_exceptions import UsingNoDefinedDataFragmentException
from handler.luna_fragments import IConstCFArgument, RConstCFArgument, SConstCFArgument, VarCFArgument
from util.ref_expr_parsers import LunaExpressionParser


class CodeFragmentHandler:

    @classmethod
    def _parse_code_fragment_parameters(cls, raw_json_parameters):
        parameters = []
        param_index = 0
        for raw_param in raw_json_parameters:
            param = FunctionParameterDescriptor()
            param.type = ArgTypeMapper.get_mapped_type(raw_param['type'])
            param.name = 'arg' + str(param_index)
            parameters.append(param)
            param_index += 1
        return parameters

    @classmethod
    def parse_code_fragment_from_json_struct(cls, block_name, block_json):
        code_fragment = CodeFragment()
        code_fragment.name = block_name
        code_fragment.code = block_json['code']
        code_fragment.args = cls._parse_code_fragment_parameters(block_json['args'])


class DataFragmentHandler:
    @classmethod
    def build_df_ref(cls, df_json_block, iterator_context):
        df_ref = []
        for cf_ref_part_expr in df_json_block['id'][1:]:
            df_ref.append(LunaExpressionParser.get_unwrapped_value(cf_ref_part_expr, iterator_context))
        return df_ref


class CalculationFragmentHandler:
    @classmethod
    def build_cf_ref(cls, cf_json_block, iterator_context):
        cf_ref = []
        for cf_ref_part_expr in cf_json_block['id'][1:]:
            cf_ref.append(LunaExpressionParser.get_unwrapped_value(cf_ref_part_expr, iterator_context))
        return cf_ref

    @classmethod
    def build_cf_args(cls, cf_block_json, iterator_context, luna_fragments):
        # Parsing cf args descriptors
        args = []
        for arg in cf_block_json['args']:
            match arg['type']:
                case 'iconst':
                    args.append(IConstCFArgument(arg['value']))
                case 'rconst':
                    args.append(RConstCFArgument(arg['value']))
                case 'sconst':
                    args.append(SConstCFArgument(arg['value']))
                case 'id':
                    possible_iter_name = arg['ref'][0]
                    if iterator_context.is_contains_iterator(possible_iter_name):
                        args.append(IConstCFArgument(iterator_context.get_iterator_cur_value(possible_iter_name)))
                    else:
                        df_name = arg['ref'][0]
                        df_ref = DataFragmentHandler.build_df_ref(arg, iterator_context)
                        args.append(VarCFArgument(df_name, df_ref))

                        # Check if df exists and add new ref, if it isn't added yet
                        if luna_fragments.check_if_df_exists(df_name):
                            luna_fragments.register_new_df_ref(df_name, df_ref)
                        else:
                            raise UsingNoDefinedDataFragmentException(f'DF {df_name} not registered')
        return args
