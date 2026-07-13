# INSTALL.md

# CENTAURUS OSINT Framework
## Guía de instalación

---

# 1. Objetivo

Este documento describe el procedimiento completo para desplegar la plataforma **CENTAURUS OSINT Framework** desde una instalación limpia de Debian.

El objetivo es garantizar que cualquier despliegue genere exactamente la misma estructura de almacenamiento, configuración del sistema y componentes de la plataforma.

---

# 2. Requisitos

## Hardware recomendado

| Recurso | Valor |
|----------|-------|
| CPU | 8 vCPU |
| Memoria RAM | 8 GB |
| Almacenamiento | 30 GB |

Distribución de discos:

| Disco | Tamaño | Uso |
|--------|---------|---------------------------|
| Disco 1 | 5 GB | Sistema Operativo |
| Disco 2 | 15 GB | Plataforma |
| Disco 3 | 10 GB | Workspace |

---

# 3. Sistema operativo

Distribución:

- Debian 13.5 AMD64 Netinstall

Modo de instalación:

- UEFI
- Instalación mínima
- Instalador en modo texto

---

# 4. Particionado

## Disco Sistema (5 GB)

| Partición | Tamaño | Formato | Punto de montaje |
|------------|---------|----------|------------------|
| EFI | 512 MB | FAT32 | /boot/efi |
| SYSTEM | Resto | ext4 | / |

## Disco Plataforma (15 GB)

| Partición | Formato | Label | Punto de montaje |
|------------|----------|-----------|------------------------|
| PLATFORM | ext4 | PLATFORM | /opt/osint-framework |

## Disco Workspace (10 GB)

| Partición | Formato | Label | Punto de montaje |
|------------|----------|-----------|----------------|
| WORKSPACE | ext4 | WORKSPACE | /workspace |

---

# 5. Primer arranque

Actualizar el sistema:

```bash
apt update
apt upgrade -y
```

---

# 6. Configuración del almacenamiento

Crear el punto de montaje de la plataforma:

```bash
mkdir -p /opt/osint-framework
```

Editar:

```bash
nano /etc/fstab
```

Configuración:

```fstab
# /
UUID=<SYSTEM_UUID>                 /                      ext4    errors=remount-ro 0 1

# EFI
UUID=<EFI_UUID>                    /boot/efi              vfat    umask=0077 0 1

# Workspace
UUID=<WORKSPACE_UUID>              /workspace             ext4    defaults 0 2

# Plataforma
UUID=<PLATFORM_UUID>               /opt/osint-framework   ext4    defaults 0 2

# CDROM
/dev/sr0                           /media/cdrom0          udf,iso9660 user,noauto 0 0
```

Recargar la configuración:

```bash
systemctl daemon-reload
mount -a
```

Verificar:

```bash
lsblk -f
```

---

# 7. Validación de la infraestructura

Comprobar:

- Particiones correctamente montadas.
- Acceso a Internet.
- Resolución DNS.
- Sincronización horaria.
- Hostname configurado.
- Acceso mediante SSH desde un equipo Windows.

---

# 8. Snapshot de la infraestructura

Crear una instantánea VMware.

Nombre recomendado:

```
01 - Infraestructura Base
```

A continuación crear un **Full Clone** para el desarrollo.

---

# 9. Instalación de Git

Instalar Git:

```bash
apt install -y git
```

Configurar la identidad:

```bash
git config --global user.name "Nombre Apellidos"
git config --global user.email "correo@dominio.com"
```

Verificar:

```bash
git config --list
```

---

# 10. Configuración de GitHub mediante SSH

Generar la clave ED25519:

```bash
ssh-keygen -t ed25519 -C "correo@dominio.com"
```

Aceptar la ubicación por defecto:

```
/root/.ssh/id_ed25519
```

Mostrar la clave pública:

```bash
cat ~/.ssh/id_ed25519.pub
```

Añadir la clave en GitHub:

```
Settings
 └── SSH and GPG Keys
      └── New SSH Key
```

Verificar la conexión:

```bash
ssh -T git@github.com
```

Resultado esperado:

```
You've successfully authenticated, but GitHub does not provide shell access.
```

---

# 11. Clonado del repositorio

Repositorio remoto:

```
git@github.com:<usuario>/centaurus-osint-framework.git
```

Clonado:

```bash
cd /opt/osint-framework

git clone git@github.com:<usuario>/centaurus-osint-framework.git centaurus
```

La estructura queda:

```
/opt/osint-framework
├── centaurus
└── lost+found
```

> **Nota:** No se recomienda clonar directamente sobre `/opt/osint-framework`, ya que las particiones ext4 crean automáticamente el directorio `lost+found`, impidiendo utilizar `git clone ... .`.

---

# 12. Estado alcanzado

Al finalizar esta fase la infraestructura deberá disponer de:

- Debian 13 instalado.
- UEFI configurado.
- Arquitectura de almacenamiento implementada.
- Puntos de montaje operativos.
- Red validada mediante DHCP.
- OpenSSH operativo.
- Snapshot de infraestructura.
- Clon de desarrollo.
- Git instalado.
- Autenticación SSH con GitHub.
- Repositorio clonado correctamente.
- Docker Engine instalado.
- Docker Compose operativo.
- Runtime de Docker desacoplado del sistema operativo.
- Runtime de containerd desacoplado del sistema operativo.
- Runtime de Ollama desacoplado del repositorio.
- Contenedor `centaurus-ollama` desplegado.
- Red Docker `centaurus-network` creada.

---

# 13. Instalación de la plataforma

Una vez preparada la infraestructura base, se procede a la instalación de la plataforma CENTAURUS.


# 14. Próximos pasos

Con la plataforma base instalada, la siguiente fase consiste en iniciar el desarrollo del framework.

Los siguientes hitos son:

- estructura inicial del Core;
- gestor de configuración;
- sistema de logging;
- gestor del Workspace;
- motor de plugins;
- Rule Engine;
- integración progresiva de herramientas OSINT.

## Docker Engine

Instalar Docker Engine desde el repositorio oficial de Docker para Debian.

Verificar la instalación:

```bash
docker version
docker info
```

## Docker Compose

Verificar la disponibilidad del plugin Compose:

```bash
docker compose version
```

## Configuración del runtime

Docker utilizará un directorio de datos dedicado:

```text
/opt/osint-framework/runtime/docker
```

containerd utilizará igualmente un directorio específico:

```text
/opt/osint-framework/runtime/containerd
```

El runtime de Ollama se almacenará en:

```text
/opt/osint-framework/runtime/ollama
```

Los modelos LLM se almacenarán de forma independiente en:

```text
/opt/osint-framework/models
```

Esta organización mantiene separado el estado de ejecución, los modelos y el código fuente del framework.

## Despliegue inicial

Desde el repositorio:

```bash
cd /opt/osint-framework/centaurus/docker
```

Validar la configuración:

```bash
docker compose config
```

Iniciar los servicios:

```bash
docker compose up -d
```

Verificar:

```bash
docker compose ps
docker ps
```

## Validación

La instalación se considera correcta cuando:

- Docker Engine está operativo.
- Docker Compose funciona correctamente.
- El contenedor `centaurus-ollama` se encuentra en ejecución.
- La red `centaurus-network` ha sido creada.
- Docker utiliza `/opt/osint-framework/runtime/docker`.
- containerd utiliza `/opt/osint-framework/runtime/containerd`.
- Ollama almacena su runtime en `/opt/osint-framework/runtime/ollama`.
- Los modelos LLM se almacenan en `/opt/osint-framework/models`.

---

# Historial

| Versión | Fecha | Cambios |
|----------|--------|---------|
| 0.3 | Julio 2026 | Documentada la instalación de Docker Engine, Docker Compose, la arquitectura de runtime (Docker, containerd y Ollama), el despliegue inicial mediante Docker Compose y la validación de la plataforma. |
| 0.2 | Julio 2026 | Añadida la preparación del entorno de desarrollo (red, OpenSSH, Git, GitHub SSH y repositorio). |
| 0.1 | Julio 2026 | Documento inicial. |