nome_arquivo = "teste.txt"

# Função para ler o arquivo
def ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
            return conteudo
    except FileNotFoundError:
        return f"Erro: O arquivo '{nome_arquivo}' não foi encontrado."
    except Exception as e:
        return f"Erro: {e}"

# Exibindo o conteúdo do arquivo
conteudo = ler_arquivo(nome_arquivo)
print("Conteúdo do arquivo:")
print(conteudo)
