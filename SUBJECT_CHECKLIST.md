# Auditoria do subject A-Maze-ing

Auditoria do `amazeing.pdf` (versao 2.2) contra o estado atual do repositorio,
em 2026-10-06. Este documento separa requisitos implementados de itens ainda
necessarios para uma entrega verificavel. Nao substitui a revisao dos autores
nem a avaliacao por colegas.

## Resumo

O fluxo principal, os dois modos de labirinto, a exibicao interativa e o pacote
reutilizavel estao implementados. Na validacao final, `make lint` passou com
flake8 limpo e mypy sem issues nos 15 arquivos; `make test` passou com 16 testes.
O wheel foi reconstruido, instalado em um virtualenv temporario e usado para
gerar um maze. A CLI tambem foi executada com configuracao temporaria, e o
analisador confirmou paredes coerentes, corredores alcancaveis, 28 ciclos,
cantos e centro alcancaveis e nenhum beco sem saida.

## Requisitos comuns

| Requisito | Estado e evidencia |
| --- | --- |
| Python 3.10 ou posterior | Atendido: `pyproject.toml` declara `requires-python = ">=3.10"`. |
| Padrao flake8 | Atendido nesta revisao: `make lint` executou `flake8 .` sem avisos. Foram corrigidos finais de linha, espacos e linhas longas, e declaradas as reexportacoes publicas em `mazegen/generator.py`. |
| Tipagem e mypy | Atendido nesta revisao: mypy executou com as flags obrigatorias e reportou `Success: no issues found in 15 source files`. A variavel que guardava a direcao do movimento foi separada da variavel de reconstrucao do caminho. |
| Tratamento de erros e gestao de recursos | Implementado nos fluxos principais: erros de configuracao, geracao e I/O sao apresentados pela CLI; leitura e escrita usam APIs de arquivo com fechamento gerenciado. Cobrir mais entradas invalidas com testes continua recomendado. |
| Docstrings e anotacoes | Presentes nas APIs e funcoes principais; mypy passou nesta revisao. |
| Makefile | Atendido: existem `install`, `run`, `debug`, `clean`, `lint` e `lint-strict`; `test` e `package` sao alvos adicionais. |
| Testes e `.gitignore` | Atendido: `.gitignore` existe e `make test` passou com 16 testes. `make install` instalou as dependencias, mas retornou erro ao final porque `pyenv rehash` nao tem permissao de escrita em `/opt/pyenv/shims`. |

## Parte obrigatoria

| Requisito | Estado e evidencia |
| --- | --- |
| Execucao `python3 a_maze_ing.py config.txt` e um argumento | Implementado em `a_maze_ing.py`; a CLI rejeita quantidade incorreta de argumentos com mensagem de uso. |
| Configuracao KEY=VALUE, comentarios, seis chaves obrigatorias e config padrao versionada | Implementado; `config.txt` esta presente e inclui seed e algoritmo opcionais. O parser rejeita sintaxe invalida, chaves desconhecidas/repetidas e valores invalidos. |
| Geracao aleatoria reproduzivel por seed | Implementado; os testes comparam duas geracoes com o mesmo algoritmo e seed. |
| Paredes norte/leste/sul/oeste consistentes, limites fechados e conectividade | Implementado pela inicializacao/carving e verificacao de conectividade. O analisador executado em `maze.txt` confirmou coerencia e conectividade dos corredores. |
| Sem areas abertas 3x3 | Implementado na etapa de braiding; ha teste que verifica cada janela 3x3 do maze gerado. |
| Padrao visual 42 | Implementado como celulas fechadas; dimensoes pequenas o omitem com aviso. O renderer e os testes verificam as celulas bloqueadas. |
| `PERFECT=True` sem ciclos | Implementado usando uma arvore geradora; teste verifica numero de arestas e vertices. |
| `PERFECT=False`: conectividade, cantos/centro, multiplos ciclos e poucos becos | Implementado pelo braiding e pela preservacao do centro. A execucao do analisador em `maze.txt` confirmou 29 ciclos independentes e zero becos reais, inclusive o bonus de zero becos. |
| Arquivo hexadecimal, uma celula por digito/coluna, tres linhas de rodape e newline final | Implementado em `mazegen/maze_writer.py`; ha teste do formato, digitos hexadecimais, coordenadas, caminho e newline. |

## Visualizacao e reuso

| Requisito | Estado e evidencia |
| --- | --- |
| Representacao visual legivel com paredes, entrada, saida e caminho | Implementada em terminal ASCII em `display/ascii_view.py`; ha testes de renderer. |
| Regenerar, mostrar/ocultar caminho e mudar cores | Implementado pelo menu numerico em `a_maze_ing.py`. A solucao tambem pode ser animada no terminal interativo. |
| Classe de geracao importavel, parametros customizados e acesso a grid/solucao | Implementado pelo pacote `mazegen` e documentado no README com exemplo de `MazeGenerator`. |
| Artefato pip na raiz e fontes para reconstruir | Atendido nesta validacao: `make package` reconstruiu o wheel; ele foi instalado em `/tmp/amazeing-wheel-check` e `MazeGenerator` foi importado e usado com sucesso. Os metadados agora incluem as instrucoes atuais do README. O wheel rastreado pelo Git aparece modificado e deve ser incluido na proxima submissao. |
| Licenca que permita reuso e distribuicao | Atendido: `LICENSE.md` contem MIT. |

## README e entrega

O README ja tem primeira linha no formato solicitado, descricao, instrucoes,
configuracao, justificativa tecnica do backtracker como padrao, exemplo do
pacote e uma declaracao mais especifica sobre uso de IA. Ainda falta:

- Registrar o planejamento real da equipe e como ele mudou, a retrospectiva
   (o que funcionou e o que melhorar) e as ferramentas realmente usadas.
- Confirmar que a divisao de responsabilidades proposta corresponde ao papel
   e as contribuicoes reais de cada integrante; ajustar se necessario.
- Confirmar com ambos os integrantes que a declaracao de uso de IA descreve
   corretamente as tarefas e partes do projeto.
- Incluir as alteracoes finais no commit/submissao. O wheel esta modificado e
   `SUBJECT_CHECKLIST.md` ainda e um arquivo nao rastreado.

## Verificacoes a concluir

1. Completar o planejamento e a retrospectiva reais no README e confirmar os
   papeis e a declaracao de uso de IA com a equipe.
2. Revisar por colega e preparar-se para explicar os algoritmos, decisoes de
   implementacao e uso de IA durante a avaliacao.
3. Incluir e submeter as alteracoes finais, especialmente o wheel atualizado.

## Bonus e preparacao da avaliacao

Os bonus de multiplos algoritmos e maze nao perfeito sem becos estao presentes.
A animacao implementada mostra o caminho; animar o processo de geracao e um
bonus opcional do subject e nao esta implementado. A avaliacao tambem pode pedir
uma alteracao pequena ao vivo: isso exige preparacao e entendimento dos autores,
nao uma funcionalidade adicional no repositorio.