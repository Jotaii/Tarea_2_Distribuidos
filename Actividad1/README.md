## Actividad 1

### Desplegar arquitectura (1 servidor - 2 clientes)
Desde linea de comandos y en la carpeta *Actividad1* ejecutar:

  `$docker-compose build`  
	`$docker-compose up`

### Interacción cliente-servidor
Para acceder a los contenedores clientes, se debe abrir una nueva terminal y ejecutar lo siguiente:
  
`$sudo docker exec -it actividad1_cliente1_1 bash`  
	
Dentro del contenedor ejecutar:

`$python client.py`

Luego, repetir el proceso en otra nueva terminal para el segundo contenedor cliente pero con el nombre "actividad1_cliente2_1".

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
Para poder desplegar más contenedores como clientes simplemente debe ingresar por línea de comando al directorio 'client'. Una vez ahí, ejecutar:

`$docker build -t <nombre_temporal> .`  
`$docker run -it <nombre_temporal> bash`
	
Donde "nombre_temporal" es un nombre que usted debe asignar para identificar al contenedor.

Finalmente, dentro de la línea de comando ejecutar:

`$python client.py`
