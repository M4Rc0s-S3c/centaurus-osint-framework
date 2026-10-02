# Despliegue de la appliance OVA

[Español](DEPLOYMENT_OVA.md) | [English](DEPLOYMENT_OVA.en.md)

[Inicio](../README.md) · [INSTALL.md](INSTALL.md) · [USER_GUIDE.md](USER_GUIDE.md)

## 1. Alcance y requisitos

La OVA distribuye una appliance preconstruida con Debian, Docker, Core, herramientas y Ollama con `qwen3:4b`. No requiere clonar el repositorio ni ejecutar el bootstrap de Git + Docker dentro de la máquina virtual.

Utiliza un entorno VMware compatible con importación OVA y con el perfil de hardware x86-64 incluido. Reserva capacidad para importar los discos virtuales y conservar el crecimiento del workspace. El tamaño de la descarga no representa todo el espacio de ejecución necesario.

Perfil de recursos de la máquina virtual documentado para la distribución:

| Recurso | Asignación |
| --- | --- |
| CPU | 8 vCPU |
| Memoria RAM | 8 GiB |
| Almacenamiento virtual | 29 GiB totales en tres discos |
| Disco SYSTEM | 5 GiB |
| Disco PLATFORM | 17 GiB |
| Disco WORKSPACE | 7 GiB |

Son recursos asignados a la appliance, no los requisitos totales del host. Reserva memoria y espacio adicionales para el sistema operativo del host, la OVA descargada, snapshots y copias. La capacidad de los discos virtuales es distinta del tamaño del fichero OVA y del espacio que ocupen sus ficheros en cada momento.

La configuración de referencia utiliza tres discos lógicos: SYSTEM, PLATFORM y WORKSPACE. Para el primer arranque conserva el perfil de hardware incluido, su firmware y la interfaz E1000 con red NAT. La baseline funciona con CPU; la aceleración GPU no es un requisito.

## 2. Descarga e identidad

[CENTAURUS-C4-FINAL.ova — Google Drive](https://drive.google.com/drive/folders/1Anvan2lh-KQzQMDvvv_nTqSjfdSnTpdT?usp=sharing)

Conserva una copia original para futuras importaciones.

| Propiedad | Valor |
| --- | --- |
| Fichero | `CENTAURUS-C4-FINAL.ova` |
| Tamaño en bytes | `11828618752` |
| SHA-256 | `d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868` |

En Linux:

```bash
stat -c '%s' CENTAURUS-C4-FINAL.ova
sha256sum CENTAURUS-C4-FINAL.ova
```

En PowerShell:

```powershell
(Get-Item .\CENTAURUS-C4-FINAL.ova).Length
Get-FileHash .\CENTAURUS-C4-FINAL.ova -Algorithm SHA256
```

Comprueba que tamaño y hash coinciden exactamente antes de importar. Ante una discrepancia, conserva el diagnóstico y vuelve a obtener el artefacto correcto.

## 3. Importación

1. Abre la función de importación/apertura de OVA de VMware y selecciona el fichero verificado.
2. Asigna un nombre y una ubicación con espacio suficiente para la máquina virtual.
3. Revisa que se conserven los tres discos, el firmware importado y el adaptador de red previsto. Evita cambios de controladoras durante la importación inicial.
4. Completa la importación y arranca la appliance desde su consola.

El primer arranque prepara la identidad local de la instancia, incluidos `machine-id` y claves de host SSH. La presencia de estas claves no implica que deba publicarse SSH ni abrir puertos adicionales para utilizar CENTAURUS.

## 4. Primera sesión

Credenciales iniciales de la appliance:

| Cuenta | Usuario | Contraseña |
| --- | --- | --- |
| Analista | `centaurus` | `centaurus` |
| Administración | `root` | `root` |

Cambia estas credenciales si la appliance va a seguir utilizándose. Accede a la consola como `centaurus`.

En una TTY interactiva:

```bash
centaurus
```

El wrapper no acepta argumentos y solicita autenticación nueva. Abre el shell del Core a través del broker; el usuario analista no necesita acceso directo al daemon Docker. Consulta [`USER_GUIDE.md`](USER_GUIDE.md) para la sesión y la lectura de resultados.

La inferencia utiliza el modelo local. Las consultas OSINT requieren conectividad con las fuentes externas correspondientes; disponer del modelo no convierte la recopilación en un proceso sin red.

## 5. Comprobaciones operativas

Desde el host de la appliance, el administrador puede revisar:

```bash
ip -br addr show centaurus0
ip route
findmnt /workspace
systemctl --failed --no-pager
```

La interfaz lógica esperada es `centaurus0`, con configuración por DHCP. Para fallos de red o de arranque, consulta [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## 6. Persistencia y mantenimiento

Las investigaciones se conservan en `/workspace`; su estructura se describe en [`STORAGE.md`](STORAGE.md). Los logs operativos están en `/workspace/logs/centaurus.log`.

Antes de mantenimiento, termina las investigaciones y cierra la sesión del Core. Conserva una copia consistente del workspace y registra la identidad de la appliance. Una copia o snapshot de la VM apagada complementa el respaldo de resultados; no sustituye su política de retención.

La appliance no mantiene un checkout Git para actualizaciones ordinarias. No apliques dentro de ella los pasos de cambio de tag y bootstrap de la modalidad Git + Docker. Los cambios de runtime requieren un procedimiento administrativo que mantenga coherentes la imagen, la configuración y sus identidades verificadas.

## 7. Apagado

Sal del shell del Core y, desde la TTY del host como `centaurus`, ejecuta:

```bash
centaurus-poweroff
```

El comando acepta cero argumentos y solicita autenticación nueva. Espera a que finalice el apagado antes de cerrar o mover los ficheros de la máquina virtual.

## 8. Documentación relacionada

- [`CONFIGURATION.md`](CONFIGURATION.md)
- [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md)
- [`DEPLOYMENT_USB.md`](DEPLOYMENT_USB.md)
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
