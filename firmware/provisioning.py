# Importa módulos necessários
import network            # Para lidar com Wi-Fi
import time               # Para atrasos
import json               # Para ler/gravar ficheiros JSON
from microdot import Microdot, Response  # Micro servidor web

# Nome do ficheiro de configuração onde se guarda SSID e password
CONFIG_FILE = 'config.json'

# Define o tipo de conteúdo por defeito como HTML nas respostas HTTP
Response.default_content_type = 'text/html'

# Microdot
app = Microdot()

# Função que tenta ligar ao Wi-Fi com base no ficheiro config.json
def ligar_wifi_de_config():
    try:
        # Tenta abrir e ler o ficheiro JSON com SSID e password
        with open(CONFIG_FILE) as f:
            dados = json.load(f)
            ssid = dados['ssid']           # Nome da rede Wi-Fi
            pwd = dados['password']       # Password da rede
    except:
        # Erro se ficheiro estiver em falta ou com formato incorreto
        print("Sem config.json ou mal formatado.")
        return False

    # Cria interface Wi-Fi em modo cliente (station)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, pwd)

    print(f"A tentar ligar a: {ssid}")

    # Tenta ligar durante 10 segundos
    for _ in range(10):
        if wlan.isconnected():
            print("Ligado ao Wi-Fi:", wlan.ifconfig())
            return True
        time.sleep(1)

    print("Falha ao ligar ao Wi-Fi.")
    return False

# Endpoint GET para mostrar o formulário de configuração Wi-Fi
@app.route('/', methods=['GET'])
def formulario(request):
    return '''
        <html><body>
        <h3>Configurar Wi-Fi</h3>
        <form method="POST">
          SSID: <input name="ssid"><br>
          Password: <input name="password" type="password"><br>
          <button type="submit">Guardar</button>
        </form>
        </body></html>
    '''

# Endpoint POST para guardar as credenciais no ficheiro config.json
@app.route('/', methods=['POST'])
def guardar_config(request):
    ssid = request.form.get('ssid')               # Lê o SSID do formulário
    password = request.form.get('password')       # Lê a password

    # Guarda os dados no ficheiro JSON
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'ssid': ssid, 'password': password}, f)

    # Informa o utilizador que a gravação foi feita
    return '<h3>Guardado! Reinicia o dispositivo.</h3>'

# Função que ativa o modo Access Point e inicia o servidor Microdot
# Permite ao utilizador configurar o Wi-Fi pelo navegador

def iniciar_portal_configuracao():
    ap = network.WLAN(network.AP_IF)         # Ativa modo Access Point
    ap.active(True)
    ap.config(essid='PicoConfig')            # Nome da rede aberta

    print('Portal ativo em http://192.168.4.1')
    app.run(host='0.0.0.0', port=80)         # Inicia o servidor web na porta 80