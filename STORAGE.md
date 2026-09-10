# Persistencia y trazabilidad

[Español](STORAGE.md) | [English](STORAGE.en.md)
[Inicio](README.md) · [Arquitectura](ARCHITECTURE.md) · [Especificación](SPECIFICATION.md)

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

```text
/workspace/
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

## 10. Workspace en Git + Docker

La modalidad Git + Docker utiliza un directorio persistente del host que se monta en `/workspace`.

La ubicación exacta se documenta en [`INSTALL.md`](INSTALL.md).

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

## 13. Documentación relacionada

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`SPECIFICATION.md`](SPECIFICATION.md)
- [`INSTALL.md`](INSTALL.md)
