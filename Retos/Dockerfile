# Usar una imagen base de Python
FROM python:3.8-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo requirements.txt y el código fuente al contenedor
COPY requirements.txt /app/
COPY . /app

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 80 para que el contenedor pueda recibir tráfico
EXPOSE 80

# Comando para ejecutar la aplicación
CMD ["python", "servidor.py"]
