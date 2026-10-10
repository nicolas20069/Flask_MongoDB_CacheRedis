# Flask + MongoDB + Redis Cache

Aplicación web desarrollada en Flask para consultar información de vehículos almacenados en MongoDB, usando Redis como caché para mejorar el rendimiento y demostrar la estrategia de almacenamiento temporal de datos.

## Descripción del proyecto

Este proyecto simula una API REST y una interfaz web para consultar vehículos por nombre. Cuando una consulta se realiza por primera vez, el sistema revisa MongoDB. Si el dato existe, lo guarda en Redis para futuras consultas rápidas. La caché tiene un tiempo de expiración de 15 segundos para nombres cortos (hasta 5 caracteres), mientras que para nombres más largos se guarda sin expiración.

La aplicación incluye:
- API REST con Flask
- Base de datos MongoDB local
- Caché Redis local
- Vistas HTML para mostrar la tabla y la consulta individual
- Validación de caché mediante el campo `source` en la respuesta

## Tecnologías utilizadas
- Python
- Flask
- MongoDB
- Redis
- Jinja2
- HTML/CSS

## Estructura del proyecto


Taller_practico/
├── app.py
├── config.py
├── README.md
├── requirements.txt
├── .gitignore
├── static/
│   └── style.css
├── templates/
│   ├── consulta.html
│   └── vehiculos.html
└── __init__.py


## Requisitos previos

Antes de ejecutar el proyecto necesitas tener instalados:

- Python 3.10 o superior
- MongoDB local en ejecución
- Redis local en ejecución
- pip para instalar dependencias

## Instalación de dependencias

- Desde la carpeta del proyecto, crea un entorno virtual y luego instala las dependencias:

python -m venv venv


- En Windows PowerShell: 

powershell
venv\Scripts\Activate.ps1
- 

- En Git  o Linux/macOS: 

source venv/bin/activate


- Luego instala las librerías: 

pip install -r requirements.txt


- Si no tienes el archivo `requirements.txt`, puedes instalar manualmente: 

pip install flask pymongo redis


## Configuración de MongoDB

- Asegúrate de que MongoDB esté corriendo localmente en el puerto por defecto: 

mongodb://localhost:27017/


- La base de datos usada es: 

automoviles


- Y la colección: 

vehiculos


## Configuración de Redis

### Iniciar Redis

- En Ubuntu/Linux:

redis-server


En Windows, si tienes Redis instalado como servicio o ejecutable local, debes iniciar el servidor desde la terminal correspondiente.

### Conectar a Redis

- Se recomienda abrir otra terminal e ingresar:

redis-cli


- Y luego cambiar a la base de datos 1:

SELECT 1


## Ejecutar la aplicación

- Una vez que MongoDB y Redis estén activos, ejecuta:

flask run


- O directamente:

python app.py


La aplicación quedará disponible en:


http://127.0.0.1:5000/


## Rutas del proyecto

### 1. Tabla general de vehículos

http://127.0.0.1:5000/tabla

Muestra toda la colección de vehículos en una tabla HTML.

### 2. API de consulta por nombre

http://127.0.0.1:5000/vehiculos/Avión

Ejemplo de respuesta:

json
{
  "data": {
    "_id": "...",
    "vehiculo": "Avión",
    "categoria": "Aéreo",
    "peso": 70,
    "descripcion": "Aeronave comercial para transporte de pasajeros"
  },
  "source": "MongoDB"
}


### 3. Vista de consulta web

http://127.0.0.1:5000/consulta?nombre=Avión

Muestra el resultado en la plantilla HTML con la información del vehículo.

## Cómo funciona la caché

La lógica del proyecto es la siguiente:

1. Se busca el vehículo en Redis.
2. Si existe, se responde desde caché (`source: Redis`).
3. Si no existe, se busca en MongoDB.
4. Si se encuentra, se guarda en Redis.
5. Los nombres con longitud menor o igual a 5 tienen TTL de 15 segundos.
6. Los nombres más largos se almacenan sin expiración.

## Pruebas con Redis
Para realizarlo, se debe hacer la consulta desde el navegador o postman, para llamar al valor desde mongoDB,
Para posteriormente se guarde en el cache de redis.

- En la consola de Redis, puedes verificar la caché:

GET "Avión"


- O también:

GET Avión


- Para ver el tiempo de vida restante:

TTL "Avión"


### Significado de TTL
- Número positivo: segundos restantes antes de que expire.
- `-2`: la clave ya expiró y fue eliminada.
- `-1`: la clave no tiene expiración.

## Pruebas con Postman

### 1. Consultar un vehículo

URL:

http://127.0.0.1:5000/vehiculos/Avión


Resultado esperado: `source: MongoDB`

### 2. Ejecutar la segunda consulta antes de 15 segundos

Ejecuta la misma URL otra vez antes de que expire la caché.

Resultado esperado: `source: Redis`

### 3. Esperar más de 15 segundos y volver a consultar

Cuando la clave expire, la aplicación vuelve a consultar MongoDB.

Resultado esperado: `source: MongoDB`

### 4. Probar con un vehículo de más de 5 caracteres

URL:

http://127.0.0.1:5000/vehiculos/Cohete


Primer consulta: `source: MongoDB`

Consultas posteriores: `source: Redis`

No importa cuánto tiempo pase, porque la clave no expira.

## Datos de ejemplo

Los vehículos representados en el proyecto incluyen:
- Automóvil
- Motocicleta
- Camión
- Bicicleta
- Monopatín
- Barco
- Lancha
- Avión
- Helicóptero
- Cohete

## Resultado esperado

La app permite:
- visualizar la tabla general
- consultar un vehículo individual por nombre
- comprobar el uso de caché con Redis
- diferenciar si la respuesta viene de base de datos o caché

## Notas finales

Este proyecto es una demostración de caché con Redis y persistencia con MongoDB. Sirve para comprender cómo se puede reducir la carga de consultas repetidas y mejorar el rendimiento de una aplicación web sin perder la consistencia de los datos.


