# Actividad 1

## Descripción 
En esta actividad se debe crear un chat donde será posible que hayan n-clientes y un servidor central  de  coordinación  de  mensajes.  Para  esta  actividad  se  debe  usar  el  framework  gRPC para implementar el sistema de mensajería usando el protocolo RPC(Remote Procedure Call).

## Desplegar arquitectura (1 servidor - 2 clientes)
Antes de desplegar la arquitectura es importante mencionar que para poder entrar a la línea de comando de cada cliente es necesario ejecutar cada uno en una nueva terminal, por lo que es importante seguir los pasos que vienen a continuación.

### Desplegar servidor y clientes iniciales

Desde linea de comandos y en la carpeta *Actividad1* ejecutar:

  `$docker-compose build`  
	`$docker-compose up --scale client=2`

Esto desplegará los contenedores del servidor y dos clientes.

### Interacción clientes
Para acceder a los chat por parte de cada cliente se deben ejecutar los siguientes comandos en terminales nuevas (uno para cada cliente):

`$docker exec -it actividad1_client_1 bash`
`$docker exec -it actividad1_client_2 bash`

Una vez dentro del contenedor, conectarse al chat mediante el siguiente comando:

`$python client.py`

El programa le preguntará un nombre de usuario.

**Observaciones:** 
- Es necesario hacerlo siempre en nuevas terminales para poder tener acceso a la linea de comando de cada chat como usuarios distintos.
- No se permite registrar usuarios vacíos, ni con espacios ni con el caracter "/" (reservado).
	
### Instrucciones del chat
Al iniciar el chat como cliente se le pedirá ingresar un nombre de usuario (ID del cliente). Si el nombre ingresado ya existe, debe escoger otro para poder ingresar al chat.
Una vez que logra entrar puede comenzar a escribir mensajes. Basta con solo escribir, ya que el historial del chat se actualiza solo. Todos los mensajes enviados se registran en el archivo 'log.txt' almacenado en la carpeta 'server'.

Algunos de los comandos que se pueden ejecutar son:
- /users: Obtiene una lista de todos los clientes conectados al chat.
- /mymsg: Obtiene una lista de todos los mensajes que ha enviado al chat.
- /exit: Cierra su sesión de cliente del chat y libera el ID de usuario (también se acepta ctrl + C). **Atención**: esto eliminará los mensajes del usuario, aunque seguirán mostrandose en el chat de otros.

### Desplegar más contenedores clientes
Para poder desplegar más contenedores como clientes simplemente debe ingresar por línea de comando al directorio 'client' (donde está el Dockerfile). Una vez ahí, ejecutar:

`$docker build -t <nombre_temporal> .`  
`$docker run -it --network=actividad1_default <nombre_temporal> bash`
	
Donde "nombre_temporal" es un nombre que usted debe asignar para identificar al contenedor. El comando anterior inicia el contenedor y lo sitúa autompaticamente en su línea de comando.

Finalmente, dentro del contenedor ejecutar:

`$python client.py`

Si desea agregar más contenedores basta con volver a ejecutar el comando "docker run" sin necesidad de construir antes, ya que la imagen está construida. Esto debe hacerse en una nueva terminal para cada nuevo cliente.

### Comentarios generales
- El id de los mensajes es asignado con el id del cliente y un timestamp en nanosegundos. Se evaluó usar uuid4 pero, ya que el id del cliente es único, entonces lo mensajes que él envie tendrán un id único también.
- Se simuló la creación de un chat online, aquellos donde los usuarios se borran una vez que se desloguean. Para efectos de esta tarea, el id del cliente corresponde a su nombre de usuario y este es bloqueado cuando loguea. Una vez el usuario cierre sesión se liberará el nombre de usuario. Esto evitaría que existan duplicados en el chat.
- El archivo "log.txt" tiene un formato en donde los mensajes quedan registrado con todos sus atributos, esto es: id del mensaje, id del cliente, fecha de envio (cliente), fecha de recepción (servidor) y mensaje.
- El cliente envía un mensaje con el timestamp de su computador, sin embargo, el chat muestra el timestamp de recepción al servidor para mantener consistencia en las horas del chat.
- En caso de querer desplegar la arquitectura nuevamente, asegurarse antes de bajar los contenedores:

	`$docker-compose down`