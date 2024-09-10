import mysql.connector
from mysql.connector import Error

def insert_row(usuario, email, clave):
    try:
        # Configura la conexión con la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            port=3307,  # Puerto mapeado en Docker
            user='root',
            password='0000',
            database='talle_api_rest'
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Consulta para insertar una nueva fila
            insert_query = """
            INSERT INTO usuarios (usuario, email, clave)
            VALUES (%s, %s, %s)
            """
            # Valores a insertar
            values = (usuario, email, clave)
            cursor.execute(insert_query, values)

            # Confirmar la transacción
            connection.commit()
            print("Fila insertada correctamente.")

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Llama a la función para insertar una fila de prueba
if __name__ == "__main__":
    insert_row('douglas', 'douglas@ejemplo.com', '0000')
