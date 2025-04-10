import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path


def extrair_texto_pymupdf(caminho_pdf):
    """Lê um PDF e extrai o texto usando PyMuPDF."""
    try:
        with fitz.open(caminho_pdf) as pdf:
            return "\n".join([pagina.get_text() for pagina in pdf])
    except Exception as e:
        return f"Erro ao ler o PDF com PyMuPDF: {e}"


def extrair_texto_ocr(caminho_pdf):
    """Lê um PDF e extrai o texto usando OCR."""
    try:
        imagens = convert_from_path(caminho_pdf)
        return "\n".join([pytesseract.image_to_string(img, lang='por') for img in imagens])
    except Exception as e:
        return f"Erro ao processar o PDF com OCR: {e}"


def selecionar_pdf():
    """Abre um diálogo para o usuário selecionar um PDF e processa o texto."""
    caminho_pdf = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
    )
    if not caminho_pdf:
        return

    metodo = var_metodo.get()
    texto_extraido = extrair_texto_pymupdf(caminho_pdf) if metodo == "pymupdf" else extrair_texto_ocr(caminho_pdf)

    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, texto_extraido)


def criar_interface():
    """Cria a interface gráfica com Tkinter."""
    global text_widget, var_metodo

    janela = tk.Tk()
    janela.title("Leitor de PDF")
    janela.geometry("800x600")

    tk.Button(janela, text="Selecionar PDF", command=selecionar_pdf).pack(pady=10)

    var_metodo = tk.StringVar(value="pymupdf")
    frame_opcoes = tk.Frame(janela)
    frame_opcoes.pack(pady=10)
    tk.Radiobutton(frame_opcoes, text="Usar PyMuPDF (texto)", variable=var_metodo, value="pymupdf").pack(side=tk.LEFT,
                                                                                                         padx=10)
    tk.Radiobutton(frame_opcoes, text="Usar OCR (imagem)", variable=var_metodo, value="ocr").pack(side=tk.LEFT, padx=10)

    text_widget = tk.Text(janela, wrap=tk.WORD, height=30, width=90)
    text_widget.pack(pady=10)

    janela.mainloop()


if __name__ == "__main__":
    criar_interface()
