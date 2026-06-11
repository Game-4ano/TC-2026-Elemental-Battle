import sys
import os

# Adiciona o diretório atual ao PYTHONPATH para que o pacote 'meu_jogo' seja encontrado
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from meu_jogo.main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Erro ao importar o jogo: {e}")
    print("\nCertifique-se de que está a executar este script a partir da raiz do projeto:")
    print("Exemplo: python run.py")