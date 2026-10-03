# Core y ciclo de ejecución

[Español](CORE_RUNTIME.md) | [English](CORE_RUNTIME.en.md)

[Inicio](../README.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`DEVELOPMENT.md`](DEVELOPMENT.md)

## 1. Autoridad y entrada

El Core coordina los componentes, gobierna el ciclo de `Investigation` e integra el conocimiento. Delega el trabajo especializado mediante contratos explícitos; no interpreta lenguaje natural ni incorpora lógica específica de cada herramienta.

La CLI utiliza `RequestInterpreter` para obtener una `StructuredRequest` validada. `Core.submit_request()` crea una investigación nueva con Target e Intent y ejecuta su ciclo. La petición original puede acompañarse como `analyst_question`: es contexto del informe, no una instrucción para Planner o RuleEngine.

Cada ejecución crea una identidad independiente. Repetir un objetivo no reanuda ni sobrescribe una investigación anterior.

## 2. Estados de dominio y resultado operacional

| Estado de `InvestigationStatus` | Significado |
| --- | --- |
| `CREATED` | Investigación creada. |
| `PLANNED` | Entrada en planificación; se solicita y valida el plan. |
| `RUNNING` | Plan validado y ejecución iniciada. |
| `COMPLETED` | Ciclo completado; puede haber cobertura reducida. |
| `FAILED` | El ciclo no pudo completarse. |

`partial` no pertenece a ese enum. Es un resultado operacional de `Executor`, junto con `completed` y `failed`:

| Resultado de Executor | Condición de agregación | Recorrido del Core |
| --- | --- | --- |
| `completed` | No hay fallos de tareas. | Continúa el pipeline; termina `COMPLETED` si las fases posteriores finalizan. |
| `partial` | Hay observaciones válidas y fallos de tareas. | Conserva los fallos por separado y procesa las observaciones; puede terminar `COMPLETED`. |
| `failed` | Hay fallos y ninguna observación válida. | Persiste fallos, marca `FAILED` y no construye un informe de resultados. |

Tener observaciones válidas no garantiza que normalización, reglas o persistencia posteriores vayan a completarse. El caso de cero hallazgos tampoco es por sí mismo un fallo. La presentación y los códigos de salida de la CLI se explican en [`USER_GUIDE.md`](USER_GUIDE.md).

## 3. Planificación y ejecución

`Planner` consulta el catálogo de capacidades para el tipo de objetivo y construye las tareas. El Intent ya ha sido validado en la frontera de entrada; el catálogo actual admite un único propósito funcional. No existe selección libre de herramientas por el LLM.

`ExecutionPlan` contiene `investigation_id`, `tasks` y `metadata`. Es efímero; no contiene un campo `objective` ni copias de Target e Intent. Antes de ejecutar, el Core comprueba el tipo de plan, la coincidencia de investigación y que sus tareas sean `ExecutionTask`.

`Executor` procesa las tareas secuencialmente y delega en `PluginManager`. Los fallos recuperables de plugins se registran y permiten continuar con las tareas siguientes. No hay replanificación autónoma. El contrato de adquisición está en [`PLUGIN_SYSTEM.md`](PLUGIN_SYSTEM.md).

## 4. Orden del pipeline

| Orden | Operación coordinada por el Core |
| --- | --- |
| 1 | Recoger el resultado del Executor y persistir `ExecutionFailure` si existe. |
| 2 | Si la ejecución no es `failed`, persistir las observaciones RAW válidas. |
| 3 | Crear evidencias mediante `EvidenceManager`, integrarlas y persistirlas. |
| 4 | Evaluar reglas, integrar los hallazgos y persistirlos. |
| 5 | Construir el informe mediante `ReportManager` e integrarlo en la investigación. |
| 6 | Persistir `report.json` y `report.md` mediante `ReportStore`. |
| 7 | Solicitar asistencia a `LLMManager` después de la persistencia. |
| 8 | Finalizar el ciclo como `COMPLETED`, también cuando la asistencia tenga un error LLM gestionado. |

El Core conserva la coordinación de esas colaboraciones. La normalización específica pertenece a la frontera de evidencias; `RuleEngine` trabaja sobre datos normalizados y `ReportManager` consolida hallazgos. Los fallos de ejecución no pasan por esa cadena de conocimiento.

## 5. Matriz de respuesta a fallos

| Frontera | Resultado esperado |
| --- | --- |
| Configuración o petición rechazada antes del Core | No se inicia una investigación por ese recorrido. |
| Planner o plan inválido tras iniciar el ciclo | `FAILED`, propagación del error y ausencia de ejecución del plan inválido. |
| Una tarea falla | `ExecutionFailure`; las demás tareas pueden continuar. |
| Todas las tareas de un plan no vacío fallan | `FAILED`, fallos persistidos y ningún informe fabricado. |
| Normalización, reglas, construcción o persistencia del informe fallan | `FAILED`; se propaga la excepción. No se fabrica el conocimiento posterior ausente. |
| El proveedor LLM #2 produce un error LLM gestionado | Advertencia y ausencia de asistencia; el informe persistido se conserva. |
| Falla la superficie de progreso gestionada por el Core | Se degrada la presentación; no adquiere autoridad sobre el conocimiento. |

El tratamiento auxiliar de LLM #2 captura excepciones del contrato `LLMError`. No implica recuperación universal de excepciones inesperadas, terminación del proceso o falta de memoria. Las reglas de rechazo de contenido se describen en [`LLM_ARCHITECTURE.md`](LLM_ARCHITECTURE.md).

## 6. Persistencia y límites de recuperación

No hay una transacción global con rollback de toda la investigación. Un fallo posterior puede dejar RAW, evidencias o hallazgos válidos ya persistidos. Esos artefactos conservan valor de diagnóstico y trazabilidad, pero no demuestran que exista un informe final.

Tampoco debe confundirse el `Report` integrado en memoria con su persistencia terminada: la integración precede a la escritura. Los stores aplican sus propias garantías locales; por ejemplo, `ReportStore` intenta retirar los archivos que acaba de crear si falla la escritura del par JSON/Markdown. Eso no revierte los demás stores.

Las rutas, el contenido de los informes y los procedimientos de respaldo están en [`STORAGE.md`](STORAGE.md).

## 7. Progreso y recursos

`RuntimeProgressReporter` es una superficie opcional y efímera. Executor comunica eventos de tareas mediante callback; no necesita conocer Rich ni gobernar `Investigation`. El Core protege la publicación de progreso y puede degradar a un reporter nulo.

Los plugins se instancian por tarea. Los proveedores HTTP cierran los clientes que crean; un cliente inyectado conserva su propietario externo. El perfil y la liberación solicitada del modelo de asistencia se describen en [`LLM_ARCHITECTURE.md`](LLM_ARCHITECTURE.md). No se presupone concurrencia de tareas ni un servicio Core permanente.

## 8. Referencias de implementación

- [`core.py`](../src/centaurus/core/core.py)
- [`investigation.py`](../src/centaurus/investigation/investigation.py)
- [`investigation_status.py`](../src/centaurus/investigation/investigation_status.py)
- [`planner.py`](../src/centaurus/planner/planner.py)
- [`executor.py`](../src/centaurus/executor/executor.py)
- [`report_store.py`](../src/centaurus/persistence/filesystem/report_store.py)
- [`TESTING.md`](TESTING.md)
