# Instalación y despliegue

[Español](INSTALL.md) | [English](INSTALL.en.md)

[Inicio](../README.md) · [Proyecto](PROJECT.md) · [Guía de uso](USER_GUIDE.md)

**La appliance OVA para VMware es la distribución principal de CENTAURUS.** Elige a continuación la modalidad que necesites; cada guía contiene sus requisitos, preparación y procedimiento detallado.

## 1. OVA VMware — distribución principal

Appliance preconstruida con el framework, las herramientas y el modelo local preparados. Es el punto de partida para utilizar CENTAURUS en una máquina virtual.

[Despliegue OVA](DEPLOYMENT_OVA.md)

## 2. Imagen USB arrancable

Imagen de disco completo para arrancar la appliance desde un dispositivo USB en hardware compatible. Incluye persistencia en el propio medio.

[Despliegue USB](DEPLOYMENT_USB.md)

## 3. Git + Docker sobre Linux

Alternativa para construir y desplegar CENTAURUS desde el repositorio en un host Linux, administrando las imágenes y los directorios persistentes.

[Despliegue Git + Docker](DEPLOYMENT_GIT_DOCKER.md)

## 4. Core local en Windows

Opción para desarrollo y ejecución local del Core. Su alcance no equivale al de la appliance completa ni garantiza paridad de todas las herramientas.

[Despliegue Windows](DEPLOYMENT_WINDOWS.md)

## 5. Después del despliegue

- [Guía de uso](USER_GUIDE.md) — primera sesión e interpretación de resultados.
- [Configuración](CONFIGURATION.md) — ajustes admitidos según la modalidad.
- [Resolución de problemas](TROUBLESHOOTING.md) — resolución de problemas común a las modalidades de despliegue.
