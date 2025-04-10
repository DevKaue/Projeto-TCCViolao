import RPi.GPIO as GPIO
import time
import re
import PyPDF2
import os

# Pinos dos servos (um para cada corda: E, A, D, G, B, e)
SERVO_PINS = [17, 18, 27, 22, 23, 24]

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PINS, GPIO.OUT)

# Criar PWM para cada servo
servos = [GPIO.PWM(pin, 50) for pin in SERVO_PINS]
for servo in servos:
    servo.start(7.5)

# Mapeamento de acordes para cordas pressionadas
ACORDES = {
    "D":   [0, 0, 1, 1, 1, 0],
    "A":   [0, 1, 1, 1, 0, 0],
    "Bm":  [0, 1, 1, 1, 1, 1],
    "E7":  [1, 1, 0, 1, 0, 0],
    "F#m": [1, 1, 1, 0, 0, 0]
}

# Nomes das cordas (ordem invertida, da aguda para grave)
CORDAS = ['e', 'B', 'G', 'D', 'A', 'E']

# Interface de "monitor"
def exibir_monitor(acorde, estados):
    os.system('clear' if os.name == 'posix' else 'cls')  # Limpa a tela
    print("🎸 MONITOR DE CORDAS\n")
    print(f"Acorde: {acorde}\n")
    for i, estado in enumerate(estados):
        simbolo = '●' if estado else '○'
        print(f"Corda {i+1} ({CORDAS[i]}):    {simbolo}")
    print("\n---")
    time.sleep(2)

# Extrair acordes do PDF
def extrair_acordes_pdf(caminho_pdf):
    acordes_encontrados = []
    with open(caminho_pdf, "rb") as file:
        leitor_pdf = PyPDF2.PdfReader(file)
        for pagina in leitor_pdf.pages:
            texto = pagina.extract_text()
            for acorde in ACORDES.keys():
                if acorde in texto:
                    acordes_encontrados.append(acorde)
    return acordes_encontrados

# Tocar o acorde
def tocar_acorde(acorde):
    if acorde in ACORDES:
        estados = ACORDES[acorde]
        exibir_monitor(acorde, estados)
        for i, servo in enumerate(servos):
            servo.ChangeDutyCycle(5 if estados[i] else 7.5)

# Função principal
def tocar_partitura_pdf(caminho_pdf):
    acordes = extrair_acordes_pdf(caminho_pdf)
    print(f"[INFO] Acordes extraídos da partitura: {acordes}")
    for acorde in acordes:
        tocar_acorde(acorde)

# Caminho do PDF
caminho_pdf = "partitura.pdf"

try:
    tocar_partitura_pdf(caminho_pdf)
finally:
    for servo in servos:
        servo.stop()
    GPIO.cleanup()
