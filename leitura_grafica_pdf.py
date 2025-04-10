import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2

def selecionar_pdf():
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=(("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*"))
    )
    if caminho_arquivo:
        exibir_conteudo(caminho_arquivo)

def exibir_conteudo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'rb') as arquivo:
            leitor = PyPDF2.PdfReader(arquivo)
            conteudo = ""
            for pagina in leitor.pages:
                conteudo += pagina.extract_text()
            
            text_widget.delete(1.0, tk.END)  # Limpa o conteúdo anterior
            text_widget.insert(tk.END, conteudo)
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível ler o PDF.\nErro: {e}")

# Configuração da janela principal
janela = tk.Tk()
janela.title("Leitor de PDF")
janela.geometry("800x800")

# Botão para selecionar arquivo PDF
botao_selecionar = tk.Button(janela, text="Selecionar PDF", command=selecionar_pdf)
botao_selecionar.pack(pady=10)

# Área para exibir o conteúdo do PDF
text_widget = tk.Text(janela, wrap=tk.WORD, height=20, width=70)
text_widget.pack(pady=10)

# Iniciar a interface
janela.mainloop()
