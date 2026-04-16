# Asimov

Asimov é um assistente de automação escrito em Python com interface gráfica baseada em **PySide6**.  
Ele fornece ferramentas de busca de arquivos, histórico e integridade do sistema, permitindo que o usuário execute operações de IA de forma integrada.  
Esta versão reorganiza e prepara o projeto para ser utilizado em um repositório GitHub, com arquivos de configuração e dependências explícitas.

## Estrutura do projeto

```
asimov/
├── main.py                # Ponto de entrada da aplicação GUI
├── config.py              # Configurações globais da aplicação
├── logger.py              # Configuração de logging
├── exceptions.py          # Definição de exceções customizadas
├── services/              # Camada de serviços e processamento
├── tools/                 # Conjunto de ferramentas disponíveis (busca, catálogo etc.)
├── ui/                    # Interface gráfica em PySide6
├── utils/                 # Funções auxiliares (armazenamento de contexto, integridade, validação etc.)
├── data/                  # Dados e metadados usados pela aplicação
├── tests/                 # Diretório para testes automatizados
├── requirements.txt       # Dependências Python
├── .gitignore             # Arquivos e diretórios a serem ignorados pelo Git
└── README.md              # Este documento
```

### Pasta `data/`

O diretório `data/` contém dados que a aplicação utiliza e produz.  
Para evitar que informações sensíveis ou arquivos gerados entrem no repositório, logs e históricos são ignorados via `.gitignore`.  
Os subdiretórios são criados vazios para que a estrutura exista, mas os conteúdos são gerados em tempo de execução.

## Instalação

Para executar o projeto localmente é recomendado utilizar um ambiente virtual.  
Siga os passos abaixo:

```bash
# Crie e ative o ambiente virtual (Windows)
python -m venv .venv
.venv\Scripts\activate

# Crie e ative o ambiente virtual (Linux/Mac)
python -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

## Uso

Após instalar as dependências, execute a aplicação com:

```bash
python main.py
```

Isso abrirá a interface gráfica do assistente IA.

## Contribuindo

1. **Fork** o repositório e crie sua branch: `git checkout -b minha-feature`.
2. Faça suas alterações e crie testes quando aplicável.
3. Faça commit das mudanças: `git commit -m 'feat: adiciona nova ferramenta'`.
4. Faça push para a branch: `git push origin minha-feature`.
5. Abra um **Pull Request** no GitHub.

## Diretrizes para agentes / Codex

O repositório inclui uma estrutura bem definida para facilitar a atuação de agentes de IA (como o Codex) no código.  
Algumas recomendações:

* Mantenha a separação entre camadas (`ui`, `services`, `tools`, `utils`); evita-se misturar lógica de negócios com interface.
* Registre logs através do módulo `logger.py` para facilitar diagnóstico.
* Sempre que adicionar uma nova ferramenta em `tools/`, atualize o catálogo de ferramentas e crie testes correspondentes.
* Evite adicionar dependências pesadas sem justificativa; liste qualquer dependência extra no `requirements.txt`.

Para detalhes adicionais sobre como agentes devem interagir com este projeto, consulte o arquivo `AGENTS.md`.