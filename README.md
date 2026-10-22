# Sistema de Estacionamento

Aplicação desktop para gerenciamento de um estacionamento de pequeno porte, desenvolvida em Python com Tkinter e SQLite. O sistema centraliza o controle de usuários, veículos, vagas, movimentações de entrada e saída, cobrança, histórico, integração externa e exportação de dados.

## Funcionalidades

- Autenticação de usuários ativos.
- Cadastro, consulta, edição e exclusão de veículos quando permitida pela integridade do histórico.
- Cadastro, consulta, edição e exclusão de vagas quando permitida.
- Registro de entrada com escolha automática de vaga compatível.
- Regras distintas para carros, motos e atendimento PCD.
- Registro de saída com cálculo de permanência.
- Histórico de movimentações abertas e encerradas.
- Gerenciamento de usuários, incluindo ativação e desativação.
- Importação de marcas de carros e motos pela BrasilAPI/FIPE.
- Consulta e filtros para os dados importados.
- Exportação dos dados operacionais para JSON e compactação em ZIP.

## Arquitetura

O projeto usa uma separação simples de responsabilidades:

```text
UI → Services → Repositories → SQLite
```

- **UI:** telas Tkinter, coleta dados do usuário e apresenta resultados.
- **Services:** concentra regras de negócio, autenticação, importação e exportação.
- **Repositories:** executam consultas parametrizadas e operações de persistência.
- **SQLite:** armazena os dados da aplicação localmente.

## Estrutura do projeto

```text
projeto/
├── database/
│   ├── repositories/
│   ├── criar_usuario.py
│   ├── init_db.py
│   └── passwords.py
├── docs/
├── services/
├── tests/
├── ui/
├── main.py
└── README.md
```

## Banco de dados

As entidades principais são:

- `usuario`: funcionários autorizados a acessar o sistema.
- `veiculo`: carros e motos cadastrados.
- `vaga`: vagas numeradas dos tipos CARRO, MOTO ou PCD.
- `movimentacao`: registros de entrada e saída, incluindo responsáveis, horários, indicação PCD e valor.

Uma movimentação pertence a um veículo e a uma vaga, além de registrar o usuário responsável pela entrada e, quando aplicável, pela saída. As referências históricas são preservadas por chaves estrangeiras com restrição de exclusão.

A tabela `marca_importada` é auxiliar e independente do domínio principal. Ela armazena as marcas obtidas na integração com a BrasilAPI/FIPE.

## Decisões de projeto

### Ocupação derivada

A tabela de vagas não possui um campo `ocupada`. A situação é derivada pela existência de uma movimentação aberta associada à vaga, evitando duas fontes de verdade para o mesmo estado.

### Histórico preservado

Uma saída encerra a movimentação com horário, responsável e valor. O registro de entrada não é removido, o que mantém o histórico consultável.

### Usuários e referências históricas

Usuários podem ser ativados ou desativados sem exclusão física. Essa abordagem preserva referências a movimentações registradas no passado.

### Segurança de senha

As senhas são armazenadas com PBKDF2-HMAC-SHA256, salt aleatório e múltiplas iterações. A comparação utiliza comparação segura. Hashes de senha também são omitidos dos arquivos JSON exportados.

## Regras principais do estacionamento

- Moto utiliza somente vaga do tipo MOTO.
- Carro comum utiliza somente vaga do tipo CARRO.
- Carro comum não recebe vaga PCD automaticamente.
- Carro PCD prioriza uma vaga PCD e pode utilizar vaga CARRO caso não exista vaga PCD disponível.
- Uma mesma placa não pode possuir duas movimentações abertas.
- Sem vaga compatível disponível, a entrada não é registrada.

## Cobrança

A tarifa é de R$ 10,00 por hora para carros e motos. Qualquer fração de hora é arredondada para a próxima hora inteira, com cobrança mínima de uma hora.

Exemplos:

- Até 1 hora: R$ 10,00.
- 1h01 até 2 horas: R$ 20,00.
- 2h01 até 3 horas: R$ 30,00.

## Integração externa

O sistema consulta marcas de veículos da BrasilAPI/FIPE por meio de `urllib.request`.

```text
BrasilAPI → HTTP → JSON → Service → Repository → SQLite → UI
```

Endpoint utilizado:

```text
https://brasilapi.com.br/api/fipe/marcas/v1/{vehicleType}
```

São importadas somente marcas dos tipos `carros` e `motos`.

## Exportação

O fluxo de exportação é:

```text
SQLite → aplicação → JSON → ZIP
```

As tabelas `usuario`, `veiculo`, `vaga`, `movimentacao` e `marca_importada` são incluídas na exportação. Dados de usuário são exportados sem hashes de senha. Os arquivos são gerados em `exports/`, diretório criado automaticamente e ignorado pelo Git.

## Tecnologias

- Python 3
- Tkinter
- SQLite
- urllib
- JSON
- ZIP (`zipfile`)
- unittest
- Git

## Como executar

O projeto utiliza apenas recursos da biblioteca padrão do Python. Após clonar o repositório, crie o primeiro usuário de forma interativa:

```bash
python3 -m database.criar_usuario
```

Em seguida, inicie a aplicação:

```bash
python3 main.py
```

O banco SQLite é criado automaticamente em `data/estacionamento.db` quando necessário. Não há senha padrão.

## Testes

Execute a suíte automatizada com:

```bash
python3 -m unittest discover -s tests -v
```

Estado atual: 52 testes automatizados aprovados.

Também é possível verificar isoladamente o esquema SQLite:

```bash
python3 -m database.verificar_db
```

## Screenshots

Ainda não há screenshots versionados. Para uma demonstração visual futura, as telas de Login, Menu principal, Entrada de veículo, Histórico e Dados importados são boas candidatas.

## Contexto

O projeto surgiu na disciplina de Tópicos Especiais em Informática e evoluiu como uma aplicação completa para compor portfólio.

## Autor

Leonardo Canio Della Torre
