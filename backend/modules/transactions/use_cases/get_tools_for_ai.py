from google.genai.types import ToolListUnion


FALLBACK_MESSAGE = "Erro ao executar a função."


def fallback_in_case_of_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return FALLBACK_MESSAGE
    return wrapper


class GetToolsForAIUseCase:
    def __init__(self, tools_use_cases: list):
        self.tools_use_cases = tools_use_cases

    def execute(self) -> list[ToolListUnion]:
        return [fallback_in_case_of_error(tool_use_case().execute) for tool_use_case in self.tools_use_cases]
