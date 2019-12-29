## Actividad 1

### Desplegar arquitectura
- Para ejecutar la actividad 1, debe ingresar a la carpeta *Actividad1* y ejecutar:

  `$sudo docker-compose build`  
	`$sudo docker-compose up`

### Interacción cliente-servidor
- Para controlar el cliente, se debe abrir una nueva terminal, ingresar a *Actividad1/client* y ejecutar:

	`$sudo docker ps`  
	`$sudo docker exec -it <nombre contenedor> bash`  
	`#python3 client.py`

- **Observaciones:** 
	- *nombre contenedor* suele tener la forma ***actividad1_client_1***.
	- El último comando se puede ejecutar reiteradamente según se requiera.

- A continuación estará ejecutando el cliente quien solicitará que ingrese un mensaje para ser enviado al servidor.

### Consideraciones generales
- ***IMPORTANTE:*** Se recomienda utilizar el comando `$sudo docker-compose down` antes de cada inicialización de arquitectura, con el objetivo de realizar un montaje limpio.

- El tiempo del log registrado en los archivos de registros se encuentra en sistema horario UTC. 

**Nota**:  Para encontrar el nombre de los contenedores, en caso de requerirse se puede utilizar el comando `$sudo docker ps`.
