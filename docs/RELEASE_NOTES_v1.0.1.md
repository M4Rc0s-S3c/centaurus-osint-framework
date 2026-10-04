# CENTAURUS v1.0.1 — Release documental

[Español](RELEASE_NOTES_v1.0.1.md) | [English](RELEASE_NOTES_v1.0.1.en.md)

[Inicio](../README.md) · [Proyecto](PROJECT.md)

## Alcance

Esta release consolida la documentación pública y la limpieza del repositorio. El código de aplicación, las pruebas, los locks de dependencias, `pyproject.toml`, los scripts de despliegue y la configuración Docker no cambian respecto a `v1.0.0`. No añade funciones al runtime ni declara nuevas validaciones de hardware.

## Cambios

- Guías en español e inglés organizadas por finalidad, con navegación y presentación uniformes.
- Ampliación de instrucciones de despliegue, configuración, resolución de problemas y respaldo.
- Referencias técnicas de plugins, arquitectura LLM, ciclo del Core y pruebas.
- Explicación más precisa de resultados deterministas, trazabilidad directa/inversa, modularidad y contenido persistido del informe.
- DHCP identificado como valor predeterminado de la appliance, con instrucciones administrativas de IPv4 estática.
- Limpieza del repositorio, aclaración de atribución y retirada de marcadores de carpetas sin uso.

## Identidades de versión

| Elemento | Identidad |
| --- | --- |
| Release/tag del repositorio | `v1.0.1`, exclusivamente documental |
| Paquete Python | `0.4.0-dev`, normalizado como `0.4.0.dev0` |
| Artefactos de appliance existentes | OVA/USB distribuidos previamente; sin cambios |
| Nombre del paquete de construcción del Core | `centaurus-core-build_v1.0.zip`; nombre interno sin cambios |

`centaurus --version` muestra la versión del paquete, no la etiqueta de release del repositorio. Las instalaciones existentes no necesitan actualizar el software por estos cambios documentales. El tag `v1.0.0` y la entrega académica permanecen intactos.

## Descargas OVA y USB

Se reutilizan los artefactos existentes mediante las guías de [despliegue OVA](DEPLOYMENT_OVA.md) y [despliegue USB](DEPLOYMENT_USB.md). No se publica una appliance de sustitución. Se conservan sus identidades originales:

| Artefacto | Tamaño en bytes | SHA-256 |
| --- | --- | --- |
| `CENTAURUS-C4-FINAL.ova` | `11828618752` | `d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868` |
| `CENTAURUS-USB.img` | `31457280000` | `7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165` |

Los archivos automáticos Source code ZIP/TAR de GitHub contienen el repositorio en este tag, no la OVA ni la imagen USB. El bootstrap Linux requiere un checkout Git; el ZIP de fuentes no sustituye ese checkout.

## Verificación y límites

Se han comparado las entradas del runtime con `v1.0.0`. El paquete determinista de construcción del Core es idéntico byte a byte, con SHA-256 `f580177c286afc71a2e3ab423d5ba5316d277112601af92e550d21ac92247463`. Se han comprobado enlaces relativos, anclajes y coherencia ES/EN.

Esto no constituye una nueva construcción Docker, ejecución completa de la suite Python, instalación Windows, importación OVA, arranque USB, prueba de IP estática en la appliance ni validación GPU. Las validaciones anteriores conservan su alcance original; la guía GPU sigue siendo experimental.
