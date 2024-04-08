# Hack4u Academy Courses Library

Una biblioteca Python para consultar cursos de la academia Hack4u, replicado por allanms 

## Cursos disponibles: 

Instala el paquete usando `pip3`: 

```python3
pip3 install allanms 
```

## Uso básico 

### Listar todos los cursos 

```python
from allanms import list_courses 

for course in list_courses():
    print(course)
```

### Obtener un curso por nombre 

```python 
from allanms import get_course_by_name 

course = get_course_by_name("Python Ofensivo")
print(course)
```

### Calcular duración total de los cursos 

```python3 
from allanms.utils import total_duration 

print(f"Duración total: {total_duration()} horas")
```
