import json
from wsgiref.simple_server import make_server

#diccionario
tasks = {}
#siguiente id a ocupar (se modifica despues)
next_id = 1
#id de la primer tarea
first_task_id = None

#funcion auxiliar para leer el cuerpo (en json) de una request
def get_json_body(environ):
    try:
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        body = environ['wsgi.input'].read(content_length)

        if not body:
            return None

        return json.loads(body)

    except (ValueError, KeyError, json.JSONDecodeError):
        return None


#funcion auxiliar para crear una response en json
def make_json_response(start_response, data, status, extra_headers=None):

    status_codes = {
        200: "200 OK",
        201: "201 Created",
        204: "204 No Content",
        400: "400 Bad Request",
        404: "404 Not Found",
        405: "405 Method Not Allowed"
    }

    headers = [
        ('Content-Type', 'application/json')
    ]

    #codigo 204 no tiene cuerpo por estandar HTTP
    if status == 204:

        headers.append(
            ('Content-Length', '0')
        )
        if extra_headers:
            headers.extend(extra_headers)
        start_response(
            status_codes[204],
            headers
        )

        return [b""]

    #convierte datos a json
    response_data = data if data is not None else {}
    response_body = json.dumps(response_data).encode('utf-8')

    headers.append(
        ('Content-Length', str(len(response_body)))
    )
    #en caso de que haya mas headers
    if extra_headers:
        headers.extend(extra_headers)

    start_response(
        status_codes.get(
            status,
            "500 Internal Server Error"
        ),
        headers
    )

    return [response_body]

#codigo de app
def app(environ, start_response):

    global next_id, first_task_id #globalizadas para acceder luego
    path = environ['PATH_INFO']
    method = environ['REQUEST_METHOD']

    #caso /tasks (el diccionario en si)
    if path == '/tasks':

        #get
        if method == 'GET':
            return make_json_response(
                start_response,
                list(tasks.values()),
                200
            )

        #post
        if method == 'POST':

            body = get_json_body(environ)

            if body and "title" in body:
                new_id = next_id
                tasks[new_id] = {
                    "id": new_id,
                    "title": body["title"],
                    "done": body.get("done", False)
                }

                #si no hay primera tarea, esta la es
                if first_task_id is None:
                    first_task_id = new_id
                #se pasa al sig id
                next_id += 1

                #se devuelve la URI de la nueva tarea
                return make_json_response(
                    start_response,
                    tasks[new_id],
                    201,
                    [
                        ('Location', f'/tasks/{new_id}')
                    ]
                )

            #si no hay title
            return make_json_response(
                start_response,
                {"error": "Missing title"},
                400
            )


        #no entro en ningun bloque if, no esta soportado el metodo
        return make_json_response(
            start_response,
            {"error": "Method Not Allowed"},
            405
        )


    #caso /tasks/ (la primer tarea)
    if path == '/tasks/':

        #no existe la primer tarea
        if (
            first_task_id is None
            or first_task_id not in tasks
        ):
            return make_json_response(
                start_response,
                {"error": "Not Found"},
                404
            )


        task_id = first_task_id

        #get
        if method == 'GET':
            return make_json_response(
                start_response,
                tasks[task_id],
                200
            )


        #patch
        if method == 'PATCH':
            body = get_json_body(environ)

            #patch debe tener cuerpo
            if not body:
                return make_json_response(
                    start_response,
                    {"error": "Empty body"},
                    400
                )

            #se patchea solo lo especificado
            if "title" in body:
                tasks[task_id]["title"] = body["title"]
            if "done" in body:
                tasks[task_id]["done"] = body["done"]

            return make_json_response(
                start_response,
                tasks[task_id],
                200
            )


        #delete
        if method == 'DELETE':
            del tasks[task_id]
            return make_json_response(
                start_response,
                None,
                204
            )


        #no entro en ningun bloque if, no esta soportado el metodo
        return make_json_response(
            start_response,
            {"error": "Method Not Allowed"},
            405
        )

    #caso /tasks/... (una tarea especifica)
    path_parts = path.split('/')
    if (
        len(path_parts) == 3
        and path_parts[1] == 'tasks'
    ):
        
        #convierte id a int
        try:
            task_id = int(path_parts[2])

        #si no se pudo, no es valido
        except ValueError:
            return make_json_response(
                start_response,
                {"error": "Invalid ID"},
                400
            )


        #get
        if method == 'GET':
            if task_id in tasks:
                return make_json_response(
                    start_response,
                    tasks[task_id],
                    200
                )

            #no hay task con esa id
            return make_json_response(
                start_response,
                {"error": "Not Found"},
                404
            )


        #patch
        if method == 'PATCH':

            #no hay task con esa id
            if task_id not in tasks:
                return make_json_response(
                    start_response,
                    {"error": "Not Found"},
                    404
                )

            body = get_json_body(environ)

            #patch debe tener cuerpo
            if not body:
                return make_json_response(
                    start_response,
                    {"error": "Empty body"},
                    400
                )

            #se patchea solo lo especificado
            if "title" in body:
                tasks[task_id]["title"] = body["title"]
            if "done" in body:
                tasks[task_id]["done"] = body["done"]

            return make_json_response(
                start_response,
                tasks[task_id],
                200
            )


        #delete
        if method == 'DELETE':
            if task_id in tasks:
                del tasks[task_id]
                return make_json_response(
                    start_response,
                    None,
                    204
                )

            #no existia el id
            return make_json_response(
                start_response,
                {"error": "Not Found"},
                404
            )

        #no entro en ningun bloque if, no esta soportado el metodo
        return make_json_response(
            start_response,
            {"error": "Method Not Allowed"},
            405
        )


    #si no es /tasks, /tasks/ ni /tasks/... la ruta no existe
    return make_json_response(
        start_response,
        {"error": "Not Found"},
        404
    )


#server
with make_server("", 9292, app) as server:

    print("Listening on http://localhost:9292")

    server.serve_forever()
