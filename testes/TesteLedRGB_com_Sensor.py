from machine import Pin
import time

# Sensor PIR
pir = Pin(0, Pin.IN)  # GP0 = pino físico 1

# LED RGB (ânodo comum)
red = Pin(10, Pin.OUT, value=1)
green = Pin(12, Pin.OUT, value=1)
blue = Pin(11, Pin.OUT, value=1)

# Estado do sistema
camera_on = True
last_motion_time = time.time()

# Definir cores
def set_color(r, g, b):
    red.value(r)
    green.value(g)
    blue.value(b)

def standby():
    set_color(1, 0, 0)  # amarelo: vermelho + verde ON

def gravar():
    set_color(1, 0, 1)  # verde ON

def apagar():
    set_color(1, 1, 1)  # tudo OFF

print("Sensor PIR pronto. A aguardar movimento...")

while True:
    tempo_desde_ultimo_mov = time.time() - last_motion_time

    if camera_on:
        if pir.value():
            print("Movimento detetado! A gravar...")
            last_motion_time = time.time()
            gravar()
        elif tempo_desde_ultimo_mov > 30:
            print("Sem movimento por 1 minuto. A desligar.")
            camera_on = False
            apagar()
        elif tempo_desde_ultimo_mov > 5:
            standby()
    else:
        apagar()

    time.sleep(0.2)
