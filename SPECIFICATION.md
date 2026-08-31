# Especificación funcional

**Estado:** FINAL · alcance funcional y distribución técnica aceptados

## 1. Propósito

Definir qué debe hacer CENTAURUS según el estado funcional consolidado, sustituyendo las formulaciones tempranas en las que el LLM generaba un `TaskPlan` o RuleEngine asignaba severidades/recomendaciones.

## 2. Requisitos funcionales

### FR-01 — Entrada en lenguaje natural

El analista puede iniciar una investigación desde la CLI mediante lenguaje natural.

### FR-02 — Interpretación estructurada

La entrada se transforma en `StructuredRequest` antes de llegar al Core. Target se detecta/normaliza de forma determinista y **LLM #1** se limita a clasificar un Intent permitido.

### FR-03 — Creación y gobierno de Investigation

Core crea una nueva `Investigation` y es la única autoridad sobre su lifecycle y la integración de conocimiento.

### FR-04 — Planificación determinista

Planner construye `ExecutionPlan` y `ExecutionTask` según Target/capacidades. El LLM no selecciona tools.

### FR-05 — Ejecución modular

Executor y PluginManager ejecutan plugins bajo contrato `BasePlugin` sin acoplar Core a tools concretas.

### FR-06 — Preservación RAW

Cada ejecución válida produce `RawObservation` y se conserva su representación original estructurada para auditoría/reproducibilidad.

### FR-07 — Normalización y Evidence

La salida RAW se transforma mediante normalizador específico y EvidenceManager en Evidence normalizada, sin introducir interpretación.

### FR-08 — Análisis determinista

RuleEngine evalúa Rules explícitas y produce Findings trazables hacia Rule y Evidence soporte.

### FR-09 — Reporting

ReportManager construye un Report persistente a partir de Findings proporcionados por Core. `report.json` es autoritativo y `report.md` es una proyección determinista.

### FR-10 — Asistencia LLM posterior

**LLM #2** puede producir síntesis, implicaciones potenciales y recomendaciones advisory grounded a partir de una proyección controlada del Report. Su salida es efímera y no autoritativa. El perfil productivo es `timeout=300`, `num_ctx=8192`, `num_predict=UNSET`, `think=false`, `keep_alive=0`, sin reintentos automáticos.

### FR-11 — Política de fallo multi-tool

Una tool puede fallar sin invalidar todo el trabajo cuando existe conocimiento válido. Los fallos operacionales se conservan fuera del Knowledge Pipeline y una ejecución parcial puede terminar con Report utilizable.

### FR-12 — Descubrimiento offline

La CLI ofrece `capabilities` y `capabilities --rules` sin requerir Ollama ni crear Investigation.

### FR-13 — Progreso interactivo

En TTY se ofrece progreso efímero de ejecución. En non-TTY esa superficie se silencia sin cambiar el contrato funcional.

### FR-14 — Persistencia trazable

RawObservation, Evidence, Finding y Report se asocian a `investigation_id` y se conservan en `/workspace` mediante la Persistence Layer.

### FR-15 — Punto de entrada operacional de la appliance

En la appliance C4, el usuario `centaurus` inicia el runtime mediante el comando host `centaurus` sin argumentos. El wrapper requiere TTY y autenticación y no concede administración Docker/Compose general.

### FR-16 — Apagado controlado

Después de salir del shell, el usuario `centaurus` puede ejecutar `centaurus-poweroff`, comando host autenticado y de cero argumentos que realiza únicamente un apagado limpio.

### FR-17 — Distribución reproducible

La versión de entrega dispone de OVA final aceptada, modalidad Git + Docker Linux y una imagen raw USB de identidad congelada. Las modalidades comparten el mismo producto y no redefinen el dominio.

### FR-18 — Portabilidad de red de la appliance física

La política de naming debe materializar el uplink físico como `centaurus0` sin depender de la vNIC E1000 de VMware. La aceptación bare-metal cerrada demuestra este contrato en una Intel I218-V/e1000e con enlace, DHCP y ruta por defecto.

## 3. Cobertura operacional

| Target | Cobertura documentada |
|---|---|
| DOMAIN | completa · siete tareas sobre seis tools |
| IP | limitada · RDAP |
| EMAIL | no operacional |
| CERTIFICATE | diferido |

## 4. Requisitos no funcionales

- ejecución local del framework y LLM;
- arquitectura modular/extensible;
- bajo acoplamiento;
- reproducibilidad;
- trazabilidad y auditabilidad;
- persistencia desacoplada del dominio;
- seguridad por diseño y mínimo privilegio;
- funcionamiento sin APIs comerciales obligatorias;
- capacidad de degradación parcial ante fallos upstream;
- degradación fail-soft de LLM #2 cuando el proveedor falla después de existir Report;
- tests como especificación ejecutable de contratos;
- validación de la distribución mediante OVA y medio físico real;
- no extrapolar una plataforma física validada a compatibilidad universal.

## 5. Exclusiones

- escaneo activo y pentesting;
- agentes autónomos/tool calling LLM;
- RAG/embeddings/memoria persistente de IA;
- GUI/Web/API como requisito del TFM;
- multiusuario/alta disponibilidad/distribución horizontal;
- scoring/severidad/confidence estructurados en Rule/Finding;
- query layer histórica desde CLI;
- CERTIFICATE operativo hasta decisión/implementación específica posterior;
- garantía universal de rendimiento LLM en cualquier CPU;
- garantía universal de compatibilidad con cualquier firmware, controlador USB o NIC.

## 6. Criterio de aceptación funcional y de distribución

El recorrido funcional está aceptado cuando la solicitud estructurada produce y preserva conocimiento trazable hasta Report con suite verde y validación runtime. La distribución técnica queda aceptada en el alcance demostrado por:

- OVA C4-RS2/Broker-D2 `FINAL_ACCEPTED`;
- G4 R0–R6 `CLOSED/PASS`;
- imagen `CENTAURUS-USB.img` congelada y materializada físicamente;
- arranque, runtime e investigación real desde USB;
- reinicio/persistencia;
- N7 bare-metal `CLOSED/PASS` para la plataforma observada.

En la prueba física final, el flujo natural llegó a un Intent válido e inició la Investigation, lo que corrobora la función de interpretación de LLM #1. LLM #2 agotó su timeout de 300 s; esa degradación fue no bloqueante y no invalidó el Report.

## Base documental

TFM-OSINT; Modelo Conceptual v3.5; Core v2.5; Runtime v2.10; Tools-Plugins v2.4; Rules/RuleEngine; Reporting v1.5; Runtime Configuration v1.4; CLI v1.6; Contrato LLM v2.6; C4-RS2/Broker-D2; G4 USB Cierre Integral v1.1; G4-N7 v1.0; Release & Distribution v1.8; Auditoría de Cobertura TFM v3.4.
