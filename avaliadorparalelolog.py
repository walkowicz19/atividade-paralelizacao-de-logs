import os
import time
import multiprocessing
from multiprocessing import Process, Queue, cpu_count
import sys

# ===============================
# Processamento de arquivo
# (sem simulação de carga pesada)
# ===============================

def processar_arquivo(caminho):
    total_linhas = 0
    total_palavras = 0
    total_caracteres = 0
    contagem = {"erro": 0, "warning": 0, "info": 0}

    with open(caminho, "r", encoding="utf-8") as f:
        for linha in f:
            total_linhas += 1
            total_caracteres += len(linha)
            palavras = linha.split()
            total_palavras += len(palavras)
            for p in palavras:
                if p in contagem:
                    contagem[p] += 1

    # Simulação de processamento pesado (mantida conforme original)
    for _ in range(1000):
        pass

    return {
        "linhas": total_linhas,
        "palavras": total_palavras,
        "caracteres": total_caracteres,
        "contagem": contagem
    }


# ===============================
# Worker (consumidor)
# ===============================

def worker(fila_tarefas, fila_resultados):
    while True:
        caminho = fila_tarefas.get()
        if caminho is None:  # sentinela de encerramento
            break
        resultado = processar_arquivo(caminho)
        fila_resultados.put(resultado)


# ===============================
# Consolidação dos resultados
# ===============================

def consolidar_resultados(resultados):
    total_linhas = 0
    total_palavras = 0
    total_caracteres = 0
    contagem_global = {"erro": 0, "warning": 0, "info": 0}

    for r in resultados:
        total_linhas += r["linhas"]
        total_palavras += r["palavras"]
        total_caracteres += r["caracteres"]
        for chave in contagem_global:
            contagem_global[chave] += r["contagem"][chave]

    return {
        "linhas": total_linhas,
        "palavras": total_palavras,
        "caracteres": total_caracteres,
        "contagem": contagem_global
    }


# ===============================
# Execução paralela (produtor-consumidor)
# ===============================

def executar_paralelo(pasta, num_processos):
    arquivos = [
        os.path.join(pasta, f)
        for f in os.listdir(pasta)
        if os.path.isfile(os.path.join(pasta, f))
    ]

    fila_tarefas = Queue(maxsize=num_processos * 4)  # buffer limitado
    fila_resultados = Queue()

    # Inicia os workers (consumidores)
    workers = []
    for _ in range(num_processos):
        p = Process(target=worker, args=(fila_tarefas, fila_resultados))
        p.start()
        workers.append(p)

    inicio = time.time()

    # Produtor: envia arquivos para a fila
    for caminho in arquivos:
        fila_tarefas.put(caminho)

    # Envia sentinelas para encerrar os workers
    for _ in range(num_processos):
        fila_tarefas.put(None)

    # Coleta resultados
    resultados = []
    for _ in range(len(arquivos)):
        resultados.append(fila_resultados.get())

    fim = time.time()

    for p in workers:
        p.join()

    resumo = consolidar_resultados(resultados)

    print(f"\n=== EXECUÇÃO PARALELA ({num_processos} processos) ===")
    print(f"Arquivos processados: {len(resultados)}")
    print(f"Tempo total: {fim - inicio:.4f} segundos")

    print("\n=== RESULTADO CONSOLIDADO ===")
    print(f"Total de linhas: {resumo['linhas']}")
    print(f"Total de palavras: {resumo['palavras']}")
    print(f"Total de caracteres: {resumo['caracteres']}")

    print("\nContagem de palavras-chave:")
    for k, v in resumo["contagem"].items():
        print(f"  {k}: {v}")

    return resumo, fim - inicio


# ===============================
# Main
# ===============================

if __name__ == "__main__":
    pasta = "log2"

    if len(sys.argv) > 1:
        configs = [int(sys.argv[1])]
    else:
        configs = [2, 4, 8, 12]

    print(f"CPUs disponíveis: {cpu_count()}")
    print(f"Pasta de logs: {pasta}")
    print("=" * 45)

    tempos = {}
    for n in configs:
        _, tempo = executar_paralelo(pasta, n)
        tempos[n] = tempo
        print()

    print("\n=== RESUMO DE TEMPOS ===")
    for n, t in tempos.items():
        print(f"  {n:2d} processos: {t:.4f}s")
