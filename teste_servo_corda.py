import RPi.GPIO as GPIO
import time

# Configuração do pino do servo (simulando uma corda)
SERVO_PIN = 18  # Altere conforme sua conexão

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Criar o controle PWM
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM (frequência padrão para servos)
pwm.start(7.5)  # Posição inicial (corda não pressionada)

# Simular a ação de pressionar e soltar uma corda
def pressionar_corda():
    print("Pressionando a corda...")
    pwm.ChangeDutyCycle(5)  # Ajuste conforme necessário para pressionar a corda
    time.sleep(1)  # Tempo de pressionamento

def soltar_corda():
    print("Soltando a corda...")
    pwm.ChangeDutyCycle(7.5)  # Posição inicial (sem pressionar)
    time.sleep(1)

try:
    while True:
        pressionar_corda()  # Simula pressionar a corda
        time.sleep(2)
        soltar_corda()  # Simula soltar a corda
        time.sleep(2)
except KeyboardInterrupt:
    print("\nEncerrando...")
    pwm.stop()
    GPIO.cleanup()
