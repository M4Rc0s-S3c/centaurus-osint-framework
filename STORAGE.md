# STORAGE.md

# Arquitectura de almacenamiento del Framework OSINT

> **Estado:** Diseño revisado, actualizado y materializado
> **Versión:** Storage v2.0
> **Fecha de revisión:** 15/08/2026
> **Base anterior:** Storage v1.1 — 11/08/2026

## Objetivo

Definir la organización física y lógica del almacenamiento del framework, separando el sistema operativo,
la plataforma de ejecución y los datos generados durante las investigaciones.

La unidad lógica de trazabilidad de los artefactos persistidos es la **Investigation**, identificada por
su `investigation_id`.

Esta versión refleja el cierre de la Persistence Layer para los artefactos actualmente definidos:
`RawObservation`, `Evidence`, `Finding` y `Report`.

La persistencia de la salida/narrativa generada por el LLM queda deliberadamente fuera de este cierre y será
analizada durante la inspección técnica del bloque LLM.

## Principios de diseño

- Separación entre sistema operativo, plataforma y datos.
- `/workspace` constituye la zona persistente de datos del framework.
- La persistencia pertenece a la infraestructura y no al dominio.
- Core coordina el uso de la persistencia dentro del flujo de ejecución.
- Los componentes especializados no gobiernan directamente la infraestructura de almacenamiento.
- Todo artefacto persistible queda asociado inequívocamente a una Investigation.
- `investigation_id` es el eje de trazabilidad.
- La persistencia debe permitir trazabilidad, reproducibilidad y acceso posterior.
- RAW y las representaciones normalizadas se conservan como artefactos diferenciados.
- La implementación física de referencia es **Filesystem + JSON**.
- Los objetos de dominio no conocen rutas físicas, JSON, Filesystem ni mecanismos concretos de persistencia.
- Los artefactos históricos de conocimiento no se modifican ni se eliminan.

## Unidad de trazabilidad: Investigation

Cada `Investigation` posee un identificador único generado al crearse.

```text
Investigation
    │
    └── investigation_id
            │
            ├── RawObservation / RAW
            ├── Evidence
            ├── Finding
            └── Report
```

No se genera un identificador paralelo para sustituir al `investigation_id` como referencia principal.

## Persistence Layer

La Persistence Layer / Storage Layer está situada en infraestructura.

Su responsabilidad es proporcionar la frontera de almacenamiento de los artefactos persistibles de una investigación,
encapsulando Filesystem y serialización.

```text
Core
 │
 │ investigation_id + artefacto
 ▼
Persistence Layer
 │
 ▼
Filesystem + JSON
```

La Persistence Layer no ejecuta plugins, planifica ejecuciones, transforma RAW en Evidence, evalúa Rules,
genera Findings, genera Reports, contiene lógica de negocio ni modifica los objetos del dominio.

## Estructura física

```text
/workspace/
└── investigations/
    └── <investigation-id>/
        ├── raw/
        ├── evidences/
        │   └── normalized/
        ├── findings/
        └── reports/
```

Los nombres físicos concretos pueden contener información adicional necesaria para mantener unicidad y trazabilidad,
pero no sustituyen `investigation_id` como referencia lógica.

## Persistencia de RawObservation

RAW conserva la representación original producida por el plugin.

- no se normaliza antes de persistir;
- no se sobrescribe;
- es acumulativo;
- incorpora `investigation_id` como eje de trazabilidad;
- mantiene la información necesaria de secuencia y origen;
- la escritura debe ser segura/atómica.

## Persistencia de Evidence

`Evidence` es producida por `EvidenceManager` después de la normalización.

La persistencia pertenece a la Persistence Layer y es coordinada por Core.

```text
/workspace/investigations/<investigation-id>/evidences/normalized/
```

Evidence permanece desacoplada de las rutas físicas y del mecanismo de almacenamiento.

## Persistencia de Finding

`Finding` representa conocimiento derivado producido por el `RuleEngine`.

### Decisión cerrada — FindingStore independiente

A 15/08/2026 se cierra la decisión física que permanecía abierta en versiones anteriores:

> **Finding se persiste mediante un `FindingStore` independiente.**

La decisión es compatible con:

- `Finding` como Value Object inmutable;
- ownership de `Investigation`;
- trazabilidad `Rule → Finding → Evidence`;
- separación dominio–infraestructura;
- autoridad de Core;
- persistencia acumulativa del conocimiento.

La Persistence Layer no crea Findings. Core coordina la persistencia del Finding ya producido por el RuleEngine.

La implementación utiliza Filesystem + JSON.

```text
/workspace/investigations/<investigation-id>/findings/
```

Los Findings son acumulativos. No se definen operaciones `update`, `delete` ni `replace` para modificar conocimiento histórico.

Cada Finding persistido conserva la información necesaria para reconstruir su trazabilidad hacia la Rule y las Evidence que lo sustentan.

## Persistencia de Report

`Report` forma parte de los artefactos persistibles de una Investigation.

```text
Findings
   ↓
ReportManager
   ↓
Report
   ↓
Core
   ↓
ReportStore
```

La persistencia física se realiza en:

```text
/workspace/investigations/<investigation-id>/reports/
```

Report mantiene la trazabilidad hacia los Findings que sustentan el conocimiento comunicado.

`ReportManager` no persiste directamente el Report.

## Relación Report / LLM

El modelo conceptual mantiene:

```text
Finding[]
   ↓
ReportManager
   ↓
Report
   ↓
LLM
   ↓
presentación lingüística
```

El LLM no crea ni modifica el objeto `Report` del dominio.

### Estado de persistencia de la salida LLM

La persistencia de la narrativa o salida lingüística del LLM **no está cerrada en Storage v2.0**.

Antes de implementarla deberán analizarse:

- necesidad funcional;
- naturaleza del artefacto;
- relación con Report;
- requisitos de reproducibilidad;
- trazabilidad;
- formato;
- ciclo de vida;
- estrategia física.

No se introduce anticipadamente un `LLMStore` ni una nueva entidad de dominio.

## Serialización

La implementación de referencia utiliza:

```text
Filesystem + JSON
```

`orjson` puede utilizarse como mecanismo interno de serialización cuando corresponda.

```text
Domain/Application object
        ↓
Persistence Layer
        ↓
JSON
        ↓
Filesystem
```

## Escritura y consistencia

La persistencia filesystem deberá evitar ficheros parcialmente escritos mediante mecanismos de escritura segura/atómica.

Los artefactos históricos de conocimiento no se sobrescriben.

## Acceso del analista

El acceso humano a los artefactos persistidos se realiza directamente sobre el filesystem del workspace.

No forma parte del alcance actual del TFM implementar una API de consulta, query layer o interfaz específica de acceso.

```text
Investigation
    │
    ├── RAW
    ├── Evidence
    ├── Finding
    └── Report
```

## Puntos de montaje

| Punto de montaje | Contenido |
|---|---|
| `/` | Sistema Debian mínimo, GRUB y configuración básica |
| `/opt/osint-framework` | Plataforma, framework, plugins, rules, modelos, configuración y Docker |
| `/workspace` | Investigaciones y artefactos persistidos |

## Relación con Docker

- La plataforma se ejecutará mediante Docker.
- `/workspace` se montará como volumen persistente.
- La actualización de la plataforma no afectará al contenido del workspace.
- Los artefactos de las investigaciones permanecerán disponibles aunque se actualice o sustituya la plataforma.

## Independencia de rutas

El Core no contiene rutas físicas codificadas.

Las ubicaciones concretas del workspace y de la Persistence Layer se obtienen mediante configuración.

Core coordina las operaciones de persistencia, pero no conoce detalles de rutas, nombres físicos, serialización
ni implementación concreta de los stores.

## Portabilidad y mantenimiento

La separación entre sistema, plataforma y workspace permite:

- actualización independiente del sistema y la plataforma;
- conservación de los datos generados;
- copias de seguridad del workspace;
- acceso a resultados desde otros equipos;
- ejecución mediante Docker;
- sustitución futura del mecanismo físico de almacenamiento sin modificar el dominio.

## Stores actualmente definidos

```text
Persistence Layer
├── RawObservationStore
├── EvidenceStore
├── FindingStore
└── ReportStore
```

Todos los stores respetan la misma frontera arquitectónica: reciben el contexto de `investigation_id`,
persisten artefactos ya producidos, no generan conocimiento, no aplican Rules, no modifican el dominio
y encapsulan Filesystem y serialización.

## Estado de esta revisión

Esta revisión sustituye Storage v1.1 de fecha 11/08/2026.

Cambios principales:

- se mantiene `/workspace` como zona persistente;
- se mantiene `Investigation` como unidad lógica de trazabilidad;
- se mantiene Core como coordinador;
- se mantiene Filesystem + JSON como implementación de referencia;
- se confirma la persistencia física de RAW;
- se incorpora y cierra la persistencia de Evidence;
- se incorpora y cierra la persistencia de Report;
- se incorpora y cierra la persistencia de Finding mediante **FindingStore independiente**;
- se elimina la condición de "Finding persistence pendiente";
- se actualiza la estructura física para representar RAW, Evidence, Finding y Report;
- se mantienen los objetos de dominio desacoplados de la infraestructura;
- se deja expresamente pendiente el análisis de si la salida del LLM debe persistirse.

**Fecha de revisión:** 15/08/2026
**Versión:** Storage v2.0
**Estado:** Diseño actualizado y alineado con la Persistence Layer implementada y validada.
