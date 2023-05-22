from src.exception.custom_exceptions import UnknownBundleExpressionTypeException


class LunaExpressionParser:
    @classmethod
    def _unwrap_math_operation(cls, left_operand, right_operand, op, iterator_context):
        match op:
            case '+':
                return cls.get_unwrapped_value(left_operand, iterator_context) + cls.get_unwrapped_value(right_operand, iterator_context)
            case '-':
                return cls.get_unwrapped_value(left_operand, iterator_context) - cls.get_unwrapped_value(right_operand, iterator_context)
            case '*':
                return cls.get_unwrapped_value(left_operand, iterator_context) * cls.get_unwrapped_value(right_operand, iterator_context)
            case '/':
                return cls.get_unwrapped_value(left_operand, iterator_context) / cls.get_unwrapped_value(right_operand, iterator_context)

    @classmethod
    def get_unwrapped_value(cls, expr, iterator_context):
        match expr.type:
            case 'iconst':
                return expr.value
            case 'rconst':
                return expr.value
            case 'sconst':
                return expr.value
            case 'id':
                it_name = expr.ref[0]
                return iterator_context.get_iterator_cur_value(it_name)
            case _:
                left_operand_expr = expr.operands[0]
                right_operand_expr = expr.operands[1]
                op = expr.type
                return cls._unwrap_math_operation(left_operand_expr, right_operand_expr, op, iterator_context)


class BundleIntExpressionParser:
    @classmethod
    def _unwrap_math_operation(cls, left_operand, right_operand, op, iterator_context):
        match op:
            case '+':
                return cls.get_unwrapped_value(left_operand, iterator_context) + cls.get_unwrapped_value(right_operand, iterator_context)
            case '-':
                return cls.get_unwrapped_value(left_operand, iterator_context) - cls.get_unwrapped_value(right_operand, iterator_context)
            case '*':
                return cls.get_unwrapped_value(left_operand, iterator_context) * cls.get_unwrapped_value(right_operand, iterator_context)
            case '/':
                return cls.get_unwrapped_value(left_operand, iterator_context) / cls.get_unwrapped_value(right_operand, iterator_context)
            case _:
                raise UnknownBundleExpressionTypeException("Unknown type: " + op)

    @classmethod
    def get_unwrapped_value(cls, expr, iterator_context):
        match expr.type:
            case 'iconst':
                return expr.value
            case 'var':
                it_name = expr.name
                return iterator_context.get_iterator_cur_value(it_name)
            case _:
                left_operand_expr = expr.operands[0]
                right_operand_expr = expr.operands[1]
                op = expr.type
                return cls._unwrap_math_operation(left_operand_expr, right_operand_expr, op, iterator_context)
