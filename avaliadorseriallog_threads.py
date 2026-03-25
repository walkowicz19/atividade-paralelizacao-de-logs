import os
import time
import threading


# ===============================
# Processamento de arquivo
# ===============================

def processar_arquivo(caminho, resultados, lock):
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

    resultado = {
        "linhas": total_linhas,
        "palavras": total_palavras,
        "caracteres": total_caracteres,
        "contagem": contagem
    }

    with lock:
        resultados.append(resultado)


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
# Execução serial com threading
# (1 thread por vez — sequencial)
# ===============================

def executar_serial_threads(pasta):
    arquivos = [
        os.path.join(pasta, f)
        for f in os.listdir(pasta)
        if os.path.isfile(os.path.join(pasta, f))
    ]

    resultados = []
    lock = threading.Lock()

    inicio = time.time()

    for caminho in arquivos:
        t = threading.Thread(target=processar_arquivo, args=(caminho, resultados, lock))
        t.start()
        t.join()  # aguarda terminar antes de iniciar o próximo (serial)

    fim = time.time()

    resumo = consolidar_resultados(resultados)

    print("\n=== EXECUÇÃO SERIAL (threading) ===")
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

    print("Executando versão serial com threading (1 thread por vez)...")
    print("=" * 45)

    _, tempo = executar_serial_threads(pasta)

    print(f"\n=== RESUMO ===")
    print(f"  Tempo serial (threading): {tempo:.4f}s")
