# Regras de Negócio — Sistema de Estacionamento

## Objetivo

Documentar as regras de negócio do sistema de estacionamento de pequeno porte, que será desenvolvido em Python e utilizado por seus funcionários.

## Escopo

O sistema controlará o acesso dos funcionários, o cadastro dos veículos, a ocupação das vagas numeradas e as movimentações de entrada e saída, incluindo o cálculo do valor da permanência.

Serão atendidos carros e motos, com algumas vagas reservadas para atendimento PCD.

## Regras de acesso

- **RN01.** Os funcionários devem acessar o sistema por meio de login com nome de usuário e senha.

## Regras de veículos

- **RN02.** Cada veículo deve possuir placa, modelo, cor e tipo.
- **RN03.** Os tipos de veículo aceitos são `CARRO` e `MOTO`.
- **RN04.** O sistema não deve armazenar dados pessoais dos motoristas.

## Regras de vagas

- **RN05.** As vagas devem ser numeradas.
- **RN06.** Cada vaga deve possuir um tipo: `CARRO`, `MOTO` ou `PCD`.
- **RN07.** Uma vaga pode estar livre ou ocupada.
- **RN08.** Motos só podem ocupar vagas do tipo `MOTO`.
- **RN09.** Carros comuns só podem ocupar vagas do tipo `CARRO` e não podem ocupar vagas do tipo `PCD`.
- **RN10.** Para fins do escopo deste projeto, o atendimento PCD será considerado apenas para carros.
- **RN11.** Uma vaga do tipo `PCD` nunca deve ser atribuída automaticamente a um carro comum.

## Regras de entrada

- **RN12.** Ao registrar a entrada de um veículo, o sistema deve atribuir automaticamente uma vaga livre compatível com sua categoria.
- **RN13.** Quando um carro com necessidade de vaga PCD entrar no estacionamento, o sistema deve procurar primeiro uma vaga do tipo `PCD` disponível.
- **RN14.** Caso todas as vagas do tipo `PCD` estejam ocupadas, um carro com necessidade de atendimento PCD poderá ocupar uma vaga convencional do tipo `CARRO`.
- **RN15.** Se não existir uma vaga compatível disponível, a entrada não deve ser registrada e o sistema deve informar que não há vaga disponível para aquela categoria.
- **RN16.** Cada entrada registrada deve conter o veículo, a vaga utilizada, a data e o horário de entrada e, quando aplicável, a indicação de atendimento PCD.
- **RN17.** Um veículo não pode possuir mais de uma movimentação aberta simultaneamente. Se já existir uma movimentação sem registro de saída para o veículo, o sistema deve impedir uma nova entrada e informar que o veículo já está estacionado.

## Regras de saída e cobrança

- **RN18.** Ao registrar a saída, o sistema deve armazenar a data e o horário de saída, calcular o valor da permanência, encerrar a movimentação e liberar a vaga utilizada.
- **RN19.** A tarifa é de R$ 10,00 por hora para carros e motos, com o mesmo preço para todos os tipos de veículo.
- **RN20.** Qualquer fração de hora deve ser arredondada para a próxima hora inteira para fins de cobrança.
- **RN21.** Exemplos de cobrança:
  - permanência de até 1 hora: R$ 10,00;
  - permanência superior a 1 hora e de até 2 horas: R$ 20,00;
  - permanência superior a 2 horas e de até 3 horas: R$ 30,00.
- **RN22.** O tempo de permanência não precisa ser armazenado diretamente, pois pode ser calculado pela diferença entre os horários de saída e de entrada.
- **RN24.** O horário de saída deve ser posterior ao horário de entrada. Caso o horário de saída seja igual ou anterior ao horário de entrada, a operação deve ser rejeitada e nenhuma alteração deve ser persistida.

## Histórico de movimentações

- **RN23.** O sistema deve manter o histórico das movimentações. Registrar a saída de um veículo não deve apagar o registro de sua entrada.

## Fora do escopo

Não fazem parte do escopo desta versão do sistema:

- cadastro de motoristas;
- armazenamento de dados pessoais de clientes;
- mensalistas;
- reservas antecipadas de vagas;
- preços diferentes por tipo de veículo;
- pagamento eletrônico;
- múltiplos estacionamentos.
