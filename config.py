from pymongo import MongoClient
import redis

# CONEXION A MONGODB
client = MongoClient("mongodb://localhost:27017/")
db=client["automoviles"]
vehiculos_collection = db["vehiculos"]

#CONEXION A REDIS
cache = redis.Redis(host="localhost", port=6379, db=1, decode_responses=True)   