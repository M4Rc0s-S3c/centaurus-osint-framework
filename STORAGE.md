# STORAGE.md

# Arquitectura de Almacenamiento
## CENTAURUS OSINT Framework

**Versión:** MVP v1.0  
**Estado:** Diseño congelado

---

# 1. Objetivo

Este documento define la arquitectura de almacenamiento de **CENTAURUS OSINT Framework**, estableciendo la organización física y lógica del sistema, así como los criterios de persistencia de datos, separación de componentes y escalabilidad.

La arquitectura se ha diseñado siguiendo un principio fundamental:

> **Separar completamente el sistema operativo, la plataforma del framework y los datos generados durante los análisis.**

Esta separación facilita el mantenimiento del sistema, simplifica las tareas de actualización y permite conservar las evidencias generadas independientemente del estado del sistema operativo.

---

# 2. Principios de diseño

La arquitectura de almacenamiento se basa en los siguientes principios:

- Separación física entre sistema, plataforma y datos.
- Independencia del Core respecto al almacenamiento.
- Persistencia de informes y evidencias.
- Compatibilidad con Docker.
- Portabilidad de la distribución.
- Facilidad de ampliación.
- Simplicidad de administración.
- Compatibilidad con futuras versiones del framework.

---

# 3. Arquitectura física

La primera versión del framework utiliza **tres discos virtuales independientes**, cada uno destinado a una función específica.

| Disco | Tamaño | Punto de montaje | Función |
|--------|--------:|------------------|----------|
| Disco 1 | 5 GB | `/` | Sistema operativo Debian |
| Disco 2 | 15 GB | `/opt/osint-framework` | Plataforma del framework |
| Disco 3 | 10 GB | `/workspace` | Datos persistentes |

Esta separación permite ampliar cada volumen de forma independiente sin afectar al resto de componentes.

---

# 4. Firmware

La distribución utilizará firmware **UEFI**.

Se crea una partición EFI independiente para alojar el cargador de arranque.

| Partición | Tamaño | Sistema de archivos | Punto de montaje |
|-----------|--------:|---------------------|------------------|
| EFI | 512 MB | FAT32 | `/boot/efi` |

La partición EFI se utilizará exclusivamente para el proceso de arranque del sistema.

---

# 5. Sistemas de archivos

Las particiones Linux utilizarán el sistema de archivos **ext4**.

Se ha seleccionado ext4 por ofrecer:

- estabilidad;
- soporte completo de permisos POSIX;
- journaling;
- compatibilidad con Docker;
- excelente rendimiento;
- amplia madurez.

La siguiente tabla resume la configuración:

| Punto de montaje | Sistema de archivos | Label |
|------------------|---------------------|--------|
| `/boot/efi` | FAT32 | EFI |
| `/` | ext4 | SYSTEM |
| `/opt/osint-framework` | ext4 | PLATFORM |
| `/workspace` | ext4 | WORKSPACE |

---

# 6. Organización de la plataforma

Toda la plataforma se instalará bajo:

```text
/opt/osint-framework/
```

La estructura inicial será:

```text
/opt/osint-framework/
├── centaurus/      ← Repositorio Git
├── runtime/        ← Estado de ejecución de la plataforma
│   ├── docker/
│   ├── containerd/
│   └── ollama/
├── models/         ← Modelos LLM
├── cache/          ← Caché persistente
└── lost+found/
```

Descripción:

| Directorio | Función |
|------------|---------|
| centaurus | Repositorio Git del proyecto (código, documentación y configuración versionada). |
| runtime | Estado de ejecución de la plataforma (Docker, containerd y Ollama). |
| models | Modelos LLM persistentes utilizados por Ollama. |
| cache | Caché persistente de la plataforma. |
---

# 7. Organización del Workspace

Toda la información generada durante los análisis se almacenará bajo:

```text
/workspace/
```

La estructura será:

```text
/ workspace

├── reports/
├── evidence/
├── logs/
├── cache/
└── tmp/
```

Descripción:

| Directorio | Función |
|------------|---------|
| reports | Informes generados |
| evidence | Evidencias obtenidas |
| logs | Registros del framework |
| cache | Información temporal |
| tmp | Archivos temporales |

---

# 8. Persistencia de datos

El Workspace constituye la única zona persistente utilizada por el framework.

Las actualizaciones del sistema operativo o de la plataforma no deberán modificar el contenido de esta ubicación.

Los informes, evidencias y registros permanecerán disponibles independientemente de las actualizaciones realizadas.

Además del Workspace, la plataforma mantiene un área de ejecución independiente en:

```text
/opt/osint-framework/runtime
```
Este directorio almacena el estado interno de Docker, containerd y Ollama, separándolo del sistema operativo y del repositorio Git.

Los modelos de lenguaje se almacenan de forma independiente en:
```text
/opt/osint-framework/models
```
Esta organización permite reinstalar el código del framework sin afectar al runtime ni a los modelos descargados.


---

# 9. Integración con Docker

Los contenedores Docker accederán al Workspace mediante volúmenes persistentes.

El directorio:

```text
/workspace
```

será montado dentro de los contenedores cuando sea necesario.

De esta forma:

- los contenedores permanecen efímeros;
- los datos sobreviven a su eliminación;
- la actualización de imágenes Docker no afecta a las evidencias generadas.


Asimismo, Docker utiliza un directorio de datos dedicado dentro de la plataforma:

```text
/opt/osint-framework/runtime/docker

```
containerd utiliza igualmente un directorio específico:
```text
/opt/osint-framework/runtime/containerd

```
De este modo, todo el estado de ejecución de la plataforma permanece fuera del sistema operativo y centralizado bajo /opt/osint-framework/runtime.
---

# 10. Acceso desde Windows

Aunque el Workspace utiliza el sistema de archivos **ext4**, será posible acceder a los informes y evidencias desde un sistema Windows utilizando herramientas de lectura de particiones Linux.

La utilidad recomendada es:

- **DiskInternals Linux Reader**

Esta herramienta permite acceder al contenido de la partición en modo de solo lectura, evitando modificaciones accidentales sobre las evidencias almacenadas.

---

# 11. Dimensionamiento del MVP

La configuración inicial del proyecto será:

| Elemento | Tamaño |
|----------|--------:|
| Partición EFI | 512 MB |
| Sistema | 5 GB |
| Plataforma | 15 GB |
| Workspace | 10 GB |

Capacidad total aproximada:

**30 GB**

Esta configuración permite desplegar completamente el framework en un dispositivo USB de **32 GB**.

---

# 12. Justificación técnica

La arquitectura propuesta presenta las siguientes ventajas:

- separación completa entre sistema, plataforma y datos;
- mayor facilidad de mantenimiento;
- posibilidad de ampliar discos individualmente;
- compatibilidad con Docker;
- compatibilidad con Ollama;
- protección de las evidencias;
- facilidad para realizar copias de seguridad;
- portabilidad del framework.
- separación entre código fuente, runtime y modelos de IA;
- centralización del estado de ejecución de Docker, containerd y Ollama.

---

# 13. Evolución futura

En futuras versiones podrán ampliarse los discos virtuales desde la plataforma de virtualización (VMware).

Tras ampliar el tamaño del disco únicamente será necesario extender el sistema de archivos correspondiente mediante herramientas estándar de Linux, sin modificar la arquitectura del framework.

Esta estrategia garantiza la escalabilidad del sistema manteniendo la organización definida para el MVP.

---

# 14. Resumen

La arquitectura de almacenamiento de **CENTAURUS OSINT Framework** establece una separación clara entre sistema operativo, plataforma y datos persistentes.

Este diseño proporciona una base sólida para el desarrollo del proyecto, facilita su mantenimiento, favorece la portabilidad y permite evolucionar el framework sin modificar su estructura principal.
La separación entre repositorio Git, runtime de la plataforma, modelos LLM y Workspace garantiza una infraestructura modular, fácilmente mantenible y alineada con la filosofía de Infrastructure as Code adoptada por el proyecto.