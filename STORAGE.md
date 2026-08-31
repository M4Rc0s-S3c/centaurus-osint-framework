# Persistencia y trazabilidad

**Estado:** FINAL · layout reconciliado con referencias de implementación real

## 1. Principio

La persistencia pertenece a infraestructura y es coordinada por Core. Los objetos de dominio no conocen filesystem, JSON, rutas físicas ni naming.

`investigation_id` es el eje lógico de correlación/trazabilidad de los artefactos de una Investigation.

## 2. Persistencia de conocimiento y auditoría

### Artefactos del Knowledge Pipeline

- `RawObservation` — objeto de aplicación persistido como registro original para auditoría/reproducibilidad;
- `Evidence` — hecho normalizado de dominio;
- `Finding` — conclusión determinista de dominio;
- `Report` — snapshot autoritativo de dominio.

### Artefactos operacionales separados

- `ExecutionFailure` — fallo de ejecución persistible fuera del Knowledge Pipeline.

La salida de LLM #2 y el progreso runtime no se persisten como conocimiento.

## 3. Stores

```text
Persistence Layer
├── RawObservationStore
├── EvidenceStore
├── FindingStore
├── ReportStore
└── ExecutionFailureStore      [operacional, separado]
```

Los stores reciben artefactos ya producidos. No normalizan, no aplican Rules y no gobiernan lifecycle.

## 4. Layout físico vigente

La referencia técnica de implementación real de Tools/Plugins y el contrato de Persistence Layer materializan RAW y Evidence bajo la misma rama `evidences/`, manteniéndolos separados:

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

### Reconciliación documental de `raw/`

`STORAGE.md v2.0` mostró posteriormente RAW como `<id>/raw/`. Sin embargo:

- el contrato de Persistence Layer v1.0 define `evidences/raw/`;
- Tools-Plugins v2.4 documenta el `FilesystemRawObservationStore` de implementación real exactamente bajo `evidences/raw/`;
- Tools-Plugins documenta asimismo `ExecutionFailure` bajo `execution/failures/`.

Con la regla **autoridad temática + referencia de implementación real más específica**, la documentación oficial adopta `evidences/raw/` como ruta física vigente. La variante `<id>/raw/` se conserva únicamente como formulación histórica/desactualizada de `STORAGE.md v2.0` y deberá corregirse cuando ese documento fuente vuelva a versionarse.

Esta reconciliación no depende del proceso USB: describe el layout lógico del workspace ya materializado por el framework.

## 5. Convención RAW

El naming documentado es:

```text
<investigation-id>_<sequence>-<source>.json
```

La secuencia pertenece a la Investigation, no a cada source. RAW es acumulativo, no se sobrescribe y conserva el `data` original estructurado.

## 6. Evidence y Finding

`EvidenceStore` persiste Evidence normalizada en `evidences/normalized/`.

`FindingStore` persiste Findings independientemente del Report; un Finding no existe solo como contenido embebido de reporting.

## 7. Report

`ReportStore` persiste el mismo snapshot en:

- `report.json` — representación autoritativa;
- `report.md` — proyección determinista del mismo Report.

Report conserva contexto/provenance y Findings, pero no `ExecutionFailure` ni estado operacional.

## 8. ExecutionFailure

`ExecutionFailureStore` conserva fallos operacionales bajo la rama `execution/failures/`.

- no es RawObservation;
- no es Evidence;
- no es Finding;
- no entra en RuleEngine;
- no se incorpora al Report salvo que un futuro contrato aprobado redefina expresamente esa frontera.

## 9. Inmutabilidad, acumulación y ausencia de rollback global

- RAW no se sobrescribe;
- Evidence histórica no se reemplaza destructivamente;
- Findings son acumulativos;
- Report es snapshot inmutable;
- fallos operacionales conservan su evidencia de ejecución;
- no se corrige el pasado modificando JSON históricos.

CENTAURUS **no implementa una transacción global con rollback sobre todos los stores de una Investigation**. La persistencia representa una secuencia auditable de hechos y conocimiento producido, no una única escritura atómica del caso completo.

Si una fase posterior falla:

```text
artefactos previos persistidos   → se conservan
fase actual                      → falla
Core                             → Investigation = FAILED
artefactos downstream no creados → permanecen ausentes
```

Esta decisión preserva la trazabilidad forense. Un RAW o una Evidence que fueron realmente obtenidos antes de un fallo siguen siendo pruebas válidas de esa ejecución y no deben desaparecer por una compensación transaccional.

La consecuencia es importante: **persistido no significa “investigación completada”**. Una Investigation `FAILED` puede contener artefactos válidos previos; únicamente un Report correctamente construido y persistido representa el snapshot final autoritativo de una Investigation que alcanzó esa fase.

## 10. Trazabilidad

```text
investigation_id
  ├─ evidences/raw/             → RawObservation
  ├─ evidences/normalized/      → Evidence
  ├─ findings/                  → Finding → Rule + Evidence(s)
  ├─ reports/                   → Report → Finding(s)
  └─ execution/failures/        → ExecutionFailure [operacional]
```

La cadena de explicación del conocimiento es:

```text
Report → Finding → Rule + Evidence → source/collected_at + RAW original correlacionable
```

La correspondencia RAW→Evidence se mantiene por la secuencia de ejecución, source/timestamp y mapping normalizador documentado; no se inventa un identificador de dominio adicional si el contrato no lo define.

## 11. Tecnología y acceso

La implementación de referencia es **Filesystem + JSON** bajo `/workspace`. El acceso humano directo al filesystem forma parte del alcance; no se exige query layer/API histórica para el TFM.

## Base documental

Persistence Layer Infrastructure Contract v1.0; Tools-Plugins v2.4; Runtime v2.10; Modelo Conceptual v3.5; Reporting v1.5; `STORAGE.md v2.0` como fuente histórica parcialmente superada en la ruta RAW.
