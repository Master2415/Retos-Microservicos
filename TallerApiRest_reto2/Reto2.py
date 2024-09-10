from flask import Flask, request, jsonify
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
import os
from flask_swagger_ui import get_swaggerui_blueprint
from functools import wraps
import smtplib  # Para enviar el correo de recuperación de contraseña

app = Flask(__name__)

# Clave secreta para JWT
app.config['SECRET_KEY'] = 'root'

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Gestión de Usuarios"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Configuración de MongoDB
mongo_uri = os.getenv('MONGO_URI', 'mongodb://mongo_container:27017/talle_api_rest')
client = MongoClient(mongo_uri)
db = client.talle_api_rest
users_collection = db.usuarios


# Middleware para requerir token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-tokens')

        if not token:
            return jsonify({'message': 'Token faltante!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users_collection.find_one({"email": data['email']})
            if not current_user:
                raise RuntimeError('Usuario no encontrado')
        except Exception as e:
            return jsonify({'message': 'Token inválido!', 'error': str(e)}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# 1. Registro de usuario
@app.route('/usuarios/', methods=['POST'])
def register_user():
    data = request.get_json()
    usuario = data.get('usuario')
    email = data.get('email')
    clave = data.get('clave')

    if not usuario or not email or not clave:
        return jsonify({'message': 'Datos incompletos'}), 400

    hashed_clave = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt())

    # Verificar si el email ya está registrado
    if users_collection.find_one({"email": email}):
        return jsonify({'message': 'Email ya registrado'}), 409

    user_id = users_collection.insert_one({
        'usuario': usuario,
        'email': email,
        'clave': hashed_clave.decode('utf-8')
    }).inserted_id

    return jsonify({'message': 'Usuario registrado exitosamente', 'id': str(user_id)}), 201

# 2. Obtener lista de usuarios con paginación
@app.route('/usuarios', methods=['GET'])
def get_users():
    try:
        page = int(request.args.get('page', 1))  # Número de página, por defecto 1
        per_page = int(request.args.get('per_page', 10))  # Número de usuarios por página, por defecto 10

        # Validar los parámetros de paginación
        if page < 1 or per_page < 1:
            return jsonify({'message': 'Parámetros de paginación inválidos'}), 400

        # Consultar usuarios con paginación
        users_cursor = users_collection.find({}, {"_id": 0, "usuario": 1, "email": 1}).skip((page - 1) * per_page).limit(per_page)
        users = list(users_cursor)

        if not users:
            return jsonify({'message': 'No hay usuarios registrados'}), 404

        # Calcular el número total de usuarios para la paginación
        total_users = users_collection.count_documents({})
        total_pages = (total_users + per_page - 1) // per_page

        return jsonify({
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'total_users': total_users,
            'users': users
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener la lista de usuarios', 'error': str(e)}), 500



# 3. Obtener un usuario por email (solo el propio usuario puede hacerlo)
@app.route('/usuarios/<string:email>', methods=['GET'])
@token_required
def get_user_by_email(current_user, email):
    if current_user['email'] != email:
        return jsonify({'message': 'No puedes acceder a los datos de otro usuario'}), 403

    user = users_collection.find_one({"email": email}, {"_id": 0, "usuario": 1, "email": 1})
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    return jsonify(user), 200

# 4. Actualizar usuario (solo sobre sus propios datos)
@app.route('/usuarios/<string:email>', methods=['PUT'])
@token_required
def update_user(current_user, email):
    if current_user['email'] != email:
        return jsonify({'message': 'No puedes actualizar los datos de otro usuario'}), 403

    data = request.get_json()
    usuario = data.get('usuario')
    clave = data.get('clave')

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    update_data = {}
    if usuario:
        update_data['usuario'] = usuario
    if clave:
        update_data['clave'] = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    users_collection.update_one({"email": email}, {"$set": update_data})

    return jsonify({'message': 'Usuario actualizado exitosamente'}), 200

# 5. Eliminar usuario (solo sobre su cuenta)
@app.route('/usuarios/<string:email>', methods=['DELETE'])
@token_required
def delete_user(current_user, email):
    if current_user['email'] != email:
        return jsonify({'message': 'No puedes eliminar la cuenta de otro usuario'}), 403

    result = users_collection.delete_one({"email": email})
    if result.deleted_count == 0:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    return jsonify({'message': 'Usuario eliminado exitosamente'}), 204


# 6. Login de usuario
@app.route('/usuarios/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    clave = data.get('clave')

    if not email or not clave:
        return jsonify({'message': 'Datos incompletos'}), 400

    user = users_collection.find_one({"email": email})
    if not user or not bcrypt.checkpw(clave.encode('utf-8'), user['clave'].encode('utf-8')):
        return jsonify({'message': 'Credenciales incorrectas'}), 401

    token = jwt.encode({
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token}), 200


# 7. Recuperar contraseña (envía un email con un enlace para cambiar la clave)
@app.route('/usuarios/recover-password', methods=['POST'])
def recover_password():
    data = request.get_json()
    email = data.get('email')

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({'message': 'Email no registrado'}), 404

    # Simular envío de correo de recuperación
    recovery_link = f"http://127.0.0.1:5000/reset-password/{email}"

    # Aquí podrías usar una librería como smtplib para enviar el correo:
    # smtp = smtplib.SMTP('smtp.example.com', 587)
    # smtp.starttls()
    # smtp.login('your_email@example.com', 'your_password')
    # smtp.sendmail('from@example.com', email, f'Link de recuperación: {recovery_link}')
    # smtp.quit()

    return jsonify({'message': f'Instrucciones enviadas al correo {email}', 'link': recovery_link}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
