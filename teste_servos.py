import RPi.GPIO as GPIO
import time
import re

# Pinos dos servos (um para cada corda: E, A, D, G, B, e)
SERVO_PINS = [17, 18, 27, 22, 23, 24]  # Ajuste conforme a fiação da Raspberry Pi

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PINS, GPIO.OUT)

# Criar PWM para cada servo
servos = [GPIO.PWM(pin, 50) for pin in SERVO_PINS]
for servo in servos:
    servo.start(7.5)  # Posição inicial

# Mapeamento de acordes para cordas pressionadas
ACORDES = {
    "D": [0, 0, 1, 1, 1, 0],  # Exemplo: D pressiona as cordas D, G e B
    "A": [0, 1, 1, 1, 0, 0],  # A pressiona as cordas A, D e G
    "Bm": [0, 1, 1, 1, 1, 1],  # Bm toca quase todas
    "E7": [1, 1, 0, 1, 0, 0],  # Exemplo do acorde E7
    "F#m": [1, 1, 1, 0, 0, 0]  # Exemplo do acorde F#m
}

# Função para pressionar as cordas do acorde
def tocar_acorde(acorde):
    if acorde in ACORDES:
        estados = ACORDES[acorde]
        for i, servo in enumerate(servos):
            if estados[i]:  # Se a corda for pressionada
                servo.ChangeDutyCycle(5)  # Ajuste o valor conforme necessário
            else:
                servo.ChangeDutyCycle(7.5)  # Posição inicial (sem pressionar)
        print(f"Tocando acorde: {acorde}")
        time.sleep(1)  # Tempo de permanência no acorde

# Função para processar o arquivo TXT
def processar_arquivo(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as file:
        for linha in file:
            match = re.search(r"\b(D|A|Bm|E7|F#m)\b", linha)
            if match:
                acorde = match.group(0)
                tocar_acorde(acorde)

try:
    processar_arquivo("partitura.txt")  # Substitua pelo caminho do arquivo
finally:
    for servo in servos:
        servo.stop()
    GPIO.cleanup()
