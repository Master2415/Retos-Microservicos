# Usa la imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000 para la aplicación Flask
EXPOSE 5000

# Define el comando por defecto
CMD ["python", "Reto2.py"]
