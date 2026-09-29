from machine import Pin
import time

# GPIOs reais que estás a usar
RED_PIN = 10   # GP10 = Pino físico 14DDD
GREEN_PIN = 12 # GP12 = Pino físico 16
BLUE_PIN = 11  # GP11 = Pino físico 15

# Inicializar como saída e desligados (1 = OFF para ânodo comum)
red = Pin(RED_PIN, Pin.OUT, value=1)
green = Pin(GREEN_PIN, Pin.OUT, value=1)
blue = Pin(BLUE_PIN, Pin.OUT, value=1)

# Espera para confirmar LED apagado
time.sleep(1)

# Acende vermelho por 3 segundos
print("Vermelho")
red.value(0)
time.sleep(3)
red.value(1)

# Acende verde por 3 segundos
print("Verde")
green.value(0)
time.sleep(3)
green.value(1)

# Acende azul por 3 segundos
print("Azul")
blue.value(0)
time.sleep(3)
blue.value(1)

# Confirma que tudo ficou apagado
print("LED apagado")

