from src.exception.custom_exceptions import ExpressionParseException


class ExpressionHandler:
    @classmethod
    def get_unwrapped_value(cls, expr, context):
        match expr.type:
            case 'iconst':
                return expr.value
            case 'id':
                if expr.ref[0] in context.iterators:
                    return context.iterators[expr.ref[0]].cur_value
                else:
                    raise ExpressionParseException('No iterator in context for expr')
            case '+':
                cls.get_unwrapped_value(expr.operands[0], context) + cls.get_unwrapped_value(expr.operands[1], context)
            case '-':
                cls.get_unwrapped_value(expr.operands[0], context) - cls.get_unwrapped_value(expr.operands[1], context)
            case '*':
                cls.get_unwrapped_value(expr.operands[0], context) * cls.get_unwrapped_value(expr.operands[1], context)
            case '/':
                cls.get_unwrapped_value(expr.operands[0], context) / cls.get_unwrapped_value(expr.operands[1], context)