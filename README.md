# CENTAURUS OSINT Framework — Documentación oficial FINAL · REV4

**Versión de paquete:** v1.6  
**Estado documental:** FINAL · reconciliado contra la baseline consolidada final v1.8  
**Fecha de corte documental:** 31-08-2026

Esta emisión constituye el **freeze editorial final de la línea REV4**. Se deriva de `CENTAURUS_DOCUMENTACION_CONSOLIDADA_ES_FINAL_v1.8_31-08-2026_G4_N7_PHYSICAL_CLOSED`, que permanece como **baseline técnica/documental consolidada FINAL e inmutable**. REV4 v1.6 no modifica arquitectura, código, OVA ni imagen USB: corrige estructura y redacción, sincroniza Markdown/DOCX y separa la documentación académica de la trazabilidad interna del proceso.

## 1. Estado final incorporado

Hechos documentales vigentes:

- `C4-RS2/Broker-D2 = FINAL_ACCEPTED`: OVA final `CENTAURUS-C4-FINAL.ova`, **11.828.618.752 bytes**, SHA-256 `d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868`.
- la OVA anterior de SHA-256 `85e62517669b8daf25fb42ba1623ef58725485e307075f16c31fef3a9177690c` permanece como `HISTORICAL_NO_GO / DO_NOT_DISTRIBUTE`.
- `G4 R0–R6 = CLOSED / PASS`: imagen raw, materialización física, validación GPT/payload byte-exacta, arranque desde USB en VMware, Docker/Ollama/Core, investigación real y persistencia tras reinicio.
- imagen raw final: `CENTAURUS-USB.img`, **31.457.280.000 bytes**, SHA-256 `7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165`.
- `G4-N7 = CLOSED / PASS` para la plataforma física observada: Toshiba Portege Z30-A, Intel I218-V/e1000e, `centaurus0`, enlace Ethernet 1 Gb/s Full Duplex, DHCP y ruta por defecto.
- investigación bare-metal: 6 Evidence, 4 Findings y Report persistido. El único fallo de adquisición persistido fue `crt.sh` por error upstream HTTP 404.
- **LLM #1 — interpretación corroborada por el flujo natural observado**: la petición llegó a un Intent válido e inició la Investigation. Esta evidencia de flujo no se presenta como un marcador telemétrico independiente `LLM1=PASS`.
- **LLM #2 = TIMEOUT_NON_BLOCKING** en ese hardware: `role=analyst_assistance`, `ReadTimeout`, 300 s. El Report ya existente permaneció autoritativo y la investigación finalizó correctamente en modo degradado.
- no se atribuye causalidad demostrada del timeout a la CPU antigua; se registra únicamente como factor plausible de recursos/rendimiento y no se formula rendimiento universal.
- `OLLAMA-D2 R2 = CLOSED / PASS`: commit `fe6ae9c9d81362d456f4cb35f5700a535d13b4bc`; perfil LLM #2 `timeout=300`, `num_ctx=8192`, `num_predict=UNSET`, `think=false`, `keep_alive=0`, sin reintentos automáticos.
- suite focal D2: **82 tests PASS**; suite global post-D2: **561 tests PASS**. No existe delta de código posterior que cambie esa baseline.
- `report.json` permanece como representación autoritativa del Report; `report.md` es su proyección determinista; la asistencia LLM #2 es efímera y no autoritativa.

## 2. Alcance técnico cerrado

Quedan cerrados en el alcance documentado del TFM:

- arquitectura, modelo de dominio, Core y Knowledge Pipeline;
- plugins/tools, Rules/RuleEngine y reporting;
- persistencia y trazabilidad;
- seguridad del framework y runtime;
- C4-PRIV-1, C4-PRIV-2, NET-N4 y OLLAMA-D2;
- resellado correctivo C4-RS2/Broker-D2 y promoción de la OVA final;
- G4 USB R0–R6;
- G4-N7 físico para la plataforma observada;
- documentación consolidada fuente v1.8.

## 3. Límites deliberados de las conclusiones

No queda un hito técnico obligatorio del producto pendiente dentro del alcance aceptado. La documentación final mantiene, no obstante, límites explícitos:

- compatibilidad universal con cualquier firmware, CPU, controlador USB o NIC: **NO DEMOSTRADA**;
- rendimiento universal de LLM local sobre hardware arbitrario: **NO DEMOSTRADO**;
- causalidad exacta del timeout de LLM #2 sobre el portátil antiguo: **NO DEMOSTRADA**;
- la publicación o distribución pública de los artefactos queda fuera del alcance de esta documentación académica.

## 4. Orden de lectura recomendado en el repositorio

La raíz del repositorio mantiene los nombres históricos de los documentos principales para no romper referencias existentes. Para comprender la fotografía final se recomienda:

1. `PROJECT.md` — identidad, propósito, alcance y modalidades de distribución.
2. `SPECIFICATION.md` — requisitos funcionales y no funcionales.
3. `STANDARDS.md` — normas y convenciones vigentes.
4. `ARCHITECTURE.md` — arquitectura global del framework.
5. `STORAGE.md` — persistencia, layout y trazabilidad.
6. `INSTALL.md` — despliegue reproducible desde Git + Docker sobre Linux.
7. `DEVELOPMENT.md` — disciplina y guía de desarrollo.

La documentación académica completa, incluidos modelo de dominio, Core Runtime, Knowledge Pipeline, plugins, Rules, seguridad, guía de usuario y notas de despliegue OVA/USB/Windows/GPU, se conserva en `CENTAURUS_DOCUMENTACION_OFICIAL_FINAL_REV4_DOCX_MD_ES_v1.6`.

## 5. Regla de autoridad

La autoridad se determina por **materia + última decisión explícitamente aceptada**. La baseline consolidada v1.8 es la fuente técnica final de esta edición. Las versiones históricas y los artefactos de proceso se preservan en el archivo completo de trazabilidad, pero no forman parte del paquete académico limpio ni prevalecen sobre los cierres posteriores.

## 6. Evolución de la línea REV4

- **v1.1:** cierre C4-PRIV-1/2 y OLLAMA-D2, actualización del entrypoint/apagado y baseline de 561 tests.
- **v1.2:** notas técnicas Windows y GPU/Ollama.
- **v1.3:** nota técnica Git + Docker Linux.
- **v1.4:** cierre C4-RS2/Broker-D2, G4 USB R0–R6 y N7 físico; actualización de la distinción operacional LLM #1 / LLM #2.
- **v1.5:** notas técnicas específicas de despliegue OVA/VMware y USB.
- **v1.6:** freeze editorial final; corrección estructural y lingüística, sincronización MD/DOCX y separación entre entrega académica limpia y trazabilidad interna.

Las notas técnicas complementarias no modifican la autoridad de los contratos del Core ni de la baseline técnica v1.8.
