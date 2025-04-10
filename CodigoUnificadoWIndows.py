import time
import re
import tkinter as tk
from tkinter import ttk, filedialog
import PyPDF2

# ==== SIMULAÇÃO DO GPIO PARA TESTE NO WINDOWS ====
class ServoSimulado:
    def __init__(self, nome):
        self.nome = nome
        self.duty = 7.5

    def start(self, duty):
        print(f"[SIM] Servo {self.nome} iniciado com duty {duty}")

    def ChangeDutyCycle(self, duty):
        self.duty = duty
        print(f"[SIM] Servo {self.nome} mudou para duty {duty}")

    def stop(self):
        print(f"[SIM] Servo {self.nome} parado")

# ==== Configuração ====
CORDAS = ['E', 'A', 'D', 'G', 'B', 'e']
servos = [ServoSimulado(nome) for nome in CORDAS]
for servo in servos:
    servo.start(7.5)

# ==== Acordes ====
ACORDES = {
    "D": [0, 0, 1, 1, 1, 0],
    "A": [0, 1, 1, 1, 0, 0],
    "Bm": [0, 1, 1, 1, 1, 1],
    "E7": [1, 1, 0, 1, 0, 0],
    "F#m": [1, 1, 1, 0, 0, 0]
}

# ==== Tocar acorde ====
def tocar_acorde(acorde, status_labels):
    if acorde in ACORDES:
        estados = ACORDES[acorde]
        for i, servo in enumerate(servos):
            if estados[i]:
                servo.ChangeDutyCycle(5)
                status_labels[i]['text'] = f"{CORDAS[i]}: ●"
                status_labels[i]['foreground'] = "green"
            else:
                servo.ChangeDutyCycle(7.5)
                status_labels[i]['text'] = f"{CORDAS[i]}: ○"
                status_labels[i]['foreground'] = "black"
        status_label['text'] = f"Tocando acorde: {acorde}"
        time.sleep(1)
    else:
        status_label['text'] = f"Acorde não reconhecido: {acorde}"

# ==== Extrair acordes de PDF ====
def extrair_acordes_pdf(caminho_pdf):
    acordes = []
    try:
        with open(caminho_pdf, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for pagina in reader.pages:
                texto = pagina.extract_text()
                matches = re.findall(r"\b(D|A|Bm|E7|F#m)\b", texto)
                acordes.extend(matches)
        return acordes
    except Exception as e:
        print(f"Erro ao ler PDF: {str(e)}")
        return []

# ==== Processar sequência de acordes extraídos ====
def processar_acordes(acordes, status_labels):
    for acorde in acordes:
        tocar_acorde(acorde, status_labels)
    status_label['text'] = "Fim da execução."

# ==== Interface gráfica ====
def iniciar_interface():
    def selecionar_pdf():
        caminho = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if caminho:
            acordes = extrair_acordes_pdf(caminho)
            if acordes:
                status_label['text'] = "Acordes extraídos! Iniciando..."
                root.after(500, lambda: processar_acordes(acordes, corda_labels))
            else:
                status_label['text'] = "Nenhum acorde encontrado."

    global root, status_label, corda_labels
    root = tk.Tk()
    root.title("Violão Automático - Leitura de PDF")
    root.geometry("300x400")

    title = ttk.Label(root, text="Estado das Cordas", font=("Arial", 16))
    title.pack(pady=10)

    frame = ttk.Frame(root)
    frame.pack(pady=10)

    corda_labels = []
    for corda in CORDAS:
        label = ttk.Label(frame, text=f"{corda}: ○", font=("Arial", 14))
        label.pack()
        corda_labels.append(label)

    status_label = ttk.Label(root, text="Selecione um PDF com acordes", font=("Arial", 12))
    status_label.pack(pady=10)

    btn = ttk.Button(root, text="Selecionar PDF e Tocar", command=selecionar_pdf)
    btn.pack(pady=10)

    root.mainloop()

# ==== Executar interface ====
try:
    iniciar_interface()
finally:
    for servo in servos:
        servo.stop()
