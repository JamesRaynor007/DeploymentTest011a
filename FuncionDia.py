from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import pandas as pd
import os

# Definir la ruta del archivo CSV
file_path = os.path.join(os.path.dirname(__file__), 'TotalPeliculasDia.csv')

# Cargar el dataset
try:
    df = pd.read_csv('TotalPeliculasDia.csv')
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error al cargar el archivo: {str(e)}")

# Verificar las columnas del DataFrame
if 'Day' not in df.columns or 'Count' not in df.columns:
    raise HTTPException(status_code=500, detail="El DataFrame no contiene las columnas esperadas.")

# Crear un diccionario para mapear dias en español a dias en inglés
dias_map = {
    'lunes': 'Monday',
    'martes': 'Tuesday',
    'miercoles': 'Wednesday',
    'jueves': 'Thursday',
    'viernes': 'Friday',
    'sabado': 'Saturday',
    'domingo': 'Sunday',
}

app = FastAPI()

@app.get("/", response_model=dict)
def read_root(request: Request):
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    return {
        "message": "Bienvenido a la API de películas.",
        "instructions": "Usa el endpoint /peliculas/?dia=nombre_del_dia para obtener datos.",
        "links": [{"dia": dia, "url": f"{base_url}/peliculas/?mes={dia}"} for dia in dias_map.keys()]
    }

@app.get("/peliculas/")
def get_peliculas(dia: str):
    # Convertir el dia a minúsculas para evitar problemas de mayúsculas
    dia = dia.lower()

    # Verificar si el dia está en el diccionario
    if dia not in dias_map:
        raise HTTPException(status_code=400, detail="Día no válido. Por favor ingrese un día en español.")

    # Obtener el dia en inglés
    dia_en_ingles = dias_map[dia]

    # Filtrar el DataFrame para encontrar el conteo de películas
    resultado = df[df['Day'] == dia_en_ingles]

    if resultado.empty:
        return {"dia": dia_en_ingles, "cantidad de películas que fueron estrenadas": 0}

    # Verificar que 'Count' sea numérico
    try:
        cantidad = int(resultado['Count'].values[0])
    except ValueError:
        raise HTTPException(status_code=500, detail="Error al procesar la cantidad de películas.")

    return {
        "dia": dia_en_ingles,
        "cantidad de películas que fueron estrenadas": cantidad
    }
