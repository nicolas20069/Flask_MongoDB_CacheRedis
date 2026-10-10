*** Activar Redis ***
En una consola de ubuntu o al correr el sistema, ingresa: 
- redis-server

*** En otra consola ***
Para usar como tal redis usamos el comando: 
- redis-cli 

*** Ingresar a la base de datos 1 de Redis ***
Por defecto Redis abre la base de datos 0, así que debes cambiar a la 1: 
- SELECT 1

------- Prueba En Redis --------------------------------------------------------------------

*** Consultar una clave ***
Si quieres ver el contenido de una clave (ejemplo: Avión):
- GET "Avión"
- GET Avión 

*** Ver el tiempo de vida restante ***
- TTL "Avión"

Si devuelve un número positivo → son los segundos restantes antes de que expire.

Si devuelve -2 → la clave ya expiró y fue eliminada.

Si devuelve -1 → la clave no tiene expiración.


-------------------- Prueba en Postman ----------------------------------------------------

*** 1. Consultar un vehiculo (GET) - POSTMAN ***
// Configurar la URL de la API
La ruta debe apuntar al endpoint que creaste en Flask.
Escribe la URL en el campo de dirección
Cambia Avión por el nombre del vehículo que quieras consultar

- http://127.0.0.1:5000/vehiculos/Avión

Hacer click en Send
Observa el JSON devuelto: debe incluir source: MongoDB

*** 2. Ejecutar la segunda consulta antes de 15s ***
El dato estará en Redis y la respuesta debe reflejarlo.

Haz clic en Send nuevamente

Observa que ahora el JSON incluye source: Redis


*** 3. Esperar más de 15 segundos y volver a consultar ***
La clave expira y se vuelve a consultar en MongoDB.

Espera al menos 15 segundos

Haz clic en Send otra vez

Verás que el source vuelve a ser MongoDB


*** 4. Probar con un vehículo de más de 5 caracteres ***
Estos no expiran en Redis, siempre vendrán de caché.

- http://127.0.0.1:5000/vehiculos/Cohete

Ejecuta la primera consulta → source: MongoDB

Ejecuta consultas posteriores → siempre source: Redis

No importa cuánto tiempo pase, no expira


