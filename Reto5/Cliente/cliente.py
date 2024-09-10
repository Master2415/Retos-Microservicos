import os  # Importa el módulo os para interactuar con el sistema operativo
import requests  # Importa el módulo requests para hacer solicitudes HTTP
import random  # Importa el módulo random para generar valores aleatorios
import string  # Importa el módulo string para manipular cadenas de texto

# Obtener URLs desde variables de entorno, con valores por defecto si no están definidas
AUTH_URL = os.getenv('AUTH_URL', 'http://localhost:5000/login')  # URL para la autenticación
SALUDO_URL = os.getenv('SALUDO_URL', 'http://localhost:5000/saludo')  # URL para el servicio de saludo

# Generar usuario y clave aleatorios
def generar_usuario_y_clave():
    usuario = ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Genera un nombre de usuario aleatorio de 8 caracteres
    clave = ''.join(random.choices(string.ascii_letters + string.digits, k=12))  # Genera una clave aleatoria de 12 caracteres
    return usuario, clave  # Devuelve el nombre de usuario y la clave generados

# Obtener token
def obtener_token(usuario, clave):
    response = requests.post(AUTH_URL, json={'usuario': usuario, 'clave': clave})  # Envía una solicitud POST para autenticarse y obtener un token
    response.raise_for_status()  # Lanza una excepción si la solicitud devuelve un error HTTP
    data = response.json()  # Convierte la respuesta en formato JSON
    return data['token']  # Devuelve el token extraído de la respuesta

# Invocar servicio de saludo
def invocar_saludo(token):
    headers = {'Authorization': f'Bearer {token}'}  # Configura el encabezado de autorización con el token JWT
    response = requests.get(SALUDO_URL, headers=headers)  # Envía una solicitud GET al servicio de saludo con el token en el encabezado
    response.raise_for_status()  # Lanza una excepción si la solicitud devuelve un error HTTP
    print(response.json())  # Imprime la respuesta en formato JSON

def main():
    usuario, clave = generar_usuario_y_clave()  # Genera un nombre de usuario y clave aleatorios
    token = obtener_token(usuario, clave)  # Obtiene un token JWT usando el usuario y clave generados
    invocar_saludo(token)  # Llama al servicio de saludo con el token obtenido

if __name__ == '__main__':
    main()  # Ejecuta la función main si el script es ejecutado directamente
