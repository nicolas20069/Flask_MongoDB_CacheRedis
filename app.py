from flask import Flask, jsonify, render_template, request
from config import vehiculos_collection, cache

# Inicializar la aplicación Flask
app = Flask(__name__)


# Rutas de la API
# Ruta para obtener todos los vehículos
@app.route("/vehiculos/<nombre>", methods=["GET"])
def get_vehiculo(nombre):
    # Verificar si el vehículo está en la caché
    vehiculo = cache.get(nombre)

    # Si el vehículo está en la caché, devolverlo desde Redis
    if vehiculo:
        return jsonify({"data": eval(vehiculo), "source": "Redis"}), 200

    # Si el vehículo no está en la caché, buscarlo en MongoDB
    vehiculo = vehiculos_collection.find_one({"vehiculo": nombre})
    if vehiculo:
        vehiculo["_id"] = str(vehiculo["_id"])  # Convertir ObjectId a string

        # Guardar el vehículo en la caché con un tiempo de expiración de 15 segundos si el nombre tiene 5 caracteres o menos
        # Por el momento de lo contrario lo guarda sin tiempo de expiración
        if len(nombre) <= 5:
            cache.setex(
                nombre, 15, str(vehiculo)
            )  # Guardar en Redis con tiempo de expiración de 15 segundos
        # Guardar el vehiculo en el caché si tiene mas de 5 caracteres y menor o igual 10
        elif len(nombre) <= 10:
            cache.setex(
                nombre, 20, str(vehiculo)
            )  # Guardar en redis con tiempo de expiración de 20 segundos
        else:
            # Guardar en Redis sin tiempo de expiración
            cache.set(
                nombre, str(vehiculo)
            )  # Modificar para guardar con tiempo de expiracion adecuado
        return jsonify({"data": vehiculo, "source": "MongoDB"}), 200

    else:
        return jsonify({"error": "Vehículo no encontrado"}), 404


# Metodo de eliminar
@app.route("/vehiculos/<nombre>", methods=["DELETE"])
def delete_vehiculo(nombre):
    cache.delete(nombre)  # Eliminar del caché de redis
    vehiculos_collection.delete_one({"vehiculo": nombre})  # Eliminar de mongoDB
    return (
        jsonify({"mensaje": "Vehículo eliminado"}),
        200,
    )  # Mensaje de confirmación de eliminación


# Ruta para mostrar la tabla de vehículos
@app.route("/tabla")
def mostrar_tabla():
    vehiculos = list(vehiculos_collection.find())
    return render_template("vehiculos.html", vehiculos=vehiculos)


# Ruta para mostrar el formulario de consulta
@app.route("/consulta", methods=["GET"])
def consulta():
    # Obtener el nombre del vehículo desde los parámetros de la URL
    nombre = request.args.get("nombre")
    # Si no se proporciona un nombre, simplemente renderizar la plantilla de consulta sin resultados
    if not nombre:
        return render_template("consulta.html")

    # Verificar si el vehículo está en la caché
    vehiculo = cache.get(nombre)
    if vehiculo:
        resultado = {
            "data": eval(vehiculo),
            "source": "Redis",
        }  # Si el vehículo está en la caché, devolverlo desde Redis
    else:
        # Si el vehículo no está en la caché, buscarlo en MongoDB
        v = vehiculos_collection.find_one({"vehiculo": nombre})
        if v:
            v["_id"] = str(v["_id"])  # Convertir ObjectId a string
            if len(nombre) <= 5:
                cache.setex(
                    nombre, 15, str(v)
                )  # Guardar en Redis con tiempo de expiración de 15 segundos
                # Guardar el vehiculo en el caché si tiene mas de 5 caracteres y menor o igual 10
            elif len(nombre) <= 10:
                cache.setex(nombre, 20, str(v))  # tiempo de expiración de 20 segundos
            else:
                cache.set(nombre, str(v))  # Guardar en Redis sin tiempo de expiración
            resultado = {"data": v, "source": "MongoDB"}

        # Si el vehículo no se encuentra en la base de datos, devolver un mensaje de error
        else:
            resultado = {"error": "Vehículo no encontrado"}

    # Renderizar la plantilla de consulta con el resultado
    return render_template("consulta.html", resultado=resultado)
