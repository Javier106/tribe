import os
import boto3
import pandas as pd
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
class ListObjectsInput(BaseModel):
    bucket_name: str = Field(description="Nombre del bucket que quiero listar")


# Función para listar objetos en el bucket
def listar_objetos(bucket_name: str):
    try:
        # Lista para almacenar los objetos válidos
        objetos = []
        # Inicializar el token de paginación
        continuation_token = None
        while True:
            # Parámetros para la solicitud
            list_kwargs = {"Bucket": bucket_name}
            if continuation_token:
                list_kwargs["ContinuationToken"] = continuation_token
            # Listar los objetos en el bucket
            response = s3.list_objects_v2(**list_kwargs)
            # Comprobar si el bucket tiene contenidos
            if "Contents" in response:
                for obj in response["Contents"]:
                    # Excluir archivos que terminan en .bzEmpty y que no contienen "2024"
                    if not obj["Key"].endswith(".bzEmpty") and "2024" in obj["Key"]:
                        objetos.append(obj["Key"])
            # Verificar si hay más objetos para listar
            if response.get("IsTruncated"):
                continuation_token = response.get("NextContinuationToken")
            else:
                break
        return objetos
    except Exception as e:
        print(f"Error al listar objetos en el bucket: {e}")
        return []


# Crear la skill utilizando StructuredTool.from_function
list_objects_tool = StructuredTool.from_function(
    func=listar_objetos,
    name="ListObjects",
    description="Useful for listing objects in an S3 bucket, excluding files ending in .bzEmpty and not containing '2024'.",
    args_schema=ListObjectsInput,
    return_direct=True,
)

# Ejemplo de llamada a la función
bucket_name = "nombredelbucket"
objetos_listados = listar_objetos(bucket_name)
df = pd.DataFrame(objetos_listados)
print(df)
