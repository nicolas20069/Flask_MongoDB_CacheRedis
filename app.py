from flask import Flask, jsonify, render_template, request
from config import vehiculos_collection, cache

# Inicializar la aplicación Flask
app = Flask(__name__)


# Función auxiliar para guardar en caché aplicando las condiciones de expiración
def guardar_en_cache(nombre, vehiculo):
    # La condición de la descripción tiene prioridad sobre las demás:
    # si la descripción supera los 20 caracteres no se almacena en caché
    descripcion = vehiculo.get("descripcion") or ""
    if len(descripcion) > 20:
        return

    # El tiempo de expiración depende de la cantidad de caracteres del nombre del vehículo
    if len(nombre) <= 5:
        cache.setex(nombre, 15, str(vehiculo))
    elif len(nombre) <= 10:
        cache.setex(nombre, 20, str(vehiculo))
    else:
        cache.setex(nombre, 40, str(vehiculo))


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

        # Guardar el vehículo en la caché según las condiciones de expiración
        guardar_en_cache(nombre, vehiculo)
        return jsonify({"data": vehiculo, "source": "MongoDB"}), 200

    else:
        return jsonify({"error": "Vehículo no encontrado"}), 404


# Metodo de actualizar
@app.route("/vehiculos/<nombre>", methods=["PUT"])
def put_vehiculo(nombre):
    data = request.get_json(silent=True)
    if not data:
        return (
            jsonify({"error": "Debe enviar los datos del vehículo en formato JSON"}),
            400,
        )

    # No permitir modificar el _id del documento
    data.pop("_id", None)

    # Actualizar el vehículo en MongoDB
    resultado = vehiculos_collection.update_one({"vehiculo": nombre}, {"$set": data})
    if resultado.matched_count == 0:
        return jsonify({"error": "Vehículo no encontrado"}), 404

    # Invalidar la caché del nombre anterior y del nuevo (si cambió) para evitar inconsistencias
    cache.delete(nombre)
    nuevo_nombre = data.get("vehiculo")
    if nuevo_nombre and nuevo_nombre != nombre:
        cache.delete(nuevo_nombre)

    # Devolver el vehículo actualizado
    vehiculo = vehiculos_collection.find_one({"vehiculo": nuevo_nombre or nombre})
    if vehiculo:
        vehiculo["_id"] = str(vehiculo["_id"])

    return (
        jsonify(
            {
                "data": vehiculo,
                "source": "MongoDB",
                "mensaje": "Vehículo actualizado",
            }
        ),
        200,
    )


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
            # Guardar en caché según las condiciones de expiración
            guardar_en_cache(nombre, v)
            resultado = {"data": v, "source": "MongoDB"}

        # Si el vehículo no se encuentra en la base de datos, devolver un mensaje de error
        else:
            resultado = {"error": "Vehículo no encontrado"}

    # Renderizar la plantilla de consulta con el resultado
    return render_template("consulta.html", resultado=resultado)
