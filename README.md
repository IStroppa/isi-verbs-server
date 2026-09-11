Consigna
En el README, una breve explicación con tus palabras de la diferencia entre `GET`, `POST`, `PATCH` y `DELETE`, y por qué `POST` no es idempotente

Respuesta:

GET: se usa para pedirle informacion al servidor. Dado un URI, se espera que la response del server incluya la informacion pedida (objeto)

POST: crea un nuevo objeto en el servidor. No es idempotente porque la idempotencia es cuando ejecutar varias veces el mismo metodo produce el
mismo resultado que ejecutarlo una unica vez, y POST ejecutado varias veces creara varios objetos distintos a pesar de que se haya dado la misma
informacion (los objetos tendran los mismos valores en sus atributos, pero su identificacion en el servidor sera distinta, y contaran como objetos
separados)

PATCH: modifica la informacion de un objeto, pero solo parcialmente. En el body se especifica que atributos se desean cambiar, y los demas no se 
veran afectados por la ejecucion del metodo.

DELETE: borra el objeto especificado del servidor.
