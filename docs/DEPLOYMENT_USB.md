# Despliegue de la imagen USB

[Español](DEPLOYMENT_USB.md) | [English](DEPLOYMENT_USB.en.md)

[Inicio](../README.md) · [INSTALL.md](INSTALL.md) · [USER_GUIDE.md](USER_GUIDE.md)

## 1. Alcance y requisitos

`CENTAURUS-USB.img` es una imagen raw de disco completo con la appliance y su particionado. Se escribe sobre un dispositivo físico; copiar el fichero a una carpeta del USB no crea el medio arrancable.

El equipo de destino debe admitir x86-64 y arranque UEFI. La validación de referencia se realizó en un Toshiba Z30-A con Ethernet Intel I218-V y controlador `e1000e`. Esa referencia no garantiza compatibilidad universal con otros adaptadores, Wi-Fi o GPU. La baseline utiliza CPU.

El dispositivo debe disponer de **al menos `31457280000` bytes reales**. Comprueba su capacidad en bytes: la etiqueta comercial «32 GB» no sustituye esa comprobación. Conserva espacio adicional para guardar la imagen original en el equipo que realizará la escritura.

## 2. Descarga y verificación

Utiliza el enlace de descarga publicado en [`INSTALL.md`](INSTALL.md).

| Propiedad | Valor |
| --- | --- |
| Fichero | `CENTAURUS-USB.img` |
| Tamaño en bytes | `31457280000` |
| Sectores de 512 bytes | `61440000` |
| SHA-256 | `7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165` |

En Linux:

```bash
stat -c '%s' CENTAURUS-USB.img
sha256sum CENTAURUS-USB.img
```

En PowerShell:

```powershell
(Get-Item .\CENTAURUS-USB.img).Length
Get-FileHash .\CENTAURUS-USB.img -Algorithm SHA256
```

No continúes si tamaño o hash difieren. La verificación identifica la descarga antes de escribir; no verifica por sí sola el dispositivo resultante.

## 3. Identificar el destino

**La escritura de la imagen sobrescribe la tabla de particiones y los datos del dispositivo seleccionado.** Respalda cualquier contenido que necesites conservar e identifica el disco por modelo, número de serie y capacidad. No lo selecciones únicamente por una letra de unidad o por el orden de aparición.

En Linux, consulta el inventario sin modificarlo:

```bash
lsblk -b -o NAME,SIZE,MODEL,SERIAL,TRAN,TYPE,MOUNTPOINTS
```

En PowerShell:

```powershell
Get-Disk | Select-Object Number,FriendlyName,SerialNumber,Size,BusType,IsBoot,IsSystem
```

Selecciona el **disco USB completo**, nunca una partición ni el disco del sistema. Desconecta otros medios extraíbles si ayuda a evitar confusiones. Cierra las aplicaciones que accedan al destino y desmonta sus volúmenes antes de escribir.

## 4. Escritura raw

1. Abre una herramienta de escritura de imágenes raw que permita seleccionar un disco físico, con los permisos administrativos necesarios.
2. Selecciona `CENTAURUS-USB.img` como origen y vuelve a contrastar la identidad y capacidad del destino.
3. Utiliza escritura directa de la imagen completa, conservando su particionado. No elijas extracción de ficheros ni conversión a instalador ISO.
4. Confirma el borrado únicamente del dispositivo identificado y deja terminar la escritura y el vaciado de buffers.
5. Si la herramienta ofrece verificación posterior, ejecútala antes del primer arranque. En dispositivos mayores, compara la región escrita de longitud `31457280000` bytes, no el hash de todo el dispositivo.
6. Expulsa el medio de forma segura. Si el sistema propone formatear particiones que no reconoce, cancela esa propuesta.

Un dispositivo reutilizado y mayor que la imagen puede conservar metadatos de un particionado anterior fuera de la región sobrescrita, incluida una copia GPT al final físico. Su preparación requiere revisión administrativa previa, identificación inequívoca y respaldo. No aceptes reparaciones automáticas de GPT ni ampliaciones de particiones como parte de este procedimiento. El espacio adicional sin asignar no implica que el workspace se haya ampliado.

## 5. Primer arranque y uso

Conecta el USB al equipo de destino y elige su entrada UEFI en el menú de arranque. Conserva los discos internos fuera del procedimiento de escritura; arrancar la appliance no requiere instalarla sobre ellos.

Inicia sesión como `centaurus` usando las credenciales publicadas en [`INSTALL.md`](INSTALL.md). Cámbialas si el medio va a seguir utilizándose. Desde una TTY interactiva:

```bash
centaurus
```

El wrapper acepta cero argumentos y pide autenticación nueva. El shell y la interpretación de resultados se describen en [`USER_GUIDE.md`](USER_GUIDE.md).

La interfaz lógica de referencia es `centaurus0` por DHCP. El administrador puede revisar `ip -br addr`, `ip route` y `findmnt /workspace`. Si no aparece una interfaz utilizable, revisa la compatibilidad del hardware antes de atribuir el problema a una fuente OSINT. La recopilación necesita red aunque el modelo LLM sea local.

## 6. Persistencia y apagado

El workspace persiste en el propio medio. Haz copias consistentes de `/workspace` con las investigaciones detenidas, conforme a [`STORAGE.md`](STORAGE.md). El desgaste, la pérdida o la extracción accidental del USB pueden afectar a esos datos.

Sal del shell del Core y ejecuta desde la TTY del host:

```bash
centaurus-poweroff
```

Espera al apagado completo antes de retirar el USB. El sistema modifica el medio durante su uso; después del primer arranque ya no se espera que la región escrita conserve el hash de la imagen de distribución.

## 7. Documentación relacionada

- [`DEPLOYMENT_OVA.md`](DEPLOYMENT_OVA.md)
- [`CONFIGURATION.md`](CONFIGURATION.md)
- [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md)
