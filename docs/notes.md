# Definições

Os dados de entrada recebidos são ProcessInput(antes eram chamados Process) que serão convertidos em ReadyProcess(antes eram chamados ArrivedProcess) pelo ProcessExecutor(antes era chamado ExecutionState) que irá instanciar o ReadyProcess correto de acordo com o algoritmo utilizado.

### Regras do ProcessInput:

id tem que ser inteiro;
arrival_time tem que ser inteiro;
burst_time tem que ser inteiro > 0;
se houver deadline tem que ser inteiro > 0;
se houver priority tem que ser inteiro;

Essa é uma classe somente de dados, seus estado deve ser imutável.

### Regras do ReadyProcess

Essa classe representa o processo na fila de pronto | em execução, para ser criada recebe um ProcessInput, e em geral suas regras são:

remaining_time começa igual a burst_time, definido por valores inteiros;
completion_time deve ser definido por valores inteiros maiores que arrival_time;
response_time deve ser definido por valores inteiros;
waiting_time deve ser definido por valores inteiros;
turnaround_time deve ser definido por completion_time - arrival_time, logo sempre será > 0;

existem variações específicas de ReadyProcess:

* FairReadyProcess -> CFS;
* DeadlineReadyProcess -> EDF;
* PriorityReadyProcess -> Priority;

### Mudanças

O ReadyProcess não herda mais de ProcessInput, somente recebe como valor de entrada no seu construtor,
em contrapartida o FairReadyProcess, DeadlineReadyProcess, PriorityReadyProcess herdam de ReadyProcess.

Essa decisão foi necessária para separar os contextos específicos, e não ficar tudo misturado em um
único tipo.

### Regras específicas do DeadlineReadyProcess

new_deadline deve ser definido por inteiros, calculado no construtor como process_input.deadline + process_input.arrival_time
deadline_ok deve ser definido por booleanos, inicializado em False por padrão

### Regras específicas do PriorityReadyProcess

priority deve ser definido por inteiro em process_input

### Regras específicas do FairReadyProcess

vruntime: deve ser definido por inteiros

**concluir as regras do FairReadyProcess de acordo com os requisitos do professor**
