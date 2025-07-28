import time
import tkinter as tk
from tkinter import filedialog
import os
import platform

# Detectar sistema
if platform.system() != "Windows" and "raspberrypi" in platform.uname().node.lower():
    import RPi.GPIO as GPIO
    IS_PI = True
else:
    IS_PI = False

# Pinos dos servos (para Raspberry Pi)
SERVO_PINS = [17, 18, 27, 22, 23, 24]  # E, A, D, G, B, e

# Mapeamento dos acordes para cordas pressionadas (1 = pressionada)
ACORDES = {
    "G":   [1, 0, 0, 0, 1, 1],
    "D":   [0, 0, 1, 1, 1, 0],
    "A":   [0, 1, 1, 1, 0, 0],
    "C":   [0, 1, 0, 2, 3, 0],
    "Em":  [1, 1, 0, 0, 0, 0],
    "Am":  [0, 1, 2, 2, 1, 0],
    "F":   [1, 3, 3, 2, 1, 1],
    "Bm":  [0, 1, 1, 1, 1, 1],
    "E7":  [1, 1, 0, 1, 0, 0],
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
        def start(self, duty): print(f"[SIM] {self.nome} iniciado")
        def ChangeDutyCycle(self, duty): print(f"[SIM] {self.nome}: {'●' if duty == 5 else '○'}")
        def stop(self): print(f"[SIM] {self.nome} parado")
    servos = [ServoFake(nome) for nome in CORDAS]
    for s in servos:
        s.start(7.5)

# Tocar acorde
def tocar_acorde(acorde, labels):
    acorde = acorde.strip()
    if acorde in ACORDES:
        estados = ACORDES[acorde]
        for i, estado in enumerate(estados):
            duty = 5 if estado else 7.5
            servos[i].ChangeDutyCycle(duty)
            labels[i]['text'] = f"{CORDAS[i]}: {'●' if estado else '○'}"
            labels[i]['bg'] = "green" if estado else "lightgray"
        print(f"[INFO] Tocando acorde: {acorde}")
        time.sleep(1)
    else:
        print(f"[AVISO] Acorde '{acorde}' não reconhecido")

# Extrair acordes de arquivo .txt
def extrair_acordes_txt(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()
            return texto.split()
    except Exception as e:
        print(f"[ERRO] Falha ao ler arquivo: {e}")
        return []

# Interface Tkinter
def iniciar_interface():
    root = tk.Tk()
    root.title("Violão Adaptado")
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

    status = tk.Label(root, text="Aguardando seleção...", font=("Arial", 12))
    status.pack(pady=10)

    def selecionar_arquivo():
        caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if caminho:
            acordes = extrair_acordes_txt(caminho)
            if acordes:
                status['text'] = f"{len(acordes)} acordes extraídos"
                for acorde in acordes:
                    status['text'] = f"Tocando: {acorde}"
                    tocar_acorde(acorde, labels)
                    root.update()
                    time.sleep(0.5)
                status['text'] = "Execução finalizada!"
            else:
                status['text'] = "Nenhum acorde encontrado."

    btn = tk.Button(root, text="Selecionar Arquivo .txt", command=selecionar_arquivo, font=("Arial", 12))
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