# Guia completo de uso do Simulador de Escalonamento

Este documento explica como instalar, executar e configurar o simulador de
escalonamento de processos pelo terminal. Ele também descreve a sintaxe dos
arquivos JSON, os parâmetros da linha de comando, os algoritmos disponíveis,
os resultados exibidos e os arquivos gerados.

Os exemplos deste guia consideram que o terminal está aberto na raiz do
projeto, isto é, no diretório que contém `main.py`, `requirements.txt` e a pasta
`casos`.

---

## 1. O que o programa faz

O simulador reproduz o funcionamento de uma CPU de núcleo único usando
processos descritos em um arquivo JSON.

Ele pode:

- executar um ou todos os algoritmos de escalonamento;
- calcular tempos de espera, resposta, turnaround e uso da CPU;
- indicar processos que estouraram seus deadlines;
- criar um gráfico de Gantt em PNG;
- criar um log textual da linha do tempo;
- repetir uma execução no modo passo a passo;
- comparar os resultados dos algoritmos no modo `ALL`.

O programa não possui interface gráfica própria. A interação principal é feita
pela interface de linha de comando.

---

## 2. Pré-requisitos

É necessário ter instalado:

- Python 3.10 ou superior;
- `pip`, o gerenciador de pacotes do Python;
- uma instalação que consiga executar `python main.py`.

Este projeto depende de:

- `Pillow`, para criar imagens PNG;
- `pytest`, para executar os testes automatizados.

Pillow é necessário para a opção `--gantt`. `pytest` não é necessário para
realizar uma simulação, mas é usado na validação do projeto.

### 2.1. Abrindo o diretório correto no terminal

No PowerShell ou Prompt de Comando do Windows:

```powershell
cd D:\ufba\Simulador-Escalonamento
```

No PowerShell, o nome do diretório atual pode ser confirmado com:

```powershell
Get-Location
```

No Prompt de Comando do Windows:

```bat
cd /d D:\ufba\Simulador-Escalonamento
```

Use a barra invertida (`\`) nos caminhos do Windows. Embora a barra comum
(`/`) possa funcionar em vários contextos, os exemplos deste documento seguem
a convenção do Windows.

---

## 3. Instalação das dependências

Na raiz do projeto, execute:

```powershell
py -m pip install -r requirements.txt
```

Se o Python estiver disponível como `python`, use:

```powershell
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` contém:

```text
pillow
pytest
```

Para instalar apenas o suporte à geração de imagens:

```powershell
python -m pip install pillow
```

Para instalar apenas o suporte aos testes:

```powershell
python -m pip install pytest
```

---

## 4. Sintaxe geral

A forma geral do comando é:

```text
python main.py --alg ALGORITMO --input ARQUIVO_JSON [OPÇÕES]
```

Os dois parâmetros `--alg` e `--input` são obrigatórios.

Exemplo mínimo:

```powershell
python main.py --alg FCFS --input casos/caso1.json
```

Exemplo com todos os resultados disponíveis:

```powershell
python main.py --alg CFS --input casos/caso1.json --gantt out/caso1.png --log out/caso1.log --seed 42 --delay 150
```

### 4.1. Lista completa de parâmetros

| Parâmetro | Obrigatório | Tipo | Significado |
|---|---:|---|---|
| `--alg` | Sim | texto | Algoritmo ou conjunto de algoritmos a executar |
| `--input` | Sim | caminho | Arquivo JSON contendo configuração e processos |
| `--gantt` | Não | caminho | Caminho do arquivo PNG do gráfico de Gantt |
| `--log` | Não | caminho | Caminho do arquivo textual da execução |
| `--seed` | Não | inteiro | Valor de semente informado à configuração |
| `--quantum` | Não | inteiro | Sobrescreve o campo `quantum` do JSON |
| `--overhead` | Não | inteiro | Sobrescreve `sobrecarga_contexto` do JSON |
| `--delay` | Não | inteiro | Intervalo em milissegundos entre eventos no modo passo a passo |
| `-h`, `--help` | Não | — | Exibe a ajuda da interface |

A opção `--seed` é aceita pela CLI e armazenada na configuração. Na versão
atual, nenhum algoritmo usa aleatoriedade, portanto ela não altera o
resultado dos algoritmos existentes.

---

## 5. Consultando a ajuda

Para listar parâmetros e valores aceitos:

```powershell
python main.py --help
```

Saída resumida esperada:

```text
usage: simso [-h] --alg ALG --input INPUT [--gantt GANTT] [--log LOG]
             [--seed SEED] [--quantum QUANTUM] [--overhead OVERHEAD]
             [--delay DELAY]
```

Se o Python apresentar `ModuleNotFoundError`, confirme a dependência instalada
com:

```powershell
python -m pip show pillow pytest
```

---

## 6. O parâmetro `--alg`

O parâmetro `--alg` escolhe o algoritmo. Letras minúsculas são aceitas,
pois o programa converte o valor informado para maiúsculas.

### 6.1. Algoritmos disponíveis

| Valor | Nome | Tipo | Explicação |
|---|---|---|---|
| `FCFS` | First Come, First Served | Não preemptivo | Executa o processo mais antigo pela chegada |
| `FIFO` | Primeiro a Entrar, Primeiro a Sair | Não preemptivo | Alias de `FCFS` |
| `SJF` | Shortest Job First | Não preemptivo | Escolhe o processo pronto com menor execução total |
| `RR` | Round-Robin | Preemptivo por fatia | Alterna processos em uma fila circular |
| `PRIORITY` | Prioridades | Preemptivo por fatia | Executa o menor número de prioridade |
| `EDF` | Earliest Deadline First | Preemptivo por fatia | Executa o processo com deadline absoluto mais próximo |
| `CFS` | Completamente Fair Scheduler — simulado | Preemptivo por fatia | Escolhe o menor `vruntime` |
| `AUTORAL` | HRRN — Highest Response Ratio Next | Preemptivo por fatia | Usa a maior razão `(espera + restante) / restante` |
| `ALL` | Todos os algoritmos acima | Comparativo | Executa FCFS, SJF, RR, PRIORITY, EDF, CFS e AUTORAL |

O valor `ALL` não inclui uma entrada duplicada de `FIFO`, pois `FIFO` é apenas
um nome alternativo para `FCFS`.

### 6.2. Exemplos por algoritmo

FCFS:

```powershell
python main.py --alg FCFS --input casos/caso1.json
```

SJF:

```powershell
python main.py --alg SJF --input casos/caso1.json
```

Round-Robin:

```powershell
python main.py --alg RR --input casos/caso1.json
```

Prioridades:

```powershell
python main.py --alg PRIORITY --input casos/caso1.json
```

EDF:

```powershell
python main.py --alg EDF --input casos/caso1.json
```

CFS:

```powershell
python main.py --alg CFS --input casos/caso1.json
```

Algoritmo autoral:

```powershell
python main.py --alg AUTORAL --input casos/caso1.json
```

Todos os algoritmos:

```powershell
python main.py --alg ALL --input casos/caso1.json
```

O nome em letras minúsculas também é aceito:

```powershell
python main.py --alg rr --input casos/caso1.json
```

---

## 7. O parâmetro `--input`

`--input` informa o caminho de um arquivo JSON.

Exemplos:

```powershell
python main.py --alg FCFS --input casos/caso1.json
python main.py --alg EDF --input casos/caso_ocioso.json
python main.py --alg ALL --input casos/caso_professor.json
```

Caminho relativo:

```text
casos/caso1.json
```

é relativo ao diretório atual do terminal.

Caminho absoluto no Windows:

```powershell
python main.py --alg SJF --input "D:\ufba\Simulador-Escalonamento\casos\caso1.json"
```

Aspas são recomendadas quando o caminho contém espaços.

---

## 8. Formato do arquivo JSON

### 8.1. Exemplo completo

```json
{
  "quantum": 2,
  "sobrecarga_contexto": 1,
  "custo_disco": 3,
  "seed": 42,
  "processos": [
    {
      "id": "P1",
      "chegada": 0,
      "execucao": 5,
      "deadline": 8,
      "prioridade": 2
    },
    {
      "id": "P2",
      "chegada": 1,
      "execucao": 4,
      "deadline": 12,
      "prioridade": 1
    }
  ]
}
```

### 8.2. Campos da configuração

| Campo | Tipo | Padrão | Significado |
|---|---|---|---|
| `quantum` | inteiro | `2` | Duração máxima de uma fatia para algoritmos preemptivos |
| `sobrecarga_contexto` | inteiro | `0` | Tempo cobrado por troca ou mudança de processo |
| `custo_disco` | inteiro | `0` | Campo reservado; atualmente não é usado |
| `seed` | inteiro ou nulo | `null` | Semente armazenada na configuração; sem efeito aleatório atual |
| `deadline_relativo` | booleano | `false` | Define se os deadlines dos processos são relativos à chegada |
| `processos` | lista | obrigatória | Lista de processos da simulação |

Exemplo mostrando o padrão:

```json
{
  "processos": [
    {
      "id": "A",
      "chegada": 0,
      "execucao": 3
    }
  ]
}
```

Neste caso, `quantum` será `2`, a sobrecarga será `0`, não haverá deadline nem
prioridade e não haverá custo de disco.

### 8.3. Campos de cada processo

| Campo | Obrigatório | Tipo | Significado |
|---|---:|---|---|
| `id` | Sim | inteiro ou texto | Identificador único usado em tabelas e Gantt |
| `chegada` | Sim | inteiro | Unidade de tempo em que o processo entra no sistema |
| `execucao` | Sim | inteiro | Tempo total de CPU necessário |
| `deadline` | Não | inteiro | Limite de conclusão absoluto ou relativo |
| `prioridade` | Não | inteiro | Nível usado pelo algoritmo de prioridades e pelo CFS |

Exemplo:

```json
{
  "id": "A",
  "chegada": 4,
  "execucao": 7,
  "deadline": 15,
  "prioridade": 1
}
```

Termos:

- **chegada**: instante em que o processo passa a estar pronto;
- **execucao** ou **burst**: quantidade de tempo de CPU necessária;
- **deadline**: prazo máximo de conclusão;
- **prioridade**: quanto menor o número, maior a prioridade;
- **pronto**: processo disponível para uso da CPU;
- **execução**: tempo em que o processo usa efetivamente a CPU;
- **fatia**: intervalo seguido pelo algoritmo antes de reavaliar a fila.

### 8.4. Tipos e regras válidas

O programa valida os valores dos processos.

Regras atuais:

- `chegada` deve ser um inteiro;
- `execucao` deve ser um inteiro maior que zero;
- `deadline`, quando informado, deve ser um inteiro;
- em JSON com deadline relativo, o deadline relativo deve ser maior ou igual a zero;
- `prioridade`, quando informada, deve ser um inteiro;
- booleanos não são aceitos como valores numéricos.

Exemplo inválido:

```json
{
  "id": "P1",
  "chegada": 0,
  "execucao": 0
}
```

Aqui, `execucao` é igual a zero e o programa rejeita o processo.

### 8.5. Deadline absoluto

Por padrão, o deadline é absoluto.

Considere:

```json
{
  "id": "P1",
  "chegada": 2,
  "execucao": 4,
  "deadline": 10
}
```

Neste modo, o processo deve terminar até o instante absoluto `10`, independentemente
de ter chegado no instante `2`.

Internamente, o programa converte esse valor em um deadline relativo à chegada:

```text
deadline relativo = deadline absoluto - instante de chegada
10 - 2 = 8
```

O relatório retorna o deadline absoluto original na tabela.

### 8.6. Deadline relativo

Para declarar um prazo contado a partir da chegada, use
`"deadline_relativo": true` no nível principal:

```json
{
  "deadline_relativo": true,
  "processos": [
    {
      "id": "P1",
      "chegada": 2,
      "execucao": 4,
      "deadline": 10
    }
  ]
}
```

Nesse exemplo, o prazo é relativo à chegada:

```text
prazo efetivo = chegada + deadline
2 + 10 = 12
```

Portanto, o processo deve terminar até o instante absoluto `12`.

O arquivo `casos/caso_professor.json` usa esse modo.

### 8.7. Processos sem deadline

Um processo pode omitir `deadline`:

```json
{
  "id": "P3",
  "chegada": 5,
  "execucao": 2,
  "prioridade": 3
}
```

Nesse caso, o campo `deadline_ok?` exibido na tabela será `-`.

### 8.8. Exemplo do caso incluso

O arquivo `casos/caso1.json` contém:

```json
{
  "quantum": 2,
  "sobrecarga_contexto": 1,
  "custo_disco": 3,
  "seed": 42,
  "processos": [
    {"id": "P1", "chegada": 0, "execucao": 5, "deadline": 8, "prioridade": 2},
    {"id": "P2", "chegada": 1, "execucao": 4, "deadline": 12, "prioridade": 1},
    {"id": "P3", "chegada": 3, "execucao": 2, "deadline": 20, "prioridade": 3}
  ]
}
```

Nesse arquivo:

- o quantum padrão é `2`;
- a sobrecarga padrão é `1`;
- o prazo de P1 é absoluto e termina no instante `8`;
- P1 chegou no instante `0`, mas P2 chegou no instante `1`;
- P3 chegou no instante `3`;
- o campo `custo_disco` não altera o resultado nesta versão.

---

## 9. O parâmetro `--quantum`

Quantum é o tamanho máximo de uma fatia para algoritmos que necessitam desse
parâmetro: RR, PRIORITY, EDF, CFS e AUTORAL.

O valor do quantum pode vir do JSON:

```json
{
  "quantum": 4,
  "processos": []
}
```

Ele pode ser substituído na linha de comando:

```powershell
python main.py --alg RR --input casos/caso1.json --quantum 3
```

Nesse exemplo, o JSON continua sem alterações. O valor `3` é usado apenas para
a execução.

Exemplo com todos os algoritmos:

```powershell
python main.py --alg ALL --input casos/caso1.json --quantum 1
```

`quantum` deve ser maior que zero para RR, PRIORITY, EDF, CFS e AUTORAL.

Os algoritmos não preemptivos FCFS e SJF ignoram o quantum para a decisão de
escalonamento. Eles executam o processo escolhido até a conclusão.

Exemplos:

```text
quantum = 1: cada fatia tenta executar até uma unidade de tempo
quantum = 2: cada fatia tenta executar até duas unidades de tempo
quantum = 5: cada fatia pode alcançar cinco unidades de tempo
```

Se o restante do processo for menor que o quantum, a fatia usa apenas o tempo
restante necessário para concluir.

---

## 10. O parâmetro `--overhead`

Sobrecarga de contexto é o custo em unidades de tempo cobrado quando ocorre uma
mudança ou troca de contexto.

Definição no JSON:

```json
{
  "sobrecarga_contexto": 2
}
```

Substituição pelo terminal:

```powershell
python main.py --alg RR --input casos/caso1.json --overhead 2
```

Exemplo sem sobrecarga:

```powershell
python main.py --alg RR --input casos/caso1.json --overhead 0
```

O número informado deve representar unidades de tempo inteiras.

O comportamento usado pelo simulador:

- FCFS e SJF não cobram sobrecarga porque executam até terminar;
- para algoritmos preemptivos, a sobrecarga é cobrada ao fim de uma fatia em
  que o processo não termina;
- se o processo termina em uma fatia, o próximo processo começa sem uma
  sobrecarga intermediária;
- a sobrecarga aparece em vermelho no Gantt;
- o tempo de sobrecarga é incluído nas métricas globais.

Exemplo de troca:

```text
P1 executa por 2 u.t.
P1 não terminou.
A sobrecarga leva 1 u.t.
P2 executa a seguir.
```

---

## 11. O parâmetro `--seed`

O seed é usado para informar uma semente às classes dos algoritmos:

```powershell
python main.py --alg CFS --input casos/caso1.json --seed 42
```

Também pode vir do JSON:

```json
{
  "seed": 42
}
```

O valor pode ser sobrescrito pelo parâmetro de linha de comando:

```powershell
python main.py --alg CFS --input casos/caso1.json --seed 100
```

Na implementação atual, não há sorteio ou geração aleatória dentro dos
algoritmos. Portanto, `--seed` é aceito e armazenado, mas não modifica uma
execução determinística do conjunto atual.

---

## 12. O parâmetro `--delay`

`--delay` ativa a impressão passo a passo dos eventos da linha do tempo.

O valor é medido em milissegundos entre eventos:

```powershell
python main.py --alg RR --input casos/caso1.json --delay 150
```

`150` significa 150 milissegundos, ou 0,15 segundo, entre a impressão de cada
evento.

Exemplo rápido:

```powershell
python main.py --alg FCFS --input casos/caso1.json --delay 250
```

Exemplo sem atraso:

```powershell
python main.py --alg FCFS --input casos/caso1.json --delay 0
```

O padrão é `0`, portanto o modo passo a passo fica desativado e os eventos não
recebem um atraso artificial.

Cada evento exibido usa uma das formas:

```text
Tempo 0: CPU com Processo P1
Tempo 2: CPU ociosa
Tempo 4: CPU com Processo P2  (sobrecarga de contexto)
```

No modo `ALL`, o atraso é aplicado para cada algoritmo separadamente.

---

## 13. O parâmetro `--gantt`

`--gantt` cria uma imagem PNG representando a execução.

Exemplo:

```powershell
python main.py --alg FCFS --input casos/caso1.json --gantt out/caso1_fcfs.png
```

O diretório de saída é criado automaticamente.

Em modo `ALL`:

```powershell
python main.py --alg ALL --input casos/caso1.json --gantt out/caso1.png
```

Para `out/caso1.png`, o programa cria:

```text
out/caso1_FCFS.png
out/caso1_SJF.png
out/caso1_RR.png
out/caso1_PRIORITY.png
out/caso1_EDF.png
out/caso1_CFS.png
out/caso1_AUTORAL.png
```

A regra é adicionar o nome do algoritmo antes da extensão:

```text
arquivo_base.extensão
arquivo_base_ALGORITMO.extensão
```

Significado das cores no Gantt:

| Cor | Significado |
|---|---|
| Verde | Processo executando na CPU |
| Vermelho | Sobrecarga de troca de contexto |
| Amarelo | Processo pronto aguardando na linha do processo |
| Cinza | Execução depois do deadline |
| Azul vertical | Deadline absoluto |

O Gantt usa uma unidade horizontal por unidade de tempo até o limite visual
permitido pelo desenho. O tamanho pode ser limitado automaticamente.

---

## 14. O parâmetro `--log`

`--log` cria um arquivo textual com a linha do tempo e o relatório da
simulação.

Exemplo:

```powershell
python main.py --alg FCFS --input casos/caso1.json --log out/caso1.log
```

O log contém:

1. uma linha para cada unidade de tempo;
2. uma linha em branco;
3. o nome do algoritmo;
4. a tabela de processos;
5. o resumo das métricas.

Exemplo de início:

```text
Tempo 0: CPU com Processo P1
Tempo 1: CPU com Processo P1
Tempo 5: CPU ociosa
```

No modo `ALL`, o sufixo do algoritmo também é aplicado:

```powershell
python main.py --alg ALL --input casos/caso1.json --log out/caso1.log
```

Arquivos esperados:

```text
out/caso1_FCFS.log
out/caso1_SJF.log
out/caso1_RR.log
out/caso1_PRIORITY.log
out/caso1_EDF.log
out/caso1_CFS.log
out/caso1_AUTORAL.log
```

O diretório `out` é criado automaticamente.

---

## 15. Usando vários resultados juntos

Exemplo recomendado para um estudo comparativo:

```powershell
New-Item -ItemType Directory -Force out | Out-Null
python main.py --alg ALL --input casos/caso1.json --gantt out/caso1.png --log out/caso1.log --seed 42 --quantum 2 --overhead 1
```

O comando:

- executa os sete algoritmos;
- cria sete imagens em `out`;
- cria sete logs em `out`;
- usa um quantum de `2`;
- usa sobrecarga de `1`;
- fornece seed `42`;
- imprime uma tabela comparativa ao final.

Como alternativa, o diretório pode ser criado pelo próprio programa. Não é
necessário criar `out` antecipadamente para `--gantt` ou `--log`.

---

## 16. Entendendo a tabela de processos

A tabela exibida no terminal usa os seguintes nomes:

| Coluna | Significado |
|---|---|
| `id` | Identificador do processo |
| `chegada` | Instante de chegada |
| `execucao` | Tempo total de execução solicitado |
| `deadline` | Deadline absoluto convertido pelo programa |
| `prioridade` | Prioridade do processo, se existir |
| `inicio` | Primeira unidade em que o processo começa a usar a CPU |
| `termino` | Unidade em que o processo termina |
| `espera` | Tempo total em que o processo aguardou a CPU |
| `turnaround` | Intervalo entre chegada e término |
| `deadline_ok?` | Indica se o processo cumpriu o deadline |

Valor `-` em `deadline_ok?` significa que o processo não tinha deadline.

Valor `NAO (estourou)` significa que o término ocorreu depois do deadline.

---

## 17. Entendendo o resumo de métricas

Exemplo de resumo:

```text
Turnaround médio ........ 12.50
Espera média ............ 8.00
Resposta média (inicio) . 5.50
Deadlines estourados .... 1
Throughput .............. 0.2000 processos/u.t.
CPU ociosa .............. 3 u.t. (12.0%)
Sobrecarga de contexto .. 4 u.t. (16.0%)
Trocas de contexto ...... 2
Tempo total ............. 25 u.t.
```

### 17.1. Turnaround médio

Turnaround é o tempo desde a chegada até a conclusão:

```text
turnaround = término - chegada
```

O turnaround médio é a média dos turnaround de todos os processos.

Apesar do nome tradicional “tempo médio de resposta” usado em alguns exercícios,
o campo `Turnaround médio` representa o valor calculado pelo programa.

### 17.2. Espera média

A espera é o tempo em que o processo ficou pronto sem usar a CPU:

```text
espera = turnaround - execução
```

A espera média é a média desse valor entre todos os processos.

### 17.3. Resposta média

A resposta individual é o tempo até o início da primeira execução:

```text
resposta = início da primeira execução - chegada
```

A resposta média é a média desses valores.

### 17.4. Deadlines estourados

Quantidade de processos cujo instante de término é posterior ao deadline:

```text
término > deadline
```

Processos sem deadline não contam como estourados.

### 17.5. Throughput

Quantidade de processos concluídos por unidade de tempo:

```text
throughput = número de processos / tempo total
```

No relatório, o valor usa quatro casas decimais.

### 17.6. CPU ociosa

Tempo em que a CPU não executou processos nem sobrecarga.

Também é exibido como percentual do tempo total:

```text
percentual ocioso = 100 * tempo ocioso / tempo total
```

### 17.7. Sobrecarga de contexto

Tempo gasto em trocas de contexto.

No relatório são exibidos:

- o tempo total em unidades de tempo;
- o percentual em relação ao tempo total.

### 17.8. Trocas de contexto

Quantidade de trocas contadas pelo mecanismo do simulador.

Esse campo não representa diretamente o número de processos únicos; ele conta
eventos de troca registrados pelo escalonador.

### 17.9. Tempo total

Maior instante de término registrado entre os processos.

O tempo total não inclui necessariamente o tempo desde o zero até o término
de cada processo se houver chegadas futuras, mas sim o horizonte final da
simulação calculado pelo código.

---

## 18. Entendendo a comparação no modo `ALL`

O modo `ALL` gera uma tabela final semelhante a:

| algoritmo | turnaround | espera | resposta | estouros | throughput | ocioso% | sobrecarga% | trocas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FCFS | 10.67 | 6.67 | 1.67 | 1 | 0.2000 | 0.0 | 0.0 | 0 |

Como as métricas são arredondadas na comparação, use os logs ou o relatório
individual para inspeção mais precisa.

---

## 19. Comportamento dos principais algoritmos

### 19.1. FCFS

Executa o processo que chegou primeiro e não permite preempção.

Depois que o processo entra na CPU, ele permanece até terminar.

Comando:

```powershell
python main.py --alg FCFS --input casos/caso1.json
```

O parâmetro `FIFO` produz o mesmo resultado:

```powershell
python main.py --alg FIFO --input casos/caso1.json
```

### 19.2. SJF

Escolhe o processo pronto com menor tempo total de execução.

Também não é preemptivo.

Comando:

```powershell
python main.py --alg SJF --input casos/caso1.json
```

Exemplo de decisão:

```text
P1 tem execucao = 8
P2 tem execucao = 3
P3 tem execucao = 5
escolhido: P2
```

### 19.3. Round-Robin

Executa cada processo por uma fatia de quantum.

Depois da fatia, o processo pode voltar ao fim da fila.

Comando:

```powershell
python main.py --alg RR --input casos/caso1.json --quantum 2
```

Processos que chegam até o fim da sobrecarga entram antes do processo
preemptado que volta ao fim da fila.

### 19.4. Prioridades

Escolhe o processo com menor número de prioridade.

Exemplo:

```text
P1 prioridade = 3
P2 prioridade = 1
P3 prioridade = 2
escolhido: P2
```

O algoritmo reavalia a fila nas fronteiras de quantum e é preemptivo.

Comando:

```powershell
python main.py --alg PRIORITY --input casos/caso1.json --quantum 2
```

### 19.5. EDF

Escolhe o processo com o menor deadline absoluto.

Comando:

```powershell
python main.py --alg EDF --input casos/caso1.json --quantum 2
```

Exemplo:

```text
P1 deadline absoluto = 20
P2 deadline absoluto = 12
P3 sem deadline
escolhido: P2
```

Um processo sem deadline não participa da comparação por deadline.

### 19.6. CFS

O CFS-Simulado acompanha uma variável `vruntime`.

Regras atuais:

```text
vruntime inicial = tempo de chegada
vruntime += Δt * 1.25^(prioridade - 1)
```

`Δt` é o tempo efetivamente executado. O processo escolhido é aquele com menor
`vruntime`.

Comando:

```powershell
python main.py --alg CFS --input casos/caso1.json --quantum 2
```

Quanto maior a prioridade:

- o código usa `prioridade - 1`;
- prioridade menor recebe um fator menor;
- a prioridade `1` recebe fator `1.25^0 = 1`;
- a prioridade `2` recebe fator `1.25^1 = 1.25`;
- a prioridade `3` recebe fator `1.25^2 = 1.5625`.

### 19.7. AUTORAL

O algoritmo autoral usa uma versão preemptiva de HRRN.

A razão é calculada assim:

```text
razão = (espera + restante) / restante
```

O processo com maior razão é escolhido. Quanto mais tempo um processo espera,
maior tende a ser sua razão, reduzindo o risco de inanição.

Comando:

```powershell
python main.py --alg AUTORAL --input casos/caso1.json --quantum 2
```

---

## 20. Exemplos completos

### 20.1. Executar FCFS sem arquivos adicionais

```powershell
python main.py --alg FCFS --input casos/caso1.json
```

### 20.2. Executar RR com quantum personalizado

```powershell
python main.py --alg RR --input casos/caso1.json --quantum 4
```

### 20.3. Executar EDF com sobrecarga personalizada

```powershell
python main.py --alg EDF --input casos/caso_professor.json --overhead 2
```

### 20.4. Criar Gantt e log

```powershell
python main.py --alg CFS --input casos/caso1.json --gantt saidas/caso1_cfs.png --log saidas/caso1_cfs.log
```

### 20.5. Gerar os resultados completos de todos os algoritmos

```powershell
python main.py --alg ALL --input casos/caso1.json --gantt saidas/tudo.png --log saidas/tudo.log --seed 42 --quantum 2 --overhead 1
```

### 20.6. Comparação usando deadline relativo

```powershell
python main.py --alg ALL --input casos/caso_professor.json --quantum 2 --overhead 1
```

### 20.7. Executar com CPU ociosa

```powershell
python main.py --alg EDF --input casos/caso_ocioso.json --gantt saidas/ocioso.png
```

### 20.8. Execução passo a passo com Gantt e log

```powershell
python main.py --alg RR --input casos/caso1.json --delay 100 --gantt saidas/rr_passo.png --log saidas/rr_passo.log
```

### 20.9. Execução determinística com CFS

```powershell
python main.py --alg CFS --input casos/caso1.json --seed 42 --quantum 2 --overhead 1
```

---

## 21. Criando seu próprio arquivo JSON

### 21.1. Usando um único processo

`casos/meu_caso.json`:

```json
{
  "quantum": 2,
  "sobrecarga_contexto": 1,
  "processos": [
    {
      "id": "P1",
      "chegada": 0,
      "execucao": 5
    }
  ]
}
```

Execução:

```powershell
python main.py --alg RR --input casos/meu_caso.json
```

### 21.2. Usando prioridades

```json
{
  "quantum": 2,
  "sobrecarga_contexto": 1,
  "processos": [
    {"id": "A", "chegada": 0, "execucao": 6, "prioridade": 3},
    {"id": "B", "chegada": 1, "execucao": 3, "prioridade": 1},
    {"id": "C", "chegada": 2, "execucao": 4, "prioridade": 2}
  ]
}
```

Execução:

```powershell
python main.py --alg PRIORITY --input casos/meu_caso.json --quantum 2
```

### 21.3. Usando deadlines absolutos

```json
{
  "deadline_relativo": false,
  "quantum": 2,
  "sobrecarga_contexto": 1,
  "processos": [
    {"id": "A", "chegada": 0, "execucao": 5, "deadline": 8},
    {"id": "B", "chegada": 2, "execucao": 3, "deadline": 12},
    {"id": "C", "chegada": 4, "execucao": 2, "deadline": 10}
  ]
}
```

Execução:

```powershell
python main.py --alg EDF --input casos/meu_caso.json --gantt out/meu_edf.png
```

### 21.4. Usando deadlines relativos

```json
{
  "deadline_relativo": true,
  "quantum": 2,
  "sobrecarga_contexto": 1,
  "processos": [
    {"id": "A", "chegada": 0, "execucao": 5, "deadline": 8},
    {"id": "B", "chegada": 2, "execucao": 3, "deadline": 12},
    {"id": "C", "chegada": 4, "execucao": 2, "deadline": 10}
  ]
}
```

Nesse formato:

```text
A: deadline absoluto = 0 + 8 = 8
B: deadline absoluto = 2 + 12 = 14
C: deadline absoluto = 4 + 10 = 14
```

---

## 22. Executando testes

Na raiz do projeto:

```powershell
python -m pytest
```

Para executar um arquivo de testes específico:

```powershell
python -m pytest tests/test_algorithms.py
```

Para mostrar nomes dos testes durante a execução:

```powershell
python -m pytest -v
```

Para interromper no primeiro erro:

```powershell
python -m pytest -x
```

`pytest` aceita padrões de caminho. Exemplos:

```powershell
python -m pytest tests/test-app-fcfs-one.py
python -m pytest tests/test_algorithms.py -k EDF
```

Não confunda o nome da opção `-k` de filtro dos testes com o parâmetro
`--alg` do simulador.

---

## 23. Possíveis erros e soluções

### 23.1. `module 'PIL' has no attribute` ou erro ao importar Pillow

Instale o pacote:

```powershell
python -m pip install --upgrade pillow
```

Execute novamente com `--gantt`.

### 23.2. `No module named pytest`

Instale o pacote:

```powershell
python -m pip install pytest
```

Depois execute:

```powershell
python -m pytest
```

### 23.3. `Algoritmo desconhecido`

O algoritmo informado não pertence à lista aceita.

Use um valor válido:

```text
FCFS
FIFO
SJF
RR
PRIORITY
EDF
CFS
AUTORAL
ALL
```

Exemplo correto:

```powershell
python main.py --alg FCFS --input casos/caso1.json
```

### 23.4. `RR exige quantum > 0`

O algoritmo preemptivo recebeu um quantum ausente ou menor ou igual a zero.

Corrija no JSON:

```json
{
  "quantum": 2
}
```

Ou substitua na linha de comando:

```powershell
python main.py --alg RR --input casos/caso1.json --quantum 2
```

### 23.5. `burst_time do processo X deve ser > 0`

A execução informada no processo é zero ou negativa.

Use um número inteiro positivo:

```json
{
  "id": "X",
  "chegada": 0,
  "execucao": 5
}
```

### 23.6. `deadline do processo X deve ser > 0`

Isso ocorre quando `deadline_relativo` é `true` e o valor relativo não é
positivo.

Corrija o deadline ou remova `deadline_relativo` para tratar o valor como
deadline absoluto.

### 23.7. Erro de arquivo não encontrado

Confirme que está na raiz do projeto:

```powershell
Get-Location
Get-ChildItem casos
```

Use o caminho completo se necessário:

```powershell
python main.py --alg FCFS --input "D:\ufba\Simulador-Escalonamento\casos\caso1.json"
```

### 23.8. Erro de JSON

Os erros podem ser causados por:

- vírgula após o último elemento;
- aspas simples em vez de aspas duplas;
- chave ou texto sem aspas;
- falta de colchetes em `processos`;
- caracteres inválidos no arquivo.

Exemplo correto:

```json
{
  "processos": [
    {"id": "P1", "chegada": 0, "execucao": 3}
  ]
}
```

Exemplo incorreto:

```json
{
  "processos": [
    {'id': 'P1', 'chegada': 0, 'execucao': 3},
  ]
}
```

JSON aceita somente aspas duplas e não permite vírgula depois do último item.

### 23.9. Diretório ou extensão incorreta

Para evitar ambiguidades, use nomes explícitos:

```powershell
python main.py --alg FCFS --input casos/caso1.json --gantt out/caso1.png --log out/caso1.log
```

O Gantt deve apontar para um nome PNG, mas o programa não força a extensão
automaticamente. A extensão `.png` é recomendada.

### 23.10. Saída vazia ou diferentes esperados

Verifique:

1. o modo absoluto ou relativo do deadline;
2. o quantum usado;
3. a sobrecarga usada;
4. a prioridade dos processos;
5. o instante de chegada;
6. a execução total;
7. o algoritmo informado.

Quando dois algoritmos precisam ser comparados, use os mesmos parâmetros:

```powershell
python main.py --alg ALL --input casos/caso1.json --quantum 2 --overhead 1
```

---

## 24. Glossário

| Termo | Explicação |
|---|---|
| CPU | Unidade central de processamento usada pela simulação |
| Processo | Unidade representada por um identificador, chegada e execução |
| Chegada | Instante em que o processo entra na fila de prontos |
| Burst | Sinônimo de tempo total de execução |
| Execução | Tempo que o processo efetivamente usa a CPU |
| Quantum | Tempo máximo de uma fatia em algoritmos preemptivos |
| Fatia | Intervalo de execução contínua antes da reavaliação |
| Pronto | Estado em que o processo aguarda acesso à CPU |
| Fila | Conjunto de processos prontos para escalonamento |
| Preempção | Interrupção antes da conclusão para reavaliar o próximo processo |
| Não preemptivo | Processo continua até concluir quando recebe a CPU |
| Sobre carga de contexto | Tempo usado na troca de processos |
| Troca de contexto | Mudança do processo atual da CPU |
| Deadline | Prazo máximo para conclusão |
| Deadline absoluto | Instante único no horizonte da simulação |
| Deadline relativo | Prazo contado a partir da chegada |
| VRuntime | Tempo virtual usado pelo CFS-Sim |
| Aging | Envelhecimento ou aumento de prioridade causado pela espera |
| HRRN | Highest Response Ratio Next; algoritmo escolhido pela maior razão |
| Turnaround | Tempo entre chegada e término |
| Espera | Tempo que o processo passou pronto sem executar |
| Resposta | Tempo até o início da primeira execução |
| Throughput | Processos concluídos por unidade de tempo |
| Gantt | Diagrama horizontal com estados da execução ao longo do tempo |
| Seed | Semente de geração aleatória, caso o algoritmo a utilize |
| CLI | Interface de linha de comando |
| JSON | Formato textual usado para os dados de entrada |
| PNG | Formato de imagem usado pelo Gantt |
| Unit de tempo | Intervalo discreto usado pela simulação |

---

## 25. Referência rápida

```text
python main.py --alg FCFS --input casos/caso1.json
python main.py --alg FIFO --input casos/caso1.json
python main.py --alg SJF --input casos/caso1.json
python main.py --alg RR --input casos/caso1.json --quantum 2
python main.py --alg PRIORITY --input casos/caso1.json --quantum 2
python main.py --alg EDF --input casos/caso1.json --quantum 2
python main.py --alg CFS --input casos/caso1.json --quantum 2
python main.py --alg AUTORAL --input casos/caso1.json --quantum 2
python main.py --alg ALL --input casos/caso1.json

python main.py --alg ALL --input casos/caso1.json --gantt out/caso1.png --log out/caso1.log
python main.py --alg RR --input casos/caso1.json --delay 150
python main.py --alg RR --input casos/caso1.json --quantum 3 --overhead 1 --seed 42
python main.py --help
python -m pytest
```
