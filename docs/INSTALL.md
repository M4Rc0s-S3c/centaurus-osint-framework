# Instalación y despliegue

[Español](INSTALL.md) | [English](INSTALL.en.md)

[Inicio](../README.md) · [PROJECT.md](PROJECT.md) · [USER_GUIDE.md](USER_GUIDE.md)

**La appliance OVA para VMware es la distribución principal de CENTAURUS.** Elige a continuación la modalidad que necesites; cada guía contiene sus requisitos, preparación y procedimiento detallado.

## 1. OVA VMware — distribución principal

Appliance preconstruida con el framework, las herramientas y el modelo local preparados. Es el punto de partida para utilizar CENTAURUS en una máquina virtual.

[`DEPLOYMENT_OVA.md`](DEPLOYMENT_OVA.md)

## 2. Imagen USB arrancable

Imagen de disco completo para arrancar la appliance desde un dispositivo USB en hardware compatible. Incluye persistencia en el propio medio.

[`DEPLOYMENT_USB.md`](DEPLOYMENT_USB.md)

## 3. Git + Docker sobre Linux

Alternativa para construir y desplegar CENTAURUS desde el repositorio en un host Linux, administrando las imágenes y los directorios persistentes.

[`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md)

## 4. Core local en Windows

Opción para desarrollo y ejecución local del Core. Su alcance no equivale al de la appliance completa ni garantiza paridad de todas las herramientas.

[`DEPLOYMENT_WINDOWS.md`](DEPLOYMENT_WINDOWS.md)

## 5. Después del despliegue

- [`USER_GUIDE.md`](USER_GUIDE.md) — primera sesión e interpretación de resultados.
- [`CONFIGURATION.md`](CONFIGURATION.md) — ajustes admitidos según la modalidad.
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) — resolución de problemas común a las modalidades de despliegue.
