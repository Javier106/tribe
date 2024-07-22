import pandas as pd
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import StructuredTool


# Función para almacenar contenido en un DataFrame y guardar como CSV
def almacenar_en_dataframe(archivo: str, contenido):
    if isinstance(contenido, list):
        df = pd.DataFrame(contenido[1:], columns=contenido[0])
    else:
        df = pd.DataFrame({"contenido": [contenido]})
    nombre_archivo_csv = f"contenido_{archivo.replace('/', '_')}.csv"
    df.to_csv(nombre_archivo_csv, index=False)
    print(f'Contenido del archivo "{archivo}" guardado en "{nombre_archivo_csv}".')
    return nombre_archivo_csv


# Modelo de entrada para la transformación
class TransformToDataFrameInput(BaseModel):
    archivo: str = Field(description="Nombre del archivo original")
    contenido: str = Field(description="Contenido del archivo")


# Crear la skill utilizando StructuredTool.from_function
minerva_tool = StructuredTool.from_function(
    func=almacenar_en_dataframe,
    name="MinervaTool",
    description="Transforms the content of a file into a DataFrame and saves it as a CSV.",
    args_schema=TransformToDataFrameInput,
    return_direct=True,
)
