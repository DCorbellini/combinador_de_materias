# Combinador de Materias

Este projecto busca facilitar la toma de decisiones a la hora de anotarse a materias, mostrando todas las combinaciones que el alumno tiene disponible en una forma clara e intuitiva

![image](https://github.com/DCorbellini/combinador_de_materias/assets/58539382/d22423d6-8bf1-4b7a-82b2-404631f412fa)

## Modo de uso
1. Descargar historia academica de **[Intraconsulta](https://alumno2.unlam.edu.ar) > Mi Matricula > Historia Academica** y guardarlo en la carpera [files](./files/) como **historia.htm**
1. Descargar oferta de materias de **[Intraconsulta](https://alumno2.unlam.edu.ar) > Inscripciones > Oferta de Materias** y guardarlo en la carpera [files](./files/) como **oferta.htm**
1. Descargar el plan de estudio de **[la pagina de Ingenieria](https://ingenieria.unlam.edu.ar/index.php?seccion=3&idArticulo=565)** y guardarlo en la carpera [files](./files/) como **materias.htm**
   - Este paso solo es necesario si se quiere cambiar el plan de estudios
   - El plan de estudios debe tener materias que se cursen una vez por semana y debe seguir la misma estructura que el plan de estudios de Ingenieria Informatica
1. Ejecutar [main.py](./main.py)
El programa va a generar un archivo excel como el que se mostro en la imagen con todas las combinaciones posibles (limitandose a una materia por dia)

### Opciones Extra
Dentro de [main.py](./main.py) hay 2 variables que ayudan a filtrar combinaciones
- REQUISITOS: lista de enteros donde se introducen los codigos de las materias que deben entrar si o si en la combiancion
- EXTRA_QUERY: Query de SQLite que se usa para filtrar la oferta de materias, con una tabla que incluye el codigo de materia, el codigo de comision, el dia, y el turno en que se cursan
Para mas informacion ver el archivo [main.py](./main.py)
