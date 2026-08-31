# Visión general del proyecto

**Estado:** FINAL · implementación y aceptación técnica cerradas en el alcance del TFM

## 1. Identidad

**CENTAURUS OSINT Framework** es un framework modular de inteligencia de fuentes abiertas orientado a equipos Blue Team y departamentos IT de PYMEs. Forma parte de una distribución Linux autocontenida diseñada para realizar evaluaciones pasivas y trazables de exposición pública.

## 2. Objetivo

Proporcionar un entorno local, trazable y extensible capaz de:

- interpretar una petición de investigación en lenguaje natural;
- construir una `Investigation` estructurada;
- planificar de forma determinista las capacidades a ejecutar;
- ejecutar tools OSINT mediante plugins;
- preservar observaciones originales y normalizadas;
- producir Findings mediante Rules deterministas;
- consolidar el conocimiento en un Report persistente;
- presentar el resultado al analista mediante CLI y asistencia LLM local acotada.

## 3. Usuarios objetivo

- equipos Blue Team;
- departamentos IT de PYMEs;
- analistas de seguridad que necesiten una primera evaluación pasiva de exposición pública.

El TFM original menciona también consultoría e investigación de seguridad como contexto posible, pero el dominio funcional congelado se centra en **Public Exposure Assessment**.

## 4. Alcance funcional

### Target DOMAIN

Cobertura completa de la versión documentada mediante WHOIS, RDAP, DNSRecon, Sublist3r, crt.sh y TheHarvester.

### Target IP

Cobertura limitada mediante RDAP.

### EMAIL y CERTIFICATE

Se conservan como conceptos de evolución/futuro. EMAIL no es Target operacional en la CLI vigente y CERTIFICATE permanece diferido como Investigation directa.

## 5. Arquitectura

CENTAURUS separa:

- interfaz e interpretación de entrada;
- orquestación Core;
- planificación y ejecución;
- tools/plugins;
- Knowledge Pipeline;
- Rules/RuleEngine;
- reporting;
- IA auxiliar;
- persistencia;
- infraestructura Docker/Ollama.

El Core es el único custodio del lifecycle de `Investigation`. `Planner` selecciona las capacidades; ningún LLM ejecuta tools ni genera Findings.

## 6. Inteligencia artificial: dos roles lógicos

CENTAURUS utiliza el mismo servicio/modelo físico para dos responsabilidades distintas:

- **LLM #1 — interpretación de entrada.** Propone exclusivamente un `Intent` del catálogo permitido dentro de `RequestInterpreter`. El Target se detecta y normaliza localmente. Si LLM #1 no puede producir una salida válida, la petición natural falla de forma cerrada antes de comenzar la investigación.
- **LLM #2 — asistencia posterior al Report.** Trabaja después de existir el Report determinista y persistido. Produce una vista efímera de síntesis/explicación/advisory. Su fallo no modifica Evidence, Findings ni Report.

La validación física final corroboró esta separación: una petición natural llegó a un Intent válido e inició una investigación real, lo que es coherente con la función de LLM #1 en el entrypoint normal. LLM #2 agotó el timeout de 300 s en hardware antiguo y el resultado autoritativo siguió disponible.

## 7. Tecnologías del estado final

| Área | Tecnología/decisión |
|---|---|
| Sistema objetivo | Debian GNU/Linux 13 |
| Framework | Python 3.12 en la imagen de entrega |
| Contenedorización | Docker + Docker Compose |
| CLI | Typer + Rich + Prompt Toolkit |
| HTTP | httpx |
| LLM local | Ollama |
| Modelo | `qwen3:4b` |
| Perfil LLM #2 D2 | `timeout=300`, `num_ctx=8192`, `num_predict=UNSET`, `think=false`, `keep_alive=0` |
| Persistencia | Filesystem + JSON |
| Logging | `logging` stdlib + RotatingFileHandler |
| Testing | pytest |

Pydantic, pydantic-settings, orjson y loguru aparecieron en formulaciones iniciales, pero no forman parte del runtime final documentado porque no existía necesidad demostrada.

## 8. Distribución y artefactos finales

La misma entrega puede consumirse mediante tres rutas:

- **OVA**: appliance Debian preconstruida y validada.
- **Git + Docker Linux**: despliegue reproducible desde una revisión Git fijada.
- **USB**: appliance física x86-64/UEFI materializada desde una imagen raw de 30.000 MiB.

Autoridades finales:

- OVA: `CENTAURUS-C4-FINAL.ova`, 11.828.618.752 bytes, SHA-256 `d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868`.
- imagen USB: `CENTAURUS-USB.img`, 31.457.280.000 bytes, SHA-256 `7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165`.

La imagen USB fue validada tras materialización física, arranque en VMware y, posteriormente, en bare-metal sobre un Toshiba Portege Z30-A con NIC Intel I218-V/e1000e. La política portable materializó la interfaz como `centaurus0`, obtuvo enlace Ethernet, DHCP y ruta por defecto. Esta evidencia **no** se extrapola a compatibilidad universal de hardware.

## 9. Qué no es CENTAURUS

No es un agente autónomo, un escáner activo, una plataforma Red Team, un SIEM, un motor de Vulnerability Assessment ni una arquitectura distribuida. El LLM no controla tools ni genera Findings.

## 10. Modelo de trabajo OSINT

CENTAURUS formaliza pasos repetibles de un analista OSINT: delimitar una Investigation, planificar adquisición, preservar RAW, normalizar Evidence, aplicar Rules, producir Findings y consolidar un Report trazable. La IA se mantiene en las fronteras de interpretación/presentación y no sustituye la cadena determinista de conocimiento.

La explicación completa desde la perspectiva del analista se encuentra en `03_USO/OSINT_ANALYST_VIEW.md`.

## 11. Operación de la appliance

El analista inicia la appliance desde el host con `centaurus` **sin argumentos**. El wrapper exige TTY y autenticación fresca y delega exclusivamente en un broker privilegiado mínimo que abre el shell CENTAURUS; el usuario no recibe administración genérica de Docker.

El apagado se realiza fuera del shell mediante `centaurus-poweroff`, también de cero argumentos y con autenticación fresca. Ejecuta únicamente un apagado limpio y no concede `systemctl`, `reboot`, `halt` ni shell root generales.

## Base documental

TFM-OSINT; Modelo Conceptual v3.5; ADR v3.2; Core v2.5; Runtime v2.10; CLI v1.6; Runtime Configuration v1.4; LLM v2.6; Release & Distribution v1.8; G4 USB Cierre Integral v1.1; G4-N7 Validación Física v1.0; Auditoría de Cobertura TFM v3.4.
