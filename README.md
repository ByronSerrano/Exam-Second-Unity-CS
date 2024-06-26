# Sistema de Gestión de Ventas

Este proyecto fue creado usando FastAPI con Python. Y para la renderización de FrontEnd, se usó Jija2Template.

## Requisitos
- Python 3.* 
- pip (instalado con Python por defecto)

## Instalación
1. Clona el repositorio en tu máquina:

   ```bash
   git clone https://github.com/ByronSerrano/Exam-Second-Unity-CS.git
   ```

2. Crea un entorno virtual en python:

   ```bash
   python -m venv env
   ```

3. Activa el Entorno Virtual:

   ```bash
   env\Script\activate
   ```


4. Dentro del proyecto, instala las dependencias:

   ```bash
   pip install -r requeriments.txt
   ```

4. Dentro del proyecto, crea un archivo llamado .env, usa estás credenciales para usar una DataBase en la nube:

   ```bash
   DB_HOST=byodsnzhyihhwcei9vo6-postgresql.services.clever-cloud.com
   DB_NAME=byodsnzhyihhwcei9vo6
   DB_USER=ugsu8hokxjgghmcmtyc5
   DB_PASSWORD=07psNw1Mv2mpImZxviJz4WcyIBVa20
   DB_PORT=50013
   ```

## Levantar el proyecto

1. Ejecutar el siguiente comando para levantar el proyecto:

   ```bash
   uvicorn main:app --reload
   ```
