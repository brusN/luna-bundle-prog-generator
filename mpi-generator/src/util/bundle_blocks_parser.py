from util.ref_expr_parsers import BundleIntExpressionParser


class BundleControlUnitParser:
    @classmethod
    def build_full_df_name(cls, raw_df_name, iterator_context):
        df_base_name = raw_df_name[0]
        df_ref = []
        for raw_df_name_part in raw_df_name[1:]:
            df_ref.append(BundleIntExpressionParser.get_unwrapped_value(raw_df_name_part, iterator_context))
        return [df_base_name] + df_ref

    @classmethod
    def build_full_cf_name(cls, raw_cf_name, iterator_context):
        cf_base_name = raw_cf_name[0]
        cf_ref = []
        for raw_cf_name_part in raw_cf_name[1:]:
            cf_ref.append(BundleIntExpressionParser.get_unwrapped_value(raw_cf_name_part, iterator_context))
        return [cf_base_name] + cf_ref
