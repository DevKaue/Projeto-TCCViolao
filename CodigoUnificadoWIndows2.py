import time
import tkinter as tk
from tkinter import filedialog
import re
import os
import platform

# Detectar ambiente
if platform.system() != "Windows":
    import RPi.GPIO as GPIO
    IS_PI = True
else:
    IS_PI = False

from PyPDF2 import PdfReader

# Pinos dos servos (para Raspberry Pi)
SERVO_PINS = [17, 18, 27, 22, 23, 24]  # E, A, D, G, B, e

# Mapeamento dos acordes para cordas pressionadas (1 = pressionada)
ACORDES = {
    "D": [0, 0, 1, 1, 1, 0],
    "A": [0, 1, 1, 1, 0, 0],
    "Bm": [0, 1, 1, 1, 1, 1],
    "E7": [1, 1, 0, 1, 0, 0],
    "F#m": [1, 1, 1, 0, 0, 0]
}

CORDAS = ['E', 'A', 'D', 'G', 'B', 'e']

# Inicialização dos servos
if IS_PI:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SERVO_PINS, GPIO.OUT)
    servos = [GPIO.PWM(pin, 50) for pin in SERVO_PINS]
    for s in servos:
        s.start(7.5)
else:
    class ServoFake:
        def __init__(self, nome): self.nome = nome
        def start(self, duty): print(f"[SIM] {self.nome} start")
        def ChangeDutyCycle(self, duty): print(f"[SIM] {self.nome} duty -> {duty}")
        def stop(self): print(f"[SIM] {self.nome} stop")
    servos = [ServoFake(nome) for nome in CORDAS]
    for s in servos:
        s.start(7.5)

# Tocar acorde e atualizar GUI
def tocar_acorde(acorde, labels):
    if acorde in ACORDES:
        estados = ACORDES[acorde]
        for i, estado in enumerate(estados):
            duty = 5 if estado else 7.5
            if IS_PI:
                servos[i].ChangeDutyCycle(duty)
            else:
                servos[i].ChangeDutyCycle(duty)
            labels[i]['text'] = f"{CORDAS[i]}: {'●' if estado else '○'}"
            labels[i]['bg'] = "green" if estado else "lightgray"
        print(f"[INFO] Tocando acorde: {acorde}")
        time.sleep(1)

# Extrair acordes do PDF, ignorando símbolos
def extrair_acordes_pdf(caminho_pdf):
    acordes = []
    try:
        reader = PdfReader(caminho_pdf)
        for page in reader.pages:
            texto = page.extract_text()
            if texto:
                encontrados = re.findall(r"\b(D|A|Bm|E7|F#m)\b", texto)
                acordes.extend(encontrados)
    except Exception as e:
        print(f"[ERRO] Falha ao ler PDF: {e}")
    return acordes

# Interface
def iniciar_interface():
    root = tk.Tk()
    root.title("Violão Adaptado - Visualização das Cordas")
    root.geometry("300x450")

    titulo = tk.Label(root, text="Cordas do Violão", font=("Arial", 16))
    titulo.pack(pady=10)

    frame = tk.Frame(root)
    frame.pack()

    labels = []
    for c in CORDAS:
        lbl = tk.Label(frame, text=f"{c}: ○", width=20, height=2, bg="lightgray", font=("Arial", 14))
        lbl.pack(pady=4)
        labels.append(lbl)

    status = tk.Label(root, text="Aguardando PDF...", font=("Arial", 12))
    status.pack(pady=10)

    def selecionar_pdf():
        caminho = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if caminho:
            acordes = extrair_acordes_pdf(caminho)
            if acordes:
                status['text'] = f"{len(acordes)} acordes extraídos"
                for acorde in acordes:
                    status['text'] = f"Tocando: {acorde}"
                    tocar_acorde(acorde, labels)
                    root.update()
                    time.sleep(1)
                status['text'] = "Execução finalizada!"
            else:
                status['text'] = "Nenhum acorde identificado."

    btn = tk.Button(root, text="Selecionar PDF", command=selecionar_pdf, font=("Arial", 12))
    btn.pack(pady=10)

    def ao_fechar():
        if IS_PI:
            for servo in servos:
                servo.stop()
            GPIO.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", ao_fechar)
    root.mainloop()

iniciar_interface()
