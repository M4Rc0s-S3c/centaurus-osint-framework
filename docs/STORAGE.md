# Persistencia y trazabilidad

[Español](STORAGE.md) | [English](STORAGE.en.md)
[Inicio](../README.md) · [Arquitectura](ARCHITECTURE.md) · [Especificación](SPECIFICATION.md)

## 1. Principio

La persistencia pertenece a infraestructura y es coordinada por el Core.

Los objetos de dominio no conocen filesystem, JSON o rutas físicas.

`investigation_id` es el eje lógico de correlación de los artefactos de una investigación.

## 2. Artefactos persistidos

### Knowledge Pipeline

- `RawObservation` — observación original;
- `Evidence` — hecho normalizado;
- `Finding` — conclusión determinista;
- `Report` — snapshot autoritativo.

### Rama operacional

- `ExecutionFailure` — fallo de ejecución.

La salida de LLM #2 y el progreso interactivo no se persisten como conocimiento.

## 3. Stores

```text
Persistence Layer
├── RawObservationStore
├── EvidenceStore
├── FindingStore
├── ReportStore
└── ExecutionFailureStore
```

Los stores persisten artefactos ya producidos. No normalizan, no aplican `Rules` y no gobiernan el ciclo de vida de `Investigation`.

## 4. Layout físico

El esquema usa el `<workspace>` configurado. `/workspace` es la ruta de referencia en appliance/contenedor; consulta [`CONFIGURATION.md`](CONFIGURATION.md) para las rutas según modalidad.

```text
<workspace>/
└── investigations/
    └── <investigation-id>/
        ├── evidences/
        │   ├── raw/
        │   └── normalized/
        ├── findings/
        ├── reports/
        └── execution/
            └── failures/
```

### RAW

RAW se materializa en:

```text
evidences/raw/
```

### Evidence

Evidence normalizada se materializa en:

```text
evidences/normalized/
```

### Findings

Los hallazgos se conservan en:

```text
findings/
```

### Reports

Los informes se conservan en:

```text
reports/
```

### Fallos operacionales

Los fallos se conservan en:

```text
execution/failures/
```

## 5. Convención RAW

El naming de referencia es:

```text
<investigation-id>_<sequence>-<source>.json
```

La secuencia pertenece a la investigación.

RAW es acumulativo y no se sobrescribe.

## 6. Report

`ReportStore` materializa el informe en:

```text
report.json
report.md
```

- `report.json` es la representación autoritativa.
- `report.md` es una proyección determinista del mismo informe.

`Report` no incorpora `ExecutionFailure` como conocimiento.

El JSON autoritativo incluye el contenido siguiente:

| Contenido | Campos persistidos |
| --- | --- |
| Contexto del caso | `investigation_id`, `generated_at`, `target`, `target_type`, `intent` |
| Petición original | `analyst_question` opcional; registrada por el recorrido normal de la CLI |
| Hallazgos | `finding_ref`, conclusión, snapshot completo de la regla y evidencias de apoyo |
| Evidencias de apoyo dentro de cada hallazgo | `source`, `collected_at` y `data` |

La petición original también aparece en el informe Markdown cuando está presente. El snapshot JSON de la regla incluye identidad, versión, campos descriptivos, condiciones y conclusión. Las evidencias que sustentan un hallazgo se incorporan al informe además de persistirse por separado; las evidencias sin hallazgo y el RAW original no quedan por ello incluidos en el informe. Los fallos operacionales permanecen separados.

El directorio completo del caso es, por tanto, la referencia para conservar todos los artefactos persistidos. Compartir solo los informes también comparte contexto, la petición original cuando está registrada y evidencias de apoyo. Revisa esos contenidos antes de entregarlos. La proyección más limitada que recibe LLM #2, descrita en [`LLM_ARCHITECTURE.md`](LLM_ARCHITECTURE.md), no elimina datos de los ficheros persistidos.

## 7. ExecutionFailure

`ExecutionFailure`:

- no es `RawObservation`;
- no es `Evidence`;
- no es `Finding`;
- no entra en `RuleEngine`;
- no modifica el significado de un Report ya construido.

## 8. Inmutabilidad y acumulación

- RAW no se sobrescribe.
- Evidence histórica no se reemplaza destructivamente.
- Findings son acumulativos.
- Report es un snapshot.
- Los fallos operacionales conservan su evidencia.

CENTAURUS no aplica una transacción global con rollback sobre todos los stores de una investigación.

Si una fase posterior falla, los artefactos previos válidamente persistidos se conservan.

```text
artefactos previos persistidos   → se conservan
fase actual                      → falla
artefactos downstream no creados → permanecen ausentes
```

Persistido no equivale necesariamente a investigación completada.

## 9. Trazabilidad

```text
investigation_id
  ├─ evidences/raw/             → RawObservation
  ├─ evidences/normalized/      → Evidence
  ├─ findings/                  → Finding → Rule + Evidence(s)
  ├─ reports/                   → Report → Finding(s)
  └─ execution/failures/        → ExecutionFailure
```

Cadena conceptual de explicación:

```text
Report
  ↓
Finding
  ↓
Rule + Evidence
  ↓
source / collected_at
  ↓
RAW original correlacionable
```

### Trazabilidad directa: de la observación al informe

El plugin produce `RawObservation`; su salida estructurada se persiste antes de normalizar. `EvidenceManager` crea `Evidence` normalizada conservando `source` y `collected_at`. Las reglas evalúan esa evidencia y cada `Finding` generado conserva su regla y las evidencias de apoyo. `Report` consolida los hallazgos dentro de la investigación. No toda observación desemboca en un hallazgo.

### Trazabilidad inversa: revisar una conclusión

1. Localiza el caso por `investigation_id` y abre `reports/report.json`.
2. Selecciona el hallazgo por su `finding_ref`, local al informe. Revisa su conclusión, el snapshot de la regla, su versión y condiciones, y las evidencias de apoyo incorporadas.
3. Contrasta esas evidencias con `evidences/normalized/`, utilizando `source`, `collected_at` y `data` dentro del mismo caso.
4. Correlaciónalas con las observaciones de `evidences/raw/` mediante fuente, tiempo de recogida y contenido transformado por el normalizador correspondiente. El contenido RAW y el normalizado no tienen por qué ser idénticos.
5. Revisa por separado `execution/failures/` para valorar la cobertura que faltó. El informe no incorpora esos fallos operacionales.

`Evidence` no contiene un identificador directo de RAW ni su ruta de fichero. Los stores RAW y normalizado asignan secuencias independientes; la coincidencia de números en sus nombres no establece una relación fiable. Tampoco se garantiza que fuente y tiempo sean únicos: si los artefactos conservados no permiten una correspondencia inequívoca, registra ese límite en lugar de dar por supuesto el enlace.

Este es un recorrido de inspección de artefactos persistidos, no un comando integrado de navegación inversa ni una cadena de custodia criptográfica. Conserva el directorio completo del caso y la versión de código/reglas utilizada cuando una auditoría deba explicar tanto las conclusiones como su obtención.

## 10. Workspace en Git + Docker

La modalidad Git + Docker utiliza un directorio persistente del host que se monta en `/workspace`.

La ubicación exacta se documenta en [`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md).

Los datos de investigación no forman parte de la imagen Docker ni del repositorio Git.

## 11. Datos excluidos del repositorio

No deben versionarse:

- investigaciones;
- evidencias generadas;
- informes reales;
- logs de ejecución;
- modelos Ollama;
- secretos;
- credenciales locales;
- ficheros `.env` de despliegue.

## 12. Tecnología

La implementación utiliza **Filesystem + JSON**.

El acceso directo a los artefactos persistidos forma parte del modelo de operación; no es obligatorio disponer de una API histórica separada.

## 13. Extracción, respaldo y recuperación

Son procedimientos administrativos. El analista de la appliance no necesita acceso genérico a Docker ni permisos adicionales sobre el sistema de archivos. La CLI no dispone de comandos de exportación o restauración; el administrador trabaja con los ficheros persistidos y un destino de transferencia autorizado.

### Extraer una investigación

1. Anota el identificador de investigación y espera a que termine su ejecución. Solicita al administrador que localice `<workspace>/investigations/<investigation-id>/` en el workspace del despliegue.
2. Copia el directorio completo del caso a un destino separado para conservar conjuntamente evidencias, hallazgos, informes y fallos operacionales. Para entregar solo el informe, copia `reports/report.json` y `reports/report.md`, explicando que el informe incluye evidencias de apoyo, pero no sustituye al directorio completo del caso ni incluye los fallos operacionales.
3. Compara los ficheros copiados con el origen mediante SHA-256, conserva el identificador del caso y la identidad del despliegue y revisa el contenido antes de compartirlo. La asistencia LLM no está incluida en los informes persistidos.

### Respaldar el workspace

1. Finaliza las investigaciones activas, cierra las sesiones del Core e impide nuevas sesiones durante la copia. Verifica el montaje real del workspace; en OVA/USB el administrador puede utilizar `findmnt /workspace`.
2. Copia el workspace completo, incluidos `investigations/` y los logs necesarios, a almacenamiento independiente. Conserva estructura, propietarios numéricos y permisos con una herramienta de respaldo adecuada. Mantén la copia fuera del workspace activo y fuera del mismo medio USB.
3. Registra el hash de la appliance o el commit de fuentes, la ruta de origen, el momento de la copia y los hashes de los ficheros. Comprueba lectura y espacio disponible en el destino. Un respaldo del workspace conserva resultados; no respalda el sistema operativo, las imágenes Docker ni el modelo Ollama.
4. Para un punto de recuperación completo de OVA, apaga limpiamente la VM y copia su directorio completo con los tres discos virtuales mediante el procedimiento de respaldo del host. Un snapshot en el mismo almacenamiento no es una copia independiente. Para USB, conserva la imagen original de distribución verificada por separado del respaldo del workspace.

### Recuperar y comprobar

1. Conserva el workspace actual antes de realizar cambios. Prepara una instancia compatible separada a partir de la distribución identificada; mantenla inactiva durante la recuperación.
2. Restaura el respaldo del workspace en el volumen de datos de esa instancia, preservando propietarios numéricos y permisos. No superpongas casos con el mismo identificador ni sustituyas contenido de SYSTEM/PLATFORM por datos del workspace.
3. Antes del uso normal, verifica el montaje, compara los hashes de los ficheros restaurados con el respaldo y abre una selección de `report.json` y `report.md`. El administrador debe confirmar también que el usuario habitual del runtime puede acceder a los datos restaurados.
4. Conserva el original y el respaldo hasta aceptar la recuperación. La presencia de ficheros no demuestra que todas las investigaciones terminaran; revisa los informes y fallos operacionales de cada caso. Este procedimiento no proporciona una migración entre formatos de persistencia incompatibles.

Este procedimiento es una pauta operativa; no declara una nueva prueba de recuperación OVA/USB. Valida la herramienta de respaldo y el método de transferencia elegidos en tu entorno antes de depender de ellos.

## 14. Documentación relacionada

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`SPECIFICATION.md`](SPECIFICATION.md)
- [`INSTALL.md`](INSTALL.md)
