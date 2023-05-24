class OsCommandExecutionException(Exception):
    pass


class SyntaxErrorException(Exception):
    pass


class ExpressionParseException(Exception):
    pass


class NoIteratorInContextException(Exception):
    pass


class UsingNoDefinedDataFragmentException(Exception):
    pass


class UnknownBundleExpressionTypeException(Exception):
    pass


class CfNotFoundException(Exception):
    pass


class MultiplyCfDescriptorsException(Exception):
    pass


class DfNotFoundException(Exception):
    pass
