from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)

# Clave secreta para firmar el JWT
SECRET_KEY = '0000'

@app.route('/', methods=['GET'])
def home():
    response = {
        "message": "Bienvenido a la aplicación Flask"
    }
    return jsonify(response), 200

@app.route('/saludo', methods=['GET'])
def saludo():
    nombre = request.args.get('nombre')

    if not nombre:
        # Responder con un código de error 400 si no se proporciona el nombre
        response = {
            "message": "Solicitud no válida: El nombre es obligatorio"
        }
        return jsonify(response), 400

    # Responder con un código de estado 200 y un saludo si se proporciona el nombre
    response = {
        "message": f"HELLO {nombre}"
    }
    return jsonify(response), 200

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        response = {
            "message": "Solicitud no válida: El contenido debe ser JSON"
        }
        return jsonify(response), 415

    data = request.get_json()

    # Verificar que se envíen los atributos 'usuario' y 'clave'
    if 'usuario' not in data or 'clave' not in data:
        response = {
            "message": "Solicitud no válida: 'usuario' y 'clave' son obligatorios"
        }
        return jsonify(response), 400

    # Datos del usuario
    usuario = data['usuario']

    # Generar el token JWT
    token = jwt.encode(
        {
            'usuario': usuario,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            'iss': 'ingesis.uniquindio.edu.co'
        },
        SECRET_KEY,
        algorithm='HS256'
    )

    response = {
        "message": "Token generado exitosamente",
        "token": token
    }
    return jsonify(response), 200

# Manejar rutas no encontradas
@app.errorhandler(404)
def recurso_no_encontrado(e):
    response = {
        "message": "Recurso no encontrado"
    }
    return jsonify(response), 404

if __name__ == '__main__':
    # Ejecutar la aplicación en el puerto 80
    app.run(host='0.0.0.0', port=80)
