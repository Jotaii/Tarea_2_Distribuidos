# Actividad 1

## Descripción 
En esta actividad se debe crear un chat donde será posible que hayan n-clientes y un servidor central  de  coordinación  de  mensajes.  Para  esta  actividad  se  debe  usar  el  framework  gRPC para implementar el sistema de mensajería usando el protocolo RPC(Remote Procedure Call).

## Desplegar arquitectura (1 servidor - 2 clientes)
Antes de desplegar la arquitectura es importante mencionar que para poder entrar a la línea de comando de cada cliente es necesario ejecutar cada uno en una nueva terminal, por lo que es importante seguir los pasos que vienen a continuación.

### Desplegar servidor y clientes iniciales

Desde linea de comandos y en la carpeta *Actividad1* ejecutar:

  `$docker-compose build`  
	`$docker-compose up`

Esto desplegará los contenedores del servidor y dos clientes.

### Interacción clientes
Para acceder al chat del primer cliente es necesario abrir una nueva terminal y en la carpeta de la actividad ejecutar:

`$docker-compose exec client1 bash`

Una vez dentro del contenedor, conectarse al chat mediante el siguiente comando:

`$python client.py`

El programa le preguntará un nombre de usuario.

Luego, repetir el proceso en otra nueva terminal para el segundo contenedor cliente pero con el nombre "client2".

**Observaciones:** 
	Es necesario hacerlo siempre en nuevas terminales para poder tener acceso a la linea de comando de cada chat como usuarios distintos.
	
### Instrucciones del chat
Al iniciar el chat como cliente se le pedirá ingresar un nombre de usuario (ID del cliente). Si el nombre ingresado ya existe, debe escoger otro para poder ingresar al chat.
Una vez que logra entrar puede comenzar a escribir mensajes. Basta con solo escribir, ya que el historial del chat se actualiza solo. Todos los mensajes enviados se registran en el archivo 'log.txt' almacenado en la carpeta 'server'.

Algunos de los comandos que se pueden ejecutar son:
- /users: Obtiene una lista de todos los clientes conectados al chat.
- /mymessages: Obtiene una lista de todos los mensajes que ha enviado al chat.
- /exit: Cierra su sesión de cliente del chat y libera el ID de usuario.

### Desplegar más contenedores clientes
Para poder desplegar más contenedores como clientes simplemente debe ingresar por línea de comando al directorio 'client' (donde está el Dockerfile). Una vez ahí, ejecutar:

`$docker build -t <nombre_temporal> .`  
`$docker run -it --network=actividad1_default <nombre_temporal> bash`
	
Donde "nombre_temporal" es un nombre que usted debe asignar para identificar al contenedor. El comando anterior inicia el contenedor y lo sitúa autompaticamente en su línea de comando.

Finalmente, dentro del contenedor ejecutar:

`$python client.py`

Si desea agregar más contenedores basta con volver a ejecutar el comando "docker run" sin necesidad de construir antes, ya que la imagen está construida. Esto debe hacerse en una nueva terminal para cada nuevo cliente.
