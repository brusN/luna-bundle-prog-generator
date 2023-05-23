# ------ Luna bundle execution subblocks ------
class ILunaFragment:

    def to_cpp_src(self):
        pass


class CodeFragment(ILunaFragment):

    def __init__(self, name, code, args):
        self.name = name
        self.code = code
        self.args = args

    def to_cpp_src(self):
        return f'void {self.code}();'


class CalculationFragment(ILunaFragment):
    def __init__(self, name, ref, code, args):
        self.name = name
        self.ref = ref
        self.code = code
        self.args = args


class DataFragment(ILunaFragment):
    def __init__(self, name, ref):
        self.name = name
        self.refs = ref

    def to_cpp_src(self):
        return f'DF {self.name};'


# ------ Cf's args descriptor classes ------

class FunctionParameterDescriptor:
    type: str
    name: str

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def to_str(self):
        return f'{self.type} {self.name}'


class CalculationFragmentArgument:
    def to_str(self):
        pass


class IConstCFArgument(CalculationFragmentArgument):

    def __init__(self, value):
        self.value = value
        self.type = 'iconst'

    def to_str(self):
        return str(self.value)


class RConstCFArgument(CalculationFragmentArgument):

    def __init__(self, value):
        self.value = value
        self.type = 'rconst'

    def to_str(self):
        return str(self.value)


class SConstCFArgument(CalculationFragmentArgument):

    def __init__(self, value):
        self.value = value
        self.type = 'sconst'

    def to_str(self):
        return str(self.value)


class VarCFArgument(CalculationFragmentArgument):
    def __init__(self, name, ref):
        self.name = name
        self.ref = ref
        self.type = 'var'

    def to_str(self):
        result = self.name
        for ref_part in self.ref:
            result += f'[{ref_part}]'
        return result
