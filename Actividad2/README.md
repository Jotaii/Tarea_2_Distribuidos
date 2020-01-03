# Actividad 2

## Descripción 
En esta actividad se debe crear un chat donde será posible que hayan n-clientes y un servidor central  de  coordinación  de  mensajes.  En esta actividad se utiliza RabbitMQ como broker de mensajería.

## Desplegar arquitectura (1 servidor - 2 clientes)
Antes de desplegar la arquitectura es importante mencionar que para poder entrar a la línea de comando de cada cliente es necesario ejecutar cada uno en una nueva terminal, por lo que es importante seguir los pasos que vienen a continuación.

### Desplegar servidor y clientes iniciales

Desde linea de comandos y en la carpeta *Actividad2* ejecutar:

  `$docker-compose build`  
	`$docker-compose up --scale client=2`

Esto desplegará los contenedores del servidor y dos clientes. 

**Nota:** Al desplegar la arquitectura es recomendable esperar a que el contenedor "rabbitmq" se inicie completamente antes de pasar a la siguiente sección (interacción con clientes). Para comprobar que el server está listo, el container "rabbitmq_1" debe mostrar en pantalla:

`... user 'guest' authenticated and granted access to vhost '/'`

### Interacción clientes
Para conectarse al chat desde cada cliente es necesario abrir una nueva terminal para cada uno y acceder a la linea de comandos:

`$docker exec -it actividad2_client_1 bash`
`$docker exec -it actividad2_client_2 bash`

Una vez dentro del contenedor, conectarse al chat mediante el siguiente comando:

`$python client.py`

El programa le preguntará un nombre de usuario.

**Observaciones:** En caso que al iniciar el chat salga error de conexión, cancele y vuelva a intentar. Esto ocurre si el cliente se inicia antes del contenedor de RabbitMQ.
	
### Instrucciones del chat
Al iniciar el chat como cliente se le pedirá ingresar un nombre de usuario (ID del cliente). Si el nombre ingresado ya existe, debe escoger otro para poder ingresar al chat.
Una vez que logra entrar puede comenzar a escribir mensajes. Basta con solo escribir, ya que el historial del chat se actualiza solo. Todos los mensajes enviados se registran en el archivo 'log.txt' almacenado en la carpeta 'server'.

Algunos de los comandos que se pueden ejecutar son:
- /users: Obtiene una lista de todos los clientes conectados al chat.
- /mymgs: Obtiene una lista de todos los mensajes que ha enviado al chat.
- /exit: Cierra su sesión de cliente del chat y libera el ID de usuario.

### Desplegar más contenedores clientes
Para poder desplegar más contenedores como clientes simplemente debe ingresar por línea de comando al directorio 'client' (donde está el Dockerfile). Una vez ahí, ejecutar:

`$docker build -t <nombre_temporal> .`  
`$docker run -it --network=actividad2_default <nombre_temporal> bash`
	
Donde "nombre_temporal" es un nombre que usted debe asignar para identificar al contenedor. El comando anterior inicia el contenedor y lo sitúa autompaticamente en su línea de comando.

Finalmente, dentro del contenedor ejecutar:

`$python client.py`

Si desea agregar más contenedores basta con volver a ejecutar el comando "docker run" sin necesidad de construir antes, ya que la imagen está construida. Esto debe hacerse en una nueva terminal para cada nuevo cliente.

### Comentarios generales
- Para efectos de esta tarea se asume que los clientes solo liberarán su id de usuario cuando estos se desconecten manualmente.
- Los registros en el server se guardan en memoria; en la realidad bastaría con implementar una base de datos.
- El chat imprime la fecha en que un mensaje llegó al server para lograr consistencia, sin embargo los mensajes tienen ambos timestamp (cliente y server). En el archivo "log.txt" se guardan todos estos registros.
- La hora está en formato UTC.
