from src.handler.luna_fragments import CodeFragment, FunctionParameterDescriptor
from src.handler.program_recom_handler import ArgTypeMapper


class CodeFragmentParser:

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
