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
    name: str
    code: str
    args: list

    def __init__(self, name, code):
        self.name = name
        self.code = code
        self.args = []


class DataFragment(ILunaFragment):
    name: str

    def __init__(self, name):
        self.name = name

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

    def to_str(self):
        return str(self.value)


class VarCFArgument(CalculationFragmentArgument):
    def __init__(self, name):
        self.name = name

    def to_str(self):
        return self.name
