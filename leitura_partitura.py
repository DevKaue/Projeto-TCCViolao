import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from pdf2image import convert_from_path

def selecionar_pdf():
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione uma partitura em PDF",
        filetypes=(("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*"))
    )
    if caminho_arquivo:
        exibir_partitura(caminho_arquivo)

# Função para converter o PDF em imagens e exibi-las
def exibir_partitura(caminho_pdf):
    try:
        # Converte o PDF em imagens
        paginas = convert_from_path(caminho_pdf, dpi=150)  # Ajuste o DPI conforme necessário
        imagens_tk = []
        
        # Converte cada página para formato compatível com Tkinter
        for pagina in paginas:
            imagem = ImageTk.PhotoImage(pagina)
            imagens_tk.append(imagem)

        # Exibe as páginas em sequência
        if imagens_tk:
            exibir_imagem(imagens_tk)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao processar o PDF: {e}")

# Função para exibir imagens na interface gráfica
def exibir_imagem(imagens_tk):
    global imagem_atual, imagens
    imagens = imagens_tk
    imagem_atual = 0  # Começa na primeira página
    atualizar_imagem()

# Função para atualizar a imagem exibida
def atualizar_imagem():
    global imagem_atual, imagens
    if 0 <= imagem_atual < len(imagens):
        canvas.itemconfig(imagem_canvas, image=imagens[imagem_atual])
        pagina_label.config(text=f"Página {imagem_atual + 1} de {len(imagens)}")

# Funções para navegação
def proxima_pagina():
    global imagem_atual
    if imagem_atual < len(imagens) - 1:
        imagem_atual += 1
        atualizar_imagem()

def pagina_anterior():
    global imagem_atual
    if imagem_atual > 0:
        imagem_atual -= 1
        atualizar_imagem()

# Configuração da janela principal
janela = tk.Tk()
janela.title("Leitor de Partituras")
janela.geometry("1000x1000")

# Botão para selecionar arquivo PDF
botao_selecionar = tk.Button(janela, text="Selecionar Partitura", command=selecionar_pdf)
botao_selecionar.pack(pady=10)

# Área para exibição da partitura
canvas = tk.Canvas(janela, width=1000, height=1000)
canvas.pack()

# Espaço para exibir a imagem no canvas
imagem_canvas = canvas.create_image(0, 0, anchor=tk.NW)

# Controles de navegação
controles_frame = tk.Frame(janela)
controles_frame.pack(pady=10)

botao_anterior = tk.Button(controles_frame, text="Anterior", command=pagina_anterior)
botao_anterior.pack(side=tk.LEFT, padx=10)

pagina_label = tk.Label(controles_frame, text="Página 0 de 0")
pagina_label.pack(side=tk.LEFT, padx=10)

botao_proximo = tk.Button(controles_frame, text="Próximo", command=proxima_pagina)
botao_proximo.pack(side=tk.LEFT, padx=10)

# Iniciar a interface
janela.mainloop()

