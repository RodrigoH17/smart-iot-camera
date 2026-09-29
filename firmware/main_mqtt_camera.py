# Importa módulos necessários para controlo de hardware, tempo, MQTT e Wi-Fi
from machine import Pin, ADC, PWM               # Controlos GPIO e sensores
import time                                      # Para delays temporais
from umqtt.simple import MQTTClient             # Cliente MQTT para comunicação
import provisioning                              # Módulo de configuração Wi-Fi (local)
import os

# ======= Tenta ligar ao Wi-Fi =======
# Utiliza função de provisioning que tenta ligar a redes conhecidas a partir de config.json
if not provisioning.ligar_wifi_de_config():
    print("Nenhuma rede funcionou. A iniciar modo de configuração...")
    provisioning.iniciar_portal_configuracao()  # Ativa o portal cativo para configuração manual
    raise SystemExit()                           # Encerra o programa caso não haja Wi-Fi

# ======= CONFIGURAÇÃO MQTT =======
MQTT_BROKER = "192.168.141.150"  # Endereço IP do broker local
MQTT_USER = "teste"              # Nome de utilizador
MQTT_PASS = "123"                # Palavra-passe
CLIENT_ID = "camera_pico"        # ID do dispositivo na rede MQTT

# Definição dos tópicos utilizados
TOPIC_CONTROL = b"camera/control"     # Recebe comando para ligar/desligar câmara
TOPIC_STATUS = b"camera/status"       # Publica estado atual (ON/OFF)
TOPIC_MODO = b"camera/modo"           # Publica modo atual (DIURNO/NOTURNO)
TOPIC_GRAVAR = b"camera/gravar"       # Notifica movimento para gravação
TOPIC_SOM = b"camera/som"             # Liga/desliga som
TOPIC_ERRO = b"camera/erro"           # Publica erros/crashs inesperados

# ======= INICIALIZAÇÃO DE COMPONENTES =======
red = Pin(10, Pin.OUT, value=1)     # LED RGB - Vermelho
green = Pin(12, Pin.OUT, value=1)   # LED RGB - Verde
blue = Pin(11, Pin.OUT, value=1)    # LED RGB - Azul
pir = Pin(0, Pin.IN)                # Sensor PIR para detetar movimento
ldr = ADC(Pin(28))                  # Sensor LDR para luz ambiente
led_modo = Pin(14, Pin.OUT)         # LED indicador de modo (diurno/noturno)
buzzer = PWM(Pin(17))               # Buzzer controlado por PWM
buzzer.duty_u16(0)                  # Desliga o buzzer
botao_som = Pin(15, Pin.IN, Pin.PULL_UP)  # Botão para controlo do som com pull-up interno

# ======= VARIÁVEIS DE ESTADO =======
camera_on = False          # Indica se a câmara está ligada
som_ativo = True           # Estado do som (ativo ou mutado)
botao_ativo = False        # Estado do botão (pressionado ou não)
last_motion = time.time()  # Guarda o timestamp do último movimento detetado

# ======= FUNÇÕES AUXILIARES =======

def set_color(r, g, b):
    # Define a cor do LED RGB
    red.value(r)
    green.value(g)
    blue.value(b)

def standby():
    # Led azul
    set_color(1, 0, 0)

def gravar():
  # LED verde
    set_color(1, 0, 1)

def apagar():
    # LED desligado
    set_color(1, 1, 1)

def som_standby():
    # Som curto (beep) durante standby, se som estiver ativo
    if som_ativo:
        buzzer.freq(400)
        buzzer.duty_u16(30000)
        time.sleep(0.1)
        buzzer.duty_u16(0)

def som_gravar():
    # Dois beeps durante a gravação, quando movimento é detetado
    if som_ativo:
        for _ in range(2):
            buzzer.freq(1000)
            buzzer.duty_u16(20000)
            time.sleep(0.1)
            buzzer.duty_u16(0)
            time.sleep(0.05)

def is_noite():
    # Verifica se é de noite com base no valor do sensor LDR
    valor = ldr.read_u16()
    print("LDR:", valor)
    return valor < 32927  # Valor do ldr calibrado para diferenciar dia/noite

# ======= CALLBACK MQTT - processamento de mensagens recebidas =======
def sub_cb(topic, msg):
    global camera_on, som_ativo
    print(f"[MQTT] {topic}: {msg}")

    if topic == TOPIC_CONTROL:
        if msg == b"ON":
            # Liga a câmara
            camera_on = True
            standby()
            client.publish(TOPIC_STATUS, b"ON", retain=True)
        elif msg == b"OFF":
            # Desliga a câmara
            camera_on = False
            apagar()
            led_modo.value(0)
            buzzer.duty_u16(0)
            client.publish(TOPIC_STATUS, b"OFF", retain=True)

    elif topic == TOPIC_SOM:
        # Atualiza estado do som
        som_ativo = msg == b"ON"
        print("Som ativo:", som_ativo)

# ======= CONFIGURAÇÃO DO CLIENTE MQTT =======
try:
    client = MQTTClient(
        CLIENT_ID,
        MQTT_BROKER,
        user=MQTT_USER,
        password=MQTT_PASS,
        keepalive=60
    )
    client.set_callback(sub_cb)  # Define função callback para mensagens recebidas
    client.set_last_will(TOPIC_ERRO, b"ERRO: Corte de Energia Inesperado, Camara Desligada!", retain=False)
    client.connect()             # Liga-se ao broker
    client.subscribe(TOPIC_CONTROL)
    client.subscribe(TOPIC_SOM)
    print("Ligado ao broker MQTT")
except OSError as e:
    print("Erro ao ligar ao broker MQTT:", e)
    provisioning.iniciar_portal_configuracao()
    raise SystemExit()

# ======= LOOP PRINCIPAL =======
print("Sistema pronto.")
while True:
    try:
        client.check_msg()  # Verifica se chegaram novas mensagens MQTT

        # Verifica se o botão do som foi pressionado
        if not botao_som.value() and not botao_ativo:
            botao_ativo = True
            som_ativo = not som_ativo  # Altera estado do som
            estado = b"ON" if som_ativo else b"OFF"
            client.publish(TOPIC_SOM, estado, retain=True)
            print("Botão som:", estado)
            time.sleep(0.3) 
        elif botao_som.value():
            botao_ativo = False

        # Se a câmara estiver ligada, verificar sensores
        if camera_on:
            if is_noite():
                led_modo.value(1)
                client.publish(TOPIC_MODO, b"NOTURNO", retain=True) # Modo noturno
            else:
                led_modo.value(0)
                client.publish(TOPIC_MODO, b"DIURNO", retain=True) # Modo diurno

            if pir.value():  # Movimento detetado
                print("Movimento detetado.")
                client.publish(TOPIC_GRAVAR, b"1")
                gravar()
                som_gravar()
                last_motion = time.time()
            elif time.time() - last_motion > 5:
                standby()
                som_standby()
        else:
            apagar()
            led_modo.value(0)
            buzzer.duty_u16(0)

        time.sleep(0.2)  # Pequeno atraso para não sobrecarregar CPU

    except Exception as e:
        print("Erro no loop principal:", e)
        time.sleep(2)  # Aguarda antes de tentar novamente