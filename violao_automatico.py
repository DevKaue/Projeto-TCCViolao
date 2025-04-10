import time
import tkinter as tk
from tkinter import filedialog
import re
import os
import platform
from PyPDF2 import PdfReader

# # Detecta o ambiente
# IS_PI = platform.system() != "Windows"
# if IS_PI:
#     import RPi.GPIO as GPIO

# Detectar ambiente
if platform.system() != "Windows":
    import RPi.GPIO as GPIO
    IS_PI = True
else:
    IS_PI = False

# Pinos dos servos (ordem: E, A, D, G, B, e)
SERVO_PINS = [17, 18, 27, 22, 23, 24]
CORDAS = ['E', 'A', 'D', 'G', 'B', 'e']  # Corda 6 até 1

# Mapeamento de acordes para cordas pressionadas
ACORDES = {
    "D":   [0, 0, 2, 3, 2, -1],
    "A":   [0, 0, 2, 2, 2, -1],
    "Bm":  [2, 2, 4, 4, 3, 2],
    "E7":  [0, 2, 0, 1, 0, 0],
    "F#m": [2, 4, 4, 2, 2, 2]
}

# Inicializa GPIO ou simulação
if IS_PI:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PINS, GPIO.OUT)
    servos = [GPIO.PWM(pin, 50) for pin in SERVO_PINS]
    for s in servos:
        s.start(7.5)
else:
    class ServoSimulado:
        def __init__(self, nome): self.nome = nome
        def start(self, duty): print(f"[SIM] {self.nome} start")
        def ChangeDutyCycle(self, duty): print(f"[SIM] {self.nome} → duty {duty}")
        def stop(self): print(f"[SIM] {self.nome} stop")
    servos = [ServoSimulado(c) for c in CORDAS]
    for s in servos:
        s.start(7.5)

# Conversão simplificada de casa para duty cycle (ajuste conforme servo)
def casa_para_duty(casa):
    casa = int(casa)
    base = 5.0
    fator = 0.3  # ajuste fino para distância entre casas
    return base + (casa * fator)

# Pressiona uma corda em uma casa específica
def pressionar_corda(corda_index, casa, label):
    duty = casa_para_duty(casa)
    servos[corda_index].ChangeDutyCycle(duty)
    label['text'] = f"{CORDAS[corda_index]}: Casa {casa}"
    label['bg'] = "green"
    print(f"[INFO] Corda {CORDAS[corda_index]} → Casa {casa}")

# Solta todas as cordas
def soltar_todas(labels):
    for i, servo in enumerate(servos):
        servo.ChangeDutyCycle(7.5)
        labels[i]['text'] = f"{CORDAS[i]}: Solta"
        labels[i]['bg'] = "lightgray"

# Tocar acorde inteiro
def tocar_acorde(acorde, labels):
    if acorde in ACORDES:
        casas = ACORDES[acorde]
        for i, casa in enumerate(casas):
            if casa >= 0:
                pressionar_corda(i, casa, labels)
            else:
                labels[i]['text'] = f"{CORDAS[i]}: Muda"
                labels[i]['bg'] = "gray"
        time.sleep(1)

# Extrai acordes e tablatura do PDF
def extrair_eventos_pdf(caminho_pdf):
    reader = PdfReader(caminho_pdf)
    eventos = []
    tab_blocos = {}
    linhas_tab = {"e": "", "B": "", "G": "", "D": "", "A": "", "E": ""}

    for page in reader.pages:
        texto = page.extract_text()
        if not texto:
            continue

        linhas = texto.split("\n")
        for linha in linhas:
            # Detectar acordes
            acordes = re.findall(r"\b(D|A|Bm|E7|F#m)\b", linha)
            eventos.extend([("acorde", acorde) for acorde in acordes])

            # Detectar linhas de tablatura
            tab_match = re.match(r"^([eBGDAE])\|([-0-9| \t]+)", linha)
            if tab_match:
                corda = tab_match.group(1)
                dados = tab_match.group(2)
                linhas_tab[corda] = dados

                # Se todas as 6 cordas foram encontradas
                if all(linhas_tab[c] for c in ["e", "B", "G", "D", "A", "E"]):
                    # Quebrar os valores por posição
                    max_len = max(len(l) for l in linhas_tab.values())
                    for i in range(0, max_len, 2):
                        frame = {}
                        for j, c in enumerate(["E", "A", "D", "G", "B", "e"]):
                            try:
                                val = linhas_tab[c][i:i+2].strip("-| \n")
                                frame[j] = int(val) if val.isdigit() else -1
                            except:
                                frame[j] = -1
                        eventos.append(("tab", frame))
                    linhas_tab = {k: "" for k in linhas_tab}  # reset
    return eventos

# GUI
def iniciar_interface():
    root = tk.Tk()
    root.title("Violão Automático - Visualização")
    root.geometry("350x500")

    titulo = tk.Label(root, text="Cordas do Violão", font=("Arial", 16))
    titulo.pack(pady=10)

    frame = tk.Frame(root)
    frame.pack()

    labels = []
    for c in CORDAS:
        lbl = tk.Label(frame, text=f"{c}: Solta", width=25, height=2, bg="lightgray", font=("Arial", 14))
        lbl.pack(pady=4)
        labels.append(lbl)

    status = tk.Label(root, text="Selecione um PDF...", font=("Arial", 12))
    status.pack(pady=10)

    def executar_eventos(eventos):
        for tipo, dado in eventos:
            if tipo == "acorde":
                status['text'] = f"Tocando acorde: {dado}"
                tocar_acorde(dado, labels)
            elif tipo == "tab":
                status['text'] = f"Tablatura: {dado}"
                for i in range(6):
                    casa = dado.get(i, -1)
                    if casa >= 0:
                        pressionar_corda(i, casa, labels)
                    else:
                        labels[i]['text'] = f"{CORDAS[i]}: Solta"
                        labels[i]['bg'] = "lightgray"
                time.sleep(1)
            soltar_todas(labels)
        status['text'] = "Finalizado."

    def selecionar_pdf():
        caminho = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if caminho:
            status['text'] = "Processando..."
            eventos = extrair_eventos_pdf(caminho)
            executar_eventos(eventos)

    btn = tk.Button(root, text="Selecionar PDF", command=selecionar_pdf, font=("Arial", 12))
    btn.pack(pady=10)

    def ao_fechar():
        if IS_PI:
            for s in servos:
                s.stop()
            GPIO.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", ao_fechar)
    root.mainloop()

iniciar_interface()
