import os
import boto3
import csv
import re
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool

os.environ["AWS_ENDPOINT_URL"] = "https://s3.eu-central-003.backblazeb2.com"

# Configurar las credenciales de Backblaze B2
session = boto3.session.Session()
s3 = session.client(
    service_name="s3",
    endpoint_url="https://s3.us-west-002.backblazeb2.com",  # URL del endpoint de Backblaze B2
    aws_access_key_id="0030e94285353960000000012",  # Application Key ID de Backblaze
    aws_secret_access_key="K003HiIvvB32rxCRH4bC///m7cV1+3Q",  # Application Key de Backblaze
)

# Inicializar el cliente de S3
s3 = boto3.client("s3")

# Nombre del bucket que quiero listar
bucket_name = "EWA-S3-APP-IA-UPLOAD"


# Modelo de entrada para listar objetos
class KeyWordsInput(BaseModel):
    bucket_name: str = Field(description="Nombre del bucket que quiero listar")
    palabra_clave: str = Field(description="Palabra clave a buscar en los archivos")


# Función para listar objetos en el bucket
def listar_objetos(bucket_name: str):
    try:
        objetos = []
        continuation_token = None
        while True:
            list_kwargs = {"Bucket": bucket_name}
            if continuation_token:
                list_kwargs["ContinuationToken"] = continuation_token
            response = s3.list_objects_v2(**list_kwargs)
            if "Contents" in response:
                for obj in response["Contents"]:
                    if not obj["Key"].endswith(".bzEmpty") and "2024" in obj["Key"]:
                        objetos.append(obj["Key"])
            if response.get("IsTruncated"):
                continuation_token = response.get("NextContinuationToken")
            else:
                break
        return objetos
    except Exception as e:
        print(f"Error al listar objetos en el bucket: {e}")
        return []


# Función para leer el contenido de un archivo TXT desde S3
def leer_txt_desde_s3(bucket_name, file_key):
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    contenido = obj["Body"].read().decode("utf-8")
    return contenido


# Función para leer el contenido de un archivo CSV desde S3
def leer_csv_desde_s3(bucket_name, file_key):
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    contenido = obj["Body"].read().decode("utf-8").splitlines()
    reader = csv.reader(contenido)
    contenido_csv = list(reader)
    return contenido_csv


# Función para buscar una palabra clave en el contenido de un archivo
def buscar_palabra_clave(contenido, palabra_clave):
    if isinstance(contenido, list):
        contenido_str = "\n".join([",".join(row) for row in contenido])
    else:
        contenido_str = contenido

    if re.search(palabra_clave, contenido_str, re.IGNORECASE):
        return True
    return False


# Función principal para procesar archivos
def procesar_archivos(bucket_name, palabra_clave):
    archivos = listar_objetos(bucket_name)

    for archivo in archivos:
        if archivo.endswith(".txt"):
            contenido = leer_txt_desde_s3(bucket_name, archivo)
        elif archivo.endswith(".csv"):
            contenido = leer_csv_desde_s3(bucket_name, archivo)
        else:
            print(f"Tipo de archivo no soportado: {archivo}")
            continue

        if buscar_palabra_clave(contenido, palabra_clave):
            print(f'La palabra clave "{palabra_clave}" fue encontrada en el archivo: {archivo}')
            return archivo, contenido

    print(f'La palabra clave "{palabra_clave}" NO fue encontrada en ninguno de los archivos.')
    return None, None


# Crear la skill utilizando StructuredTool.from_function
vulcano_search = StructuredTool.from_function(
    func=procesar_archivos,
    name="KeyWordsSearch",
    description="Searches for a keyword in .txt and .csv files in an S3 bucket.",
    args_schema=KeyWordsInput,
    return_direct=True,
)
