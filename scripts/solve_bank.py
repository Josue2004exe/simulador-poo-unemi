import json
import os
import re

def solve():
    db_file = os.path.join(os.path.dirname(__file__), "..", "data", "questions_bank.json")
    with open(db_file, "r", encoding="utf-8") as f:
        db = json.load(f)
    
    # Positive rules: substring or regex matching the correct option.
    # Sorted by specificity (specific terms first, general terms last).
    rules = [
        # Specific ID overrides for "Ninguna respuesta es correcta."
        ("1bd63af996f0f8a33235723d0ed161bf2d5ad013b4c9c93e48a848e2eec77ac3", "Ninguna respuesta es correcta."),
        ("53e9b746916ec800f2e954a6e262653795747ea984b7352e90e321e28da1b29f", "Ninguna respuesta es correcta."),
        ("ba32caede0cde19b61a59ae6bcc6062e530a9e79f5be6345fa0e5835fe7653f9", "Ninguna respuesta es correcta."),
        ("7fa44bb25ceaf42665138ac123023f477fda0358f5ae26794ce39ffc19f1f3e9", "Ninguna respuesta es correcta."),
        
        # General rules
        (None, "Porque posee compatibilidad con inteligencia artificial y ciencia de datos, además de frameworks para desarrollo web."),
        (None, "Validar las credenciales del estudiante y determinar si puede acceder al sistema."),
        (None, "python manage.py startapp"),
        (None, "Permite que el campo pueda dejarse vacío durante la validación de formularios."),
        (None, "Porque representa de forma clara la entidad del mundo real que se desea modelar."),
        (None, "Debe convertirse en una cadena con formato JSON para facilitar el intercambio de datos entre aplicaciones."),
        (None, "Herencia, porque las clases hijas adquieren características de la clase padre."),
        (None, "Organizar el contenido del documento de forma estructurada y significativa."),
        (None, "En el directorio \"venv\" asociado al proyecto."),
        (None, "Captura las acciones del usuario, envía solicitudes al servidor y presenta las respuestas recibidas."),
        (None, "Colocar un breakpoint antes de la operación, avanzar con Step Over e inspeccionar el valor de \"saldo\" en cada pausa."),
        (None, "Analizador, porque procesa información para generar un resultado."),
        (None, "Un molde o plantilla para crear objetos con características similares."),
        (None, "Facilitar el intercambio de información entre aplicaciones mediante un formato de texto estándar."),
        (None, "La escalabilidad."),
        (None, "Internet es la infraestructura de red, mientras que la Web es un servicio que funciona sobre ella."),
        (None, "Registrar el modelo utilizando admin.site.register(Estudiante)."),
        (None, "Convertir el diccionario en una cadena con formato JSON mediante un proceso de serialización."),
        (None, "PUT, porque está diseñado para actualizar o reemplazar la información de un recurso existente."),
        (None, "Consultor, porque presenta información sin alterar el estado del objeto."),
        (None, "python manage.py makemigrations"),
        (None, "Porque representa entidades del mundo real mediante objetos con atributos y métodos."),
        (None, "Un modelo que será utilizado para crear una tabla en la base de datos."),
        (None, "Porque HTML define la estructura del contenido y CSS define su presentación visual."),
        (None, "El proyecto pierde uno de los módulos que conforman la estructura del sistema, aunque los demás archivos continúan organizados dentro del mismo proyecto."),
        (None, "PUT, porque permite actualizar la información de un recurso existente en el servidor."),
        (None, "No se generarán nuevas migraciones para reflejar los cambios realizados en el modelo."),
        (None, "Una cadena en formato JSON lista para ser enviada o almacenada."),
        (None, "Permite mayor flexibilidad, mantenimiento y reutilización del código."),
        (None, "Representar entidades del mundo real con atributos y comportamientos específicos."),
        (None, "Colocar un breakpoint y ejecutar el programa en modo depuración para analizar la ejecución paso a paso."),
        (None, "Un campo."),
        (None, "El modelo no fue registrado en el archivo admin.py."),
        (None, "Inicializar el objeto asignando valores iniciales a sus atributos al momento de su creación."),
        (None, "Indicar a qué elementos HTML se aplicarán los estilos definidos."),
        (None, "Ejecutar python manage.py makemigrations y posteriormente python manage.py migrate, porque cambió la estructura del modelo."),
        (None, "ORM."),
        (None, "GET, POST, PUT, DELETE."),
        (None, "python manage.py migrate"),
        (None, "Porque utiliza un formato de texto estándar que puede ser interpretado por diferentes plataformas y lenguajes."),
        (None, "Una instancia de la clase Auto con valores particulares."),
        (None, "Acciones o comportamientos que el objeto puede realizar dentro del sistema."),
        (None, "En el editor de código, porque es el espacio destinado a escribir y modificar las instrucciones del programa."),
        (None, "Encapsulación, porque restringe la modificación directa de los datos."),
        (None, "Todos los estudiantes que sean necesarios, ya que ForeignKey representa una relación de uno a muchos."),
        (None, "Programar manualmente funcionalidades comunes como autenticación, formularios y conexión con bases de datos."),
        (None, "Cuando se requiere enviar información al servidor para registrar nuevos datos o procesar un formulario."),
        (None, "Una etiqueta de apertura, atributos opcionales, contenido y una etiqueta de cierre."),
        (None, "El objeto puede no tener un estado inicial definido correctamente."),
        (None, "En el panel del proyecto, ya que permite explorar la estructura de carpetas y archivos del proyecto."),
        (None, "Un diccionario de Python se convierte en una cadena con formato JSON para ser enviada a un servidor."),
        (None, "django-admin startproject"),
        (None, "Son propiedades que almacenan información específica del objeto en un momento determinado."),
        (None, "Una instancia concreta de la clase Libro con valores específicos asignados a sus atributos."),
        (None, "DELETE, porque está diseñado para eliminar recursos existentes del servidor."),
        (None, "El contenido visible que será mostrado en el navegador al usuario."),
        (None, "Colocar breakpoints en los bloques condicionales y ejecutar el programa en modo depuración para observar dónde se detiene la ejecución."),
        (None, "Aplicar un proceso de deserialización para convertir la cadena JSON en un objeto de Python."),
        (None, "En la librería el desarrollador decide cuándo utilizar sus funciones; en el framework es el framework quien controla el flujo de ejecución."),
        (None, "Permite almacenar valores NULL en la base de datos para ese campo."),
        (None, "Convertir el objeto de Python a una cadena en formato JSON mediante un proceso de serialización."),
        (None, "Modelar estudiantes, docentes y asignaturas como clases independientes con atributos y métodos propios, estableciendo relaciones entre ellas según su interacción."),
        (None, "La ejecución paso a paso del depurador."),
        (None, "python manage.py runserver"),
        (None, "Uno a muchos."),
        (None, "Permitir la entrada de datos del usuario para ser enviados al sistema."),
        (None, "Un método modificador, porque altera directamente el valor de un atributo."),
        (None, "Una respuesta HTTP con el contenido solicitado y la información correspondiente al resultado de la petición."),
        (None, "Un diccionario u objeto almacenado en la memoria de Python."),
        (None, "Contener metadatos e información que no se muestra directamente en la página."),
        (None, "Ejecutar el programa en modo depuración y observar la variable desde el depurador."),
        (None, "Encapsulación, porque controla el acceso a los datos internos."),
        (None, "python manage.py createsuperuser"),
        (None, "La Vista."),
        (None, "Porque define las características y comportamientos que tendrán los objetos creados a partir de ella."),
        (None, "Muchos a muchos."),
        (None, "Definir el texto que representará al objeto cuando sea mostrado por Django."),
        (None, "El selector de clase puede aplicarse a varios elementos, mientras que el id es único."),
        (None, "Herencia y polimorfismo, porque comparten características y tienen comportamientos diferentes."),
        (None, "Los archivos \".py\" que contienen la implementación del sistema."),
        (None, "Porque permite diferenciar entre el estado del objeto y las acciones que puede realizar."),
        (None, "Procesar la solicitud, obtener la información requerida y enviar una respuesta al cliente."),
        (None, "Se envía una solicitud HTTP al servidor correspondiente para obtener los recursos."),
        (None, "Crear una carpeta del proyecto que contenga los archivos \".py\", el directorio \"venv\" y los archivos de configuración del IDE."),
        (None, "Una base de datos."),
        (None, "Una relación donde varios estudiantes pueden pertenecer a una misma carrera."),
        (None, "Abstracción, porque se enfoca en lo importante del objeto."),
        (None, "La clase define las características y comportamientos, mientras que el objeto es la instancia concreta de esa definición."),
        (None, "GET, porque está diseñado para solicitar información sin modificar los recursos existentes."),
        (None, "Polimorfismo, porque un mismo método tiene comportamientos distintos."),
        (None, "Métodos, porque representan comportamientos asociados al objeto estudiante."),
        (None, "PUT para modificar el curso y DELETE para eliminarlo."),
        (None, "El Modelo."),
        (None, "Interpretar los archivos HTML, CSS y otros recursos para mostrar la página al usuario."),
        (None, "Dentro de la carpeta principal del proyecto, junto con los demás archivos \".py\"."),
        (None, "El campo puede dejarse vacío en formularios y además almacenar valores NULL en la base de datos."),
        (None, "Encapsulación, porque protege los datos internos y controla su acceso."),
        (None, "Diango."),
        (None, "POST, porque permite enviar información al servidor para crear un nuevo recurso."),
        (None, "Controlar la apariencia visual y el diseño de los elementos HTML."),
        (None, "También se eliminarán los estudiantes relacionados con esa carrera."),
        (None, "El servidor procesa la solicitud antes de generar la respuesta correspondiente."),
        (None, "Django impedirá almacenar el nuevo registro porque el correo debe ser único."),
        (None, "El backend."),
        (None, "La POO organiza la solución en objetos que integran datos y comportamientos relacionados."),
        (None, "La serialización convierte objetos de Python en formato JSON, mientras que la deserialización convierte datos JSON nuevamente en objetos de Python."),
        (None, "El modificador altera el estado del objeto, mientras que el consultor solo muestra información sin cambiarlo."),
        (None, "La independencia del motor de base de datos."),
        (None, "No es necesario ejecutar migraciones, porque únicamente se agregó un método y no cambió la estructura del modelo."),
        (None, "Permitir el acceso a documentos enlazados mediante navegadores usando protocolos como HTPP o HTPPS."),
        
        # Fallback values
        (None, "Ninguna respuesta es correcta.")
    ]

    solved_count = 0
    unsolved = []

    for q in db["preguntas"]:
        q_id = q["id"]
        q_text = q["text_snippet"]
        options = q["options"]
        
        found = False
        # Try specific rule override
        for target_id, correct_text in rules:
            if target_id == q_id:
                # Find correct_text in options
                for idx, opt in enumerate(options):
                    if opt.strip() == correct_text.strip():
                        q["correct_index"] = idx
                        found = True
                        solved_count += 1
                        break
                if found:
                    break
        
        if found:
            continue
            
        # Try generic rules matching text
        for target_id, correct_text in rules:
            if target_id is None:
                # Search option text
                for idx, opt in enumerate(options):
                    if opt.strip() == correct_text.strip():
                        q["correct_index"] = idx
                        found = True
                        solved_count += 1
                        break
                if found:
                    break
        
        if not found:
            unsolved.append(q)

    print(f"Solved: {solved_count}/{len(db['preguntas'])}")
    if unsolved:
        print(f"Unsolved: {len(unsolved)}")
        for idx, u in enumerate(unsolved):
            print(f"[{idx}] Text: {u['text_snippet']}")
            print(f"    Options: {u['options']}")
            
    # Save the updated database
    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "questions_bank_solved.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        
if __name__ == "__main__":
    solve()
