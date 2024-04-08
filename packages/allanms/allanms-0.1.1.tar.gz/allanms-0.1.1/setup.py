from setuptools import setup, find_packages 

# Leer el contenido del archivo README.md 
with open("README.md", "r", encoding="utf-8") as fh: 
    long_description = fh.read()

setup(
    name="allanms", # Nombre
    version="0.1.1", # Versión 
    packages=find_packages(), # Busca para el paquete creado todos los paquetes que existen 
    install_requires=[], 
    author="Allan Murillo",
    description="Una biblioteca para consultar cursos de la plataforma hack4u",
    long_description=long_description, 
    long_description_content_type="text/markdown", # Tipo de contenido en el que se trata (En este caso sería .md de Marckdown)
    url="https://hack4u.io",
)
