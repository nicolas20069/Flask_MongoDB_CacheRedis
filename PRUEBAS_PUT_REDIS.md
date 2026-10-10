# Guía de pruebas — Método PUT y caché con Redis

Esta guía cubre la parte del método **PUT** y las **condiciones de expiración** de la caché.
Todas las pruebas se realizan en **Postman** y se verifican en **redis-cli**.

---

## 0. Requisitos previos

- MongoDB corriendo en `mongodb://localhost:27017/` (base `automoviles`, colección `vehiculos`).
- **Redis corriendo en el puerto 6379** (obligatorio para ver la caché).
- Aplicación levantada:

```
python app.py
```

Servidor disponible en `http://127.0.0.1:5000`.

> Nota: en la máquina de prueba **Redis no estaba iniciado** (puerto 6379 cerrado). Antes de la
> sustentación hay que arrancar el servidor de Redis y comprobar con `redis-cli ping` que responde `PONG`.

---

## 1. Condiciones de expiración (resumen)

| Condición (según el nombre del vehículo) | Tiempo en caché |
|---|---|
| 5 caracteres o menos | 15 segundos |
| Más de 5 y hasta 10 caracteres | 20 segundos |
| Más de 10 caracteres | 40 segundos |
| Descripción con más de 20 caracteres | **No se cachea** (tiene prioridad) |

> **Importante:** con los datos actuales **todas las descripciones tienen más de 20 caracteres**, por lo
> que, aplicando la regla de prioridad, **ningún vehículo se cachea**. Para demostrar la caché primero
> se usa el **PUT** para dejar una descripción corta (≤ 20 caracteres) y así activar el almacenamiento.

Se recomiendan nombres **sin tildes** para la demo (evitan problemas de codificación en `redis-cli`):

- `Barco` (5) → TTL 15 s
- `Cohete` (6) → TTL 20 s
- `Bicicleta` (9) → TTL 20 s
- `Motocicleta` (11) → TTL 40 s

---

## 2. Método PUT — Actualizar vehículo

**Postman**

- Método: `PUT`
- URL: `http://127.0.0.1:5000/vehiculos/Barco`
- Body → raw → **JSON**:

```json
{
  "descripcion": "Lancha pequena",
  "peso": 3
}
```

**Respuesta esperada (200):**

```json
{
  "data": { "_id": "...", "vehiculo": "Barco", "categoria": "...", "peso": 3, "descripcion": "Lancha pequena" },
  "source": "MongoDB",
  "mensaje": "Vehículo actualizado"
}
```

> La URL identifica el vehículo **actual**. Si querés **renombrarlo**, incluí el campo `vehiculo` en el body
> (el `_id` se ignora/omite siempre). El método invalida la caché tanto del nombre anterior como del nuevo.

---

## 3. Demostrar invalidación de caché al actualizar

1. `GET http://127.0.0.1:5000/vehiculos/Cohete` → `"source": "MongoDB"` (primera consulta, aún con descripción larga → no cachea).
2. `PUT http://127.0.0.1:5000/vehiculos/Cohete` con descripción corta:

```json
{ "descripcion": "Cohete ok" }
```

3. `GET http://127.0.0.1:5000/vehiculos/Cohete` → `"source": "MongoDB"` y ahora **sí** se cachea.
4. En Redis verificar:

```
redis-cli
SELECT 1
GET Cohete
TTL Cohete
```

Debe devolver el JSON del vehículo y un `TTL` entre 0 y 20.

5. `GET http://127.0.0.1:5000/vehiculos/Cohete` otra vez → `"source": "Redis"`.

6. Ahora `PUT http://127.0.0.1:5000/vehiculos/Cohete` con otro valor:

```json
{ "peso": 12 }
```

7. En Redis comprobar que la clave **se invalidó**:

```
GET Cohete     -->  (nil)
TTL Cohete     -->  -2
```

8. `GET http://127.0.0.1:5000/vehiculos/Cohete` → vuelve a `"source": "MongoDB"`.

---

## 4. Demostrar las 4 condiciones de expiración

Para cada caso: hacer `PUT` con una **descripción corta (≤ 20)** y luego `GET`, midiendo el `TTL`.

### 4.1 Caso 15 segundos — nombre de 5 caracteres o menos

```
PUT  /vehiculos/Barco        { "descripcion": "Lancha pequena" }
GET  /vehiculos/Barco        --> source: MongoDB  (se cachea)
TTL Barco                    --> ~15
```

### 4.2 Caso 20 segundos — nombre de 6 a 10 caracteres

```
PUT  /vehiculos/Cohete       { "descripcion": "Cohete ok" }
GET  /vehiculos/Cohete       --> source: MongoDB
TTL Cohete                   --> ~20
```

```
PUT  /vehiculos/Bicicleta    { "descripcion": "Bici ok" }
GET  /vehiculos/Bicicleta    --> source: MongoDB
TTL Bicicleta                --> ~20
```

### 4.3 Caso 40 segundos — nombre de más de 10 caracteres

```
PUT  /vehiculos/Motocicleta  { "descripcion": "Moto ok" }
GET  /vehiculos/Motocicleta  --> source: MongoDB
TTL Motocicleta              --> ~40
```

### 4.4 Caso SIN caché — descripción con más de 20 caracteres (prioridad)

Con la descripción original (larga) no se cachea aunque el nombre sea corto:

```
GET  /vehiculos/Barco        --> source: MongoDB
GET  /vehiculos/Barco        --> source: MongoDB  (SEGUIRÁ siendo MongoDB: no se cacheó)
TTL Barco                    --> -2  (la clave no existe)
```

> Hacer este caso **antes** de modificar `Barco` en el punto 4.1, o restaurar la descripción larga con PUT.

---

## 5. Verificar expiración automática

```
GET  /vehiculos/Motocicleta   --> source: MongoDB (TTL 40)
GET  /vehiculos/Motocicleta   --> source: Redis
# esperar más de 40 segundos
GET  /vehiculos/Motocicleta   --> source: MongoDB (la clave expiró sola)
TTL Motocicleta               --> -2
```

---

## 6. Casos de error del PUT

- Vehículo inexistente:

```
PUT /vehiculos/NoExiste   { "peso": 1 }
--> 404  { "error": "Vehículo no encontrado" }
```

- Sin body JSON:

```
PUT /vehiculos/Barco   (sin body, o sin Content-Type: application/json)
--> 400  { "error": "Debe enviar los datos del vehículo en formato JSON" }
```

---

## 7. Guion sugerido para el video (sección PUT)

1. Explicar que el PUT actualiza el vehículo en MongoDB y **borra su clave en Redis**.
2. Mostrar un `PUT` en Postman y la respuesta 200.
3. Mostrar antes/después en `redis-cli` (`GET` y `TTL`) evidenciando la invalidación.
4. Mostrar las 4 condiciones de expiración con `TTL` (15 / 20 / 40 / sin caché).
5. Mostrar la expiración automática tras esperar el TTL.
6. Cerrar mostrando que `GET` y `DELETE` de los compañeros siguen funcionando.
