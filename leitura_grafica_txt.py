import tkinter as tk
from tkinter import filedialog, messagebox

def selecionar_arquivo():
    # Abre uma janela para o usuário selecionar o arquivo
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo de texto",
        filetypes=(("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*"))
    )
    if caminho_arquivo:
        exibir_conteudo(caminho_arquivo)

def exibir_conteudo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            conteudo = arquivo.read()
            # Exibe o conteúdo na Text widget
            text_widget.delete(1.0, tk.END)  # Limpa o conteúdo anterior
            text_widget.insert(tk.END, conteudo)
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível ler o arquivo.\nErro: {e}")

# Configuração da janela principal
janela = tk.Tk()
janela.title("Leitor de Arquivo TXT")
janela.geometry("800x800")

# Botão para selecionar arquivo
botao_selecionar = tk.Button(janela, text="Selecionar Arquivo", command=selecionar_arquivo)
botao_selecionar.pack(pady=10)

# Área para exibir o conteúdo do arquivo
text_widget = tk.Text(janela, wrap=tk.WORD, height=20, width=70)
text_widget.pack(pady=10)

# Iniciar a interface
janela.mainloop()
