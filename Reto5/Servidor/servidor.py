from flask import Flask, request, jsonify  # Importa las clases y funciones necesarias desde el módulo Flask
import jwt  # Importa el módulo jwt para manejar JSON Web Tokens
import datetime  # Importa el módulo datetime para trabajar con fechas y horas

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

SECRET_KEY = '0000'  # Define una clave secreta para firmar los JSON Web Tokens

@app.route('/', methods=['GET'])  # Define una ruta para la raíz de la aplicación que acepta solicitudes GET
def home():
    response = {
        "message": "Bienvenido a la aplicación Flask"  # Mensaje de bienvenida
    }
    return jsonify(response), 200  # Convierte el diccionario a JSON y devuelve la respuesta con código 200 (OK)

@app.route('/saludo', methods=['GET'])  # Define una ruta para /saludo que acepta solicitudes GET
def saludo():
    nombre = request.args.get('nombre', 'Douglas')  # Obtiene el parámetro 'nombre' de la solicitud, usa 'Mundo' como valor por defecto
    response = {
        "message": f"HELLO {nombre}"  # Mensaje de saludo personalizado
    }
    return jsonify(response), 200  # Convierte el diccionario a JSON y devuelve la respuesta con código 200 (OK)

@app.route('/login', methods=['POST'])  # Define una ruta para /login que acepta solicitudes POST
def login():
    data = request.get_json()  # Obtiene los datos JSON de la solicitud
    usuario = data.get('usuario', 'default_user')  # Extrae el valor del campo 'usuario', usa 'default_user' si no está presente

    # Genera el token JWT
    token = jwt.encode(
        {
            'usuario': usuario,  # Incluye el nombre de usuario en el token
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Establece la expiración del token
            'iss': 'ingesis.uniquindio.edu.co'  # Establece el emisor del token
        },
        SECRET_KEY,  # Usa la clave secreta para firmar el token
        algorithm='HS256'  # Especifica el algoritmo de firma
    )

    response = {
        "message": "Token generado exitosamente",  # Mensaje de éxito
        "token": token  # Token JWT generado
    }
    return jsonify(response), 200  # Convierte el diccionario a JSON y devuelve la respuesta con código 200 (OK)

@app.errorhandler(404)  # Define un manejador de errores para el código 404 (Recurso no encontrado)
def recurso_no_encontrado(e):
    response = {
        "message": "Recurso no encontrado"  # Mensaje de error para recurso no encontrado
    }
    return jsonify(response), 404  # Convierte el diccionario a JSON y devuelve la respuesta con código 404 (Recurso no encontrado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)  # Inicia el servidor Flask en todas las interfaces de red en el puerto 80
