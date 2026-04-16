# Guia para agentes de IA

Este documento fornece diretrizes para agentes automatizados (como o Codex ou agentes internos) interagirem com o repositório **Asimov** de forma segura e eficiente.  
O objetivo é facilitar a colaboração entre humanos e máquinas, mantendo a consistência e a qualidade do código.

## Princípios gerais

1. **Não modifique dados em `data/` que sejam gerados em tempo de execução.**  
   Utilize o diretório apenas para leitura de artefatos estáticos (`tools_catalog.json`) ou gravação de novos logs/históricos, respeitando as exclusões definidas no `.gitignore`.
2. **Mantenha a estrutura do projeto.**  
   Crie novas funcionalidades em diretórios apropriados: `tools/` para ferramentas, `services/` para lógica de negócio, `ui/` para componentes gráficos e `utils/` para utilidades.
3. **Documente as mudanças.**  
   Sempre que criar uma nova ferramenta ou serviço, escreva um comentário explicativo e adicione documentação no README se necessário.
4. **Escreva testes.**  
   Para cada nova funcionalidade, crie um teste correspondente em `tests/` para garantir o correto funcionamento e evitar regressões.
5. **Evite dependências excessivas.**  
   Antes de adicionar um novo pacote ao `requirements.txt`, verifique se a funcionalidade pode ser implementada com bibliotecas já existentes ou com módulos da biblioteca padrão.
6. **Consistência de estilo.**  
   Siga as convenções de código Python (PEP 8) e utilize nomes descritivos para variáveis, funções e classes.

## Cadastro de novas ferramentas

Ao criar uma nova ferramenta:

1. Crie um arquivo dentro de `tools/` com o nome e a implementação da ferramenta.  
   Por exemplo, `meu_tool.py`.
2. Adicione a ferramenta ao arquivo `tools/catalog.py` para que ela seja reconhecida pelo assistente.
3. Escreva testes unitários em `tests/` que cubram o uso esperado e casos de falha.
4. Atualize o `README.md` se a ferramenta impactar no uso geral do programa.

## Logs e histórico

Use o módulo `logger.py` para registrar mensagens de depuração, aviso e erro.  
Os logs são gravados em tempo de execução e não devem ser versionados.  
Históricos de conversa ou de ferramentas são salvos em `data/` e são ignorados pelo Git através do `.gitignore`.

## Segurança e privacidade

Não compartilhe dados sensíveis ou pessoais nos arquivos versionados.  
Antes de commitar, verifique se não há credenciais, conversas ou informações pessoais em arquivos JSON ou logs.

## Atualização de dependências

Ao atualizar bibliotecas no `requirements.txt`, teste a aplicação completa para garantir que não haja incompatibilidades.  
Documente quaisquer mudanças de breaking changes no `README.md`.