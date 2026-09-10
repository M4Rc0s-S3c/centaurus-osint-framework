# Especificación funcional

[Español](SPECIFICATION.md) | [English](SPECIFICATION.en.md)
[Inicio](README.md) · [Proyecto](PROJECT.md) · [Arquitectura](ARCHITECTURE.md) · [Instalación](INSTALL.md)

## 1. Propósito

Este documento define el comportamiento funcional público de CENTAURUS.

La implementación actual utiliza planificación determinista y mantiene al LLM fuera de la selección/ejecución de herramientas y de la generación autoritativa de hallazgos.

## 2. Requisitos funcionales

### FR-01 — Entrada en lenguaje natural

El analista puede iniciar una investigación mediante la CLI utilizando lenguaje natural.

### FR-02 — Interpretación estructurada

La entrada se transforma en `StructuredRequest`.

- `TargetFactory` detecta y normaliza el `Target` de forma determinista.
- LLM #1 clasifica únicamente un `Intent` permitido.

### FR-03 — Gobierno de Investigation

El Core crea `Investigation` y gobierna su ciclo de vida.

### FR-04 — Planificación determinista

`Planner` construye `ExecutionPlan` y `ExecutionTask` a partir del `Target`, `Intent` y capacidades disponibles.

El LLM no selecciona herramientas.

### FR-05 — Ejecución modular

`Executor` y `PluginManager` ejecutan plugins mediante contratos explícitos.

### FR-06 — Preservación RAW

Cada ejecución válida puede producir `RawObservation`, que se conserva para auditoría y reproducibilidad.

### FR-07 — Normalización y Evidence

La salida RAW se transforma mediante normalización específica en `Evidence`, sin introducir conclusiones analíticas.

### FR-08 — Análisis determinista

`RuleEngine` evalúa `Rules` y produce `Findings` trazables hacia las evidencias que los soportan.

### FR-09 — Reporting

`ReportManager` construye y persiste el informe.

```text
report.json → autoritativo
report.md   → proyección determinista
```

### FR-10 — Asistencia LLM posterior

LLM #2 puede producir ayuda de síntesis y explicación a partir del `Report`.

Su salida:

- es grounded;
- es efímera;
- no es autoritativa;
- no modifica `Evidence`, `Findings` o `Report`;
- falla en modo fail-soft.

Perfil actual:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

### FR-11 — Fallo parcial de herramientas

El fallo de una herramienta no invalida necesariamente toda la investigación cuando existe conocimiento válido suficiente.

Los errores se representan como `ExecutionFailure` y permanecen fuera del Knowledge Pipeline.

### FR-12 — Descubrimiento offline

La CLI ofrece:

```bash
centaurus capabilities
centaurus capabilities --rules
```

sin necesidad de iniciar una investigación.

### FR-13 — Progreso interactivo

En TTY puede mostrarse progreso efímero.

En ejecución no interactiva esa superficie puede silenciarse sin alterar el contrato funcional.

### FR-14 — Persistencia trazable

Los artefactos se correlacionan mediante `investigation_id` y se conservan bajo `/workspace`.

### FR-15 — Punto de entrada de la appliance

El usuario estándar puede iniciar el runtime mediante:

```bash
centaurus
```

### FR-16 — Apagado controlado

El apagado limpio de la appliance se realiza mediante:

```bash
centaurus-poweroff
```

### FR-17 — Distribución reproducible

El producto puede consumirse mediante:

- Git + Docker Linux;
- OVA VMware;
- imagen USB arrancable.

### FR-18 — Portabilidad de red

La appliance utiliza `centaurus0` como nombre lógico del uplink y evita depender de un modelo concreto de vNIC VMware.

## 3. Cobertura operacional

| Target | Cobertura |
|---|---|
| DOMAIN | principal/completa en la versión actual |
| IP | limitada mediante RDAP |
| EMAIL | no operacional como Target directo |
| CERTIFICATE | diferido |

## 4. Herramientas integradas

La versión actual incluye:

- WHOIS;
- RDAP;
- DNSRecon;
- Sublist3r;
- TheHarvester;
- crt.sh.

La incorporación de nuevas herramientas se realiza mediante plugins.

## 5. Requisitos no funcionales

CENTAURUS debe mantener:

- ejecución local del framework y LLM;
- modularidad;
- bajo acoplamiento;
- reproducibilidad;
- trazabilidad;
- persistencia desacoplada del dominio;
- mínimo privilegio;
- funcionamiento sin APIs comerciales obligatorias;
- degradación parcial ante fallos upstream;
- degradación fail-soft de LLM #2;
- pruebas automatizadas de contratos;
- separación entre producto y modalidad de distribución.

## 6. Exclusiones

No forman parte del alcance actual:

- escaneo activo;
- explotación/pentesting automatizado;
- agentes autónomos con tool calling LLM;
- RAG/embeddings como requisito del producto;
- GUI/Web/API obligatoria;
- alta disponibilidad o distribución horizontal;
- garantía universal de rendimiento LLM;
- garantía universal de compatibilidad con cualquier hardware.

## 7. Criterios de aceptación

Una investigación funcional debe preservar la cadena:

```text
RAW
  ↓
Evidence
  ↓
Finding
  ↓
Report
```

con trazabilidad suficiente para explicar el origen del conocimiento.

Una degradación de LLM #2 no invalida un `Report` ya construido y persistido.

## 8. Documentación relacionada

- [`PROJECT.md`](PROJECT.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`STORAGE.md`](STORAGE.md)
- [`INSTALL.md`](INSTALL.md)
