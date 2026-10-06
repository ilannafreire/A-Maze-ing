"""Exceptions shared by maze generation components."""


class MazeGenerationError(ValueError):
    """Raised when a maze cannot satisfy its requested constraints."""


# Dani, não sei se vale a pena criar mais exceções específicas para cada tipo
# de erro de geração de labirinto. Por enquanto, uma exceção genérica parece
# suficiente.
# Precisa ter um erro caso a configuração do labirinto seja impossível de
# satisfazer no terminal?
# Nome e configuração dos arquivos.
# Caso o terminal esteja muito pequeno para exibir o labirinto, talvez seja
# necessário lançar um erro avisando ao usuário pra aumentar a tela.
# Menu de cores: deixa ou pra usuário escolher ou assim que apertar o 3 o
# labirinto e o cursor mudam de cor automaticamente?

__all__ = ["MazeGenerationError"]
