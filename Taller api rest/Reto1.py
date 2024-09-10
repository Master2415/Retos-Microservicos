from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt
import jwt
import datetime
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'  # Ruta al archivo swagger.yaml
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Gestión de Usuarios"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'talle_api_rest'
app.config['SECRET_KEY'] = 'your_secret_key'  # Clave secreta para JWT

mysql = MySQL(app)

# 1. Registro de usuario
@app.route('/usuarios/', methods=['POST'])
def register_user():
    data = request.get_json()
    usuario = data.get('usuario')
    email = data.get('email')
    clave = data.get('clave')

    if not usuario or not email or not clave:
        return jsonify({'message': 'Datos incompletos'}), 400

    # Encriptar la clave
    hashed_clave = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    cur = mysql.connection.cursor()
    # Verificar si el email ya está registrado
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        return jsonify({'message': 'Email ya registrado'}), 409

    cur.execute("INSERT INTO usuarios (usuario, email, clave) VALUES (%s, %s, %s)",
                (usuario, email, hashed_clave))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Usuario registrado exitosamente'}), 201

# 2. Obtener lista de usuarios
@app.route('/usuarios', methods=['GET'])
def get_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, usuario, email FROM usuarios")
    users = cur.fetchall()
    cur.close()

    if not users:
        return jsonify({'message': 'No hay usuarios registrados'}), 404

    return jsonify(users), 200

# 3. Obtener un usuario por ID
@app.route('/usuarios/<int:id>', methods=['GET'])
def get_user_by_id(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, usuario, email FROM usuarios WHERE id = %s", (id,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    return jsonify(user), 200

# 4. Actualizar usuario
@app.route('/usuarios/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    usuario = data.get('usuario')
    email = data.get('email')
    clave = data.get('clave')

    cur = mysql.connection.cursor()

    # Verificar si el usuario existe
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cur.fetchone()

    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    if email:
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND id != %s", (email, id))
        existing_user = cur.fetchone()
        if existing_user:
            return jsonify({'message': 'Email ya registrado'}), 409

    update_data = {
        'usuario': usuario or user[1],
        'email': email or user[2],
        'clave': bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt()) if clave else user[3]
    }

    cur.execute("""
        UPDATE usuarios
        SET usuario = %s, email = %s, clave = %s
        WHERE id = %s
    """, (update_data['usuario'], update_data['email'], update_data['clave'], id))

    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Usuario actualizado exitosamente'}), 200

# 5. Eliminar usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_user(id):
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    user = cur.fetchone()

    if not user:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Usuario eliminado exitosamente'}), 204

# 6. Login de usuario
@app.route('/usuarios/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    clave = data.get('clave')

    if not email or not clave:
        return jsonify({'message': 'Datos incompletos'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if not user or not bcrypt.checkpw(clave.encode('utf-8'), user[3].encode('utf-8')):
        return jsonify({'message': 'Credenciales incorrectas'}), 401

    token = jwt.encode({
        'id': user[0],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'token': token}), 200

# 7. Recuperación de clave
@app.route('/usuarios/recover-password', methods=['POST'])
def recover_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': 'Email es obligatorio'}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({'message': 'Email no registrado'}), 404

    # Aquí enviarías un correo al usuario con instrucciones para recuperar la clave
    # Este es un ejemplo simple, en la realidad usarías un servicio de correo electrónico
    return jsonify({'message': f'Instrucciones para recuperar la clave enviadas a {email}'}), 200

if __name__ == '__main__':
    app.run(debug=True)
