# ------ Luna bundle execution subblocks ------
class ILunaFragment:

    def to_cpp_src(self):
        pass


class CodeFragment(ILunaFragment):
    name: str
    code: str
    args: list

    def __init__(self):
        self.args = []

    def to_cpp_src(self):
        return f'void {self.code}();'


class CalculationFragment(ILunaFragment):
    def __init__(self, name, ref, code):
        self.name = name
        self.ref = ref
        self.code = code
        self.args = []


class DataFragment(ILunaFragment):
    def __init__(self, name, ref):
        self.name = name
        self.refs = []

    def to_cpp_src(self):
        return f'DF {self.name};'


# ------ Cf's args descriptor classes ------

class FunctionArgumentDescriptor:
    type: str
    name: str

    def to_str(self):
        return f'{self.type} {self.name}'


class CalculationFragmentArgument:
    def to_str(self):
        pass


class ConstCFArgument(CalculationFragmentArgument):

    def __init__(self, value):
        self.value = value
        self.type = 'const'

    def to_str(self):
        return str(self.value)


class VarCFArgument(CalculationFragmentArgument):
    type = 'var'

    def __init__(self, name, ref):
        self.name = name
        self.ref = ref
        self.type = 'var'

    def to_str(self):
        result = self.name
        for ref_part in self.ref:
            result += f'[{ref_part}]'
        return result
