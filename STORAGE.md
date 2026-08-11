# STORAGE.md

# Arquitectura de almacenamiento del Framework OSINT

> **Estado:** Diseño revisado y actualizado\
> **Versión:** Storage v1.1\
> **Fecha de revisión:** 11/08/2026\
> **Base anterior:** Diseño congelado (MVP v1.0)

## Objetivo

Definir la organización física y lógica del almacenamiento del
framework, separando el sistema operativo, la plataforma de ejecución y
los datos generados durante las investigaciones.

Esta revisión actualiza el diseño inicial para reflejar las decisiones
arquitectónicas posteriores relativas a trazabilidad por
`Investigation`, Persistence Layer y organización de los artefactos
persistibles.

La unidad lógica de trazabilidad de los artefactos persistidos es la
**Investigation**, identificada por su `investigation_id`.

## Principios de diseño

-   Separación entre sistema operativo, plataforma y datos.
-   `/workspace` constituye la zona persistente de datos del framework.
-   La persistencia pertenece a la infraestructura y no al dominio.
-   El **Core coordina el uso de la persistencia** dentro del flujo de
    ejecución.
-   Los componentes especializados no gobiernan el ciclo de vida de
    `Investigation` ni gestionan directamente la infraestructura de
    almacenamiento.
-   Los artefactos persistibles se asocian inequívocamente a una
    `Investigation`.
-   La persistencia debe permitir trazabilidad y reproducibilidad.
-   RAW y las representaciones normalizadas se conservan como artefactos
    diferenciados.
-   El almacenamiento debe permitir consulta y verificación posterior
    por un analista.
-   La solución inicial utiliza Filesystem + JSON.
-   La plataforma debe seguir siendo portable y compatible con Docker.

## Unidad de trazabilidad: Investigation

Cada `Investigation` posee un identificador único generado al crearse.

El `investigation_id` constituye la referencia de asociación de los
artefactos persistidos durante esa investigación.

``` text
Investigation
    │
    └── investigation_id
            │
            ├── RawObservation / RAW
            ├── Evidence
            ├── Finding*
            └── Report
```

\* La estrategia física definitiva de persistencia de `Finding` queda
pendiente de la decisión correspondiente del modelo conceptual y no se
congela en este documento.

No se genera un identificador paralelo para sustituir al
`investigation_id` como referencia principal de una investigación.

## Persistence Layer

La persistencia se organiza mediante una **Persistence Layer / Storage
Layer** situada en infraestructura.

Su responsabilidad es proporcionar la frontera de almacenamiento de los
artefactos persistibles de una investigación, desacoplada de los objetos
y responsabilidades del dominio.

La Persistence Layer:

-   almacena y recupera artefactos persistibles;
-   utiliza el `investigation_id` para asociarlos a una investigación;
-   encapsula los detalles de Filesystem y serialización;
-   mantiene separadas las representaciones RAW y normalizadas;
-   puede incorporar stores especializados por tipo de artefacto.

La Persistence Layer **no**:

-   ejecuta plugins o herramientas;
-   crea `Evidence`;
-   evalúa Rules;
-   genera `Finding`;
-   genera `Report`;
-   modifica directamente el ciclo de vida de `Investigation`;
-   contiene lógica de orquestación del runtime.

### Coordinación por Core

El Core permanece como punto de coordinación del runtime.

``` text
Core
 │
 ├── Plugin / Executor
 │       ↓
 │   RawObservation
 │       │
 │       ├──────────────→ Persistence Layer → RAW
 │       │
 │       ↓
 │   Normalización
 │       ↓
 │   EvidenceManager
 │       ↓
 │    Evidence
 │       │
 │       ├──────────────→ Persistence Layer → Evidence
 │       │
 │       ↓
 │   RuleEngine
 │       ↓
 │    Finding
 │
 ├── ReportManager
 │       ↓
 │     Report
 │       │
 │       └──────────────→ Persistence Layer → Report
 │
 └── Investigation
```

Los componentes especializados realizan únicamente su responsabilidad y
devuelven el control al Core.

## Stores especializados

La Persistence Layer puede organizarse mediante stores especializados:

``` text
Persistence Layer
│
├── RawObservationStore
├── EvidenceStore
├── FindingStore      ← estrategia física pendiente
└── ReportStore
```

No todos los stores tienen que implementarse simultáneamente.

La primera implementación corresponde a `RawObservationStore`, seguida
de Evidence y Report conforme se complete su integración funcional.

## Organización física

`/workspace` continúa siendo la zona persistente.

``` text
/workspace/
└── investigations/
    └── <investigation-id>/
        ├── evidences/
        │   ├── raw/
        │   └── normalized/
        ├── findings/
        └── reports/
├── logs/
├── cache/
└── tmp/
```

La carpeta de la investigación constituye la unidad física principal
para acceder a los artefactos relacionados con ella.

`logs/`, `cache/` y `tmp/` permanecen fuera de esta unidad porque
representan información operacional o temporal.

## Persistencia RAW

RAW representa la observación original producida por un plugin antes de
su transformación en conocimiento normalizado.

El RAW debe conservarse íntegramente y sin sustituirlo por la
representación normalizada.

El contrato mínimo previsto es conceptualmente:

``` text
persist_raw(
    investigation_id,
    RawObservation
)
```

El `investigation_id` se proporciona explícitamente como contexto de
persistencia.

`RawObservation` mantiene su contrato de aplicación y no incorpora
conocimiento sobre Filesystem, rutas ni mecanismos de almacenamiento.

### Identificación física de RAW

La convención prevista es:

``` text
<investigation-id>_<sequence>-<source>.json
```

Ejemplo:

``` text
550e8400-e29b-41d4-a716-446655440000_0001-whois.json
550e8400-e29b-41d4-a716-446655440000_0002-rdap.json
```

La identificación física permite reconocer:

-   la `Investigation`;
-   la posición secuencial dentro de ella;
-   la fuente o plugin.

La secuencia no debe provocar sobrescritura de un RAW existente.

## Persistencia de Evidence

La representación normalizada de Evidence se conservará separada del
RAW:

``` text
/workspace/investigations/<investigation-id>/evidence/
├── raw/
└── normalized/
```

La persistencia de Evidence pertenece a la Persistence Layer y será
coordinada por Core una vez producida por `EvidenceManager`.

`EvidenceManager` no conoce rutas físicas ni mecanismos de persistencia.

## Persistencia de Finding

`Finding` pertenece al conocimiento derivado de una investigación y
mantiene trazabilidad hacia las Evidence que lo sustentan.

La estrategia física definitiva de persistencia de `Finding` no se
congela aquí mientras el modelo conceptual mantenga dicha decisión
pendiente.

La Persistence Layer deberá permitir incorporar posteriormente un
`FindingStore` sin modificar los contratos del dominio.

## Persistencia de Report

`Report` forma parte de los artefactos persistibles de una
Investigation.

Su persistencia será realizada por la Persistence Layer después de que
`ReportManager` haya generado el Report y el Core haya recuperado el
control.

``` text
/workspace/investigations/<investigation-id>/reports/
```

Los formatos concretos permanecen gobernados por el contrato de
Reporting.

## Serialización

La implementación inicial utiliza:

``` text
Filesystem + JSON
```

`orjson` puede utilizarse como mecanismo interno de serialización.

El contrato de la Persistence Layer no expone la librería concreta de
serialización.

``` text
Domain/Application object
        ↓
Persistence Layer
        ↓
JSON
        ↓
Filesystem
```

## Escritura y consistencia

La persistencia de artefactos debe evitar ficheros parcialmente
escritos.

La implementación filesystem deberá utilizar un mecanismo de escritura
segura/atómica apropiado.

Los artefactos RAW son acumulativos y no deben sobrescribirse durante
una investigación.

## Puntos de montaje

  ------------------------------------------------------------------------
  Punto de montaje         Partición               Contenido
  ------------------------ ----------------------- -----------------------
  `/`                      Partición 1 --- Sistema Debian mínimo, GRUB y
                                                   configuración básica
                                                   del sistema operativo.

  `/opt/osint-framework`   Partición 2 ---         Docker, Docker Compose,
                           Plataforma              Framework OSINT,
                                                   plugins, Rule Engine,
                                                   Ollama, modelo Qwen3:4B
                                                   Instruct y
                                                   configuración.

  `/workspace`             Partición 3 ---         Investigaciones,
                           Workspace               evidencias, informes,
                                                   logs, caché y archivos
                                                   temporales.
  ------------------------------------------------------------------------

## Organización de la plataforma

``` text
/opt/osint-framework/
├── framework/
├── plugins/
├── rules/
├── models/
├── config/
├── docker/
├── scripts/
├── docs/
└── docker-compose.yml
```

## Relación con Docker

-   La plataforma se ejecutará mediante Docker.
-   `/workspace` se montará como volumen persistente.
-   La actualización de la plataforma no afectará al contenido del
    workspace.
-   Los artefactos de las investigaciones permanecerán disponibles
    aunque se actualice o sustituya la plataforma.

## Independencia de rutas

El Core no contendrá rutas físicas codificadas.

Las ubicaciones concretas del workspace y de la Persistence Layer se
obtendrán mediante configuración.

El Core coordina las operaciones de persistencia, pero no conoce
detalles de rutas, nombres físicos, serialización ni implementación del
almacenamiento.

## Acceso del analista

La organización por `investigation_id` permite localizar posteriormente
los artefactos pertenecientes a una investigación.

El objetivo es permitir el acceso y verificación de:

``` text
Investigation
    │
    ├── RAW
    ├── Evidence
    ├── Finding
    └── Report
```

manteniendo la trazabilidad entre los artefactos cuando los contratos
correspondientes la proporcionen.

## Portabilidad y mantenimiento

La separación entre sistema, plataforma y workspace permite:

-   actualización independiente del sistema operativo y de la
    plataforma;
-   conservación de los datos generados;
-   copias de seguridad del workspace;
-   acceso a resultados desde otros equipos;
-   ejecución mediante Docker;
-   sustitución futura del mecanismo físico de almacenamiento sin
    modificar el dominio.

## Evolución prevista

La Persistence Layer se define como una capacidad de infraestructura
extensible.

La implementación inicial se centra en Filesystem + JSON y en la
persistencia de RAW.

La incorporación posterior de Evidence, Report y, cuando corresponda,
Finding reutilizará esta misma frontera de infraestructura y mantendrá
el `investigation_id` como eje de trazabilidad.

No se congela en esta versión una tecnología distinta de Filesystem +
JSON ni una estrategia física de `Finding` que todavía no haya sido
aprobada por el modelo conceptual.

## Estado de esta revisión

Esta revisión sustituye el diseño de almacenamiento MVP v1.0 de fecha
09/07/2026.

Cambios principales:

-   se mantiene `/workspace` como zona persistente;
-   se introduce formalmente la **Persistence Layer / Storage Layer**;
-   se establece el **Core como coordinador** de las operaciones de
    persistencia dentro del runtime;
-   se establece `Investigation` como unidad lógica de trazabilidad;
-   se introduce `investigation_id` como referencia explícita de los
    artefactos persistidos;
-   se separan físicamente RAW y Evidence normalizada;
-   se prepara la capa para stores especializados;
-   se mantiene abierta la estrategia física de Finding;
-   se establece Filesystem + JSON como implementación inicial;
-   se incorpora la organización física por `investigation_id`;
-   se refuerzan los requisitos de trazabilidad, reproducibilidad y
    acceso posterior por parte del analista.

**Fecha de revisión:** 11/08/2026\
**Versión:** Storage v1.1
