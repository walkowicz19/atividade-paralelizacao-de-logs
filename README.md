# Relatório — Paralelizar Avaliador de Arquivos de Log

**Disciplina:** Programação Concorrente  
**Aluno(s):** Matheus Nery Walkowicz
**Turma:** Noturno  
**Professor:** Rafael Marconi Ramos 
**Data:** 25/03/2026  

---

# 1. Descrição do Problema

O problema consiste em processar um grande volume de arquivos de log textuais, extraindo estatísticas agregadas como contagem de linhas, palavras, caracteres e ocorrências de palavras-chave (`erro`, `warning`, `info`).

A versão de referência realiza esse processamento de forma **serial com threading** (1 thread por vez), que serve como baseline T(1). O objetivo desta atividade foi implementar uma versão **paralela** utilizando o padrão **produtor-consumidor com buffer limitado**, explorando múltiplos processos para reduzir o tempo total.

**Questões respondidas:**

- **Objetivo do programa:** Consolidar métricas de arquivos de log operacionais para uso em relatórios gerenciais.
- **Volume de dados:** 1.000 arquivos, cada um com 10.000 linhas — totalizando 10 milhões de linhas, 200 milhões de palavras e ~1,37 GB de caracteres.
- **Algoritmo:** Produtor-consumidor com fila limitada (`multiprocessing.Queue`). O processo principal (produtor) distribui caminhos de arquivos; os workers (consumidores) processam cada arquivo e retornam os resultados.
- **Complexidade aproximada:** O(N × L), onde N = número de arquivos e L = linhas por arquivo — linear no total de dados.

---

# 2. Ambiente Experimental

| Item                        | Descrição                        |
| --------------------------- | -------------------------------- |
| Processador                 | 12th Gen Intel(R) Core(TM) i5-12500   3.00 GHz |
| Número de núcleos           | 12 Núcleos |
| Memória RAM                 | 16 GB DDR4 |
| Sistema Operacional         | Windows 11 |
| Linguagem utilizada         | Python                       |
| Biblioteca de paralelização | `multiprocessing` + `threading` (stdlib) |
| Versão Python               | 3.13.2 |

---

# 3. Metodologia de Testes

O tempo de execução foi medido com `time.time()` imediatamente antes da distribuição das tarefas e após a coleta de todos os resultados. Cada configuração foi executada **uma vez** com a pasta `log2` (1.000 arquivos × 10.000 linhas).

### Configurações testadas

- 1 thread (versão serial com threading — referência T(1))
- 2 processos
- 4 processos
- 8 processos
- 12 processos

### Procedimento experimental

- 1 execução por configuração
- Máquina em uso normal durante os testes
- Buffer da fila limitado a `num_processos × 4` slots
- Sentinelas `None` utilizadas para encerramento dos workers

---

# 4. Resultados Experimentais

| Nº Processos | Tempo de Execução (s) |
| ------------ | --------------------- |
| 1 (serial threading) | 19.8888        |
| 2            | 10.3750               |
| 4            | 5.9962                |
| 8            | 3.6839                |
| 12           | 3.3992                |

### Resultado consolidado (todos os testes produziram o mesmo resultado correto)

| Métrica               | Valor          |
| --------------------- | -------------- |
| Total de linhas       | 10.000.000     |
| Total de palavras     | 200.000.000    |
| Total de caracteres   | 1.366.663.305  |
| Ocorrências `erro`    | 33.332.083     |
| Ocorrências `warning` | 33.330.520     |
| Ocorrências `info`    | 33.329.065     |

---

# 5. Cálculo de Speedup e Eficiência

### Fórmulas utilizadas

```
Speedup(p)    = T(1) / T(p)
Eficiência(p) = Speedup(p) / p
```

Onde **T(1) = 19.8888s** (tempo serial com threading de referência).

---

# 6. Tabela de Resultados

| Processos | Tempo (s) | Speedup | Eficiência |
| --------- | --------- | ------- | ---------- |
| 1 (serial)| 19.8888   | 1.00    | 1.000      |
| 2         | 10.3750   | 1.92    | 0.960      |
| 4         | 5.9962    | 3.32    | 0.830      |
| 8         | 3.6839    | 5.40    | 0.675      |
| 12        | 3.3992    | 5.85    | 0.487      |

---

# 7. Gráfico de Tempo de Execução

![Gráfico Tempo Execução](grafico1.png)

---

# 8. Gráfico de Speedup

![Gráfico Speedup](grafico2.png)

---

# 9. Gráfico de Eficiência

![Gráfico Eficiência](grafico3.png)

---

# 10. Análise dos Resultados

**O speedup obtido foi próximo do ideal?**  
O speedup foi superlinear em todas as configurações. Com 2 processos o speedup foi ~1.9x (ideal seria 2x), e com 12 processos chegou a ~5.8x (ideal seria 12x). Isso ocorre porque cada processo opera sobre um subconjunto menor de dados, aproveitando melhor o cache de CPU, além de contornar o GIL do Python via `multiprocessing`.

**A aplicação apresentou escalabilidade?**  
Sim, porém com retornos decrescentes a partir de 8 processos. A transição de 2→4 processos reduziu o tempo de 10.37s para 5.99s (~42%), enquanto de 8→12 reduziu apenas de 3.68s para 3.39s (~8%), indicando aproximação do limite de saturação dos núcleos disponíveis.

**Em qual ponto a eficiência começou a cair?**  
A eficiência cai a cada adição de processos (de 0.960 com 2 processos para 0.487 com 12), o que é esperado. O ganho marginal entre 8 e 12 processos foi mínimo (~0.28s), sugerindo que o gargalo passou a ser I/O de disco e overhead de gerenciamento de processos.

**Houve overhead de paralelização?**  
Sim, especialmente notável em 12 processos. O overhead inclui: criação e encerramento de processos, serialização/desserialização de dados entre processos via `Queue`, e possível contenção no acesso ao disco.

---

# 11. Conclusão

O paralelismo trouxe ganho expressivo de desempenho: o tempo caiu de **19.89s** (serial threading) para **3.39s** com 12 processos — uma redução de **83%** no tempo de execução.

O melhor custo-benefício foi com **8 processos**, que entregou speedup de ~5.4x com eficiência ainda razoável. Com 12 processos o ganho adicional foi marginal (~0.28s), indicando saturação nessa configuração de hardware.

O padrão **produtor-consumidor com buffer limitado** mostrou-se adequado para o problema, pois desacopla a leitura de arquivos do processamento e evita sobrecarga de memória com o buffer controlado.

**Possíveis melhorias:**
- Usar `mmap` para leitura mais eficiente dos arquivos
- Processar múltiplos arquivos por worker em batch para reduzir overhead de IPC
- Avaliar uso de `concurrent.futures.ProcessPoolExecutor` para código mais limpo
