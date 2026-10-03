# Sistema de plugins

[Español](PLUGIN_SYSTEM.md) | [English](PLUGIN_SYSTEM.en.md)

[Inicio](../README.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`DEVELOPMENT.md`](DEVELOPMENT.md)

## 1. Alcance y responsabilidades

Los plugins adaptan herramientas y fuentes OSINT al contrato de adquisición del framework. No planifican investigaciones, crean `Evidence`, aplican reglas ni generan informes. La selección de capacidades sigue siendo determinista y el Core conserva el gobierno de `Investigation`.

`Planner` crea tareas; `Executor` las recorre; `PluginManager` carga e invoca el plugin; el plugin devuelve `RawObservation`. El catálogo de herramientas y su cobertura se describen en [`SPECIFICATION.md`](SPECIFICATION.md).

## 2. Contrato y estructura del paquete

La implementación debe heredar de `BasePlugin` y exponer una clase llamada `Plugin` desde su paquete. `PluginManager` comprueba la presencia de `__init__.py` y `plugin.py`, importa `centaurus.plugins.<plugin_id>` y valida la clase exportada.

| Elemento | Contrato |
| --- | --- |
| `src/centaurus/plugins/<plugin_id>/__init__.py` | Expone la clase `Plugin`, normalmente importándola desde `plugin.py`. |
| `src/centaurus/plugins/<plugin_id>/plugin.py` | Implementa `Plugin(BasePlugin)`. |
| `execute(parameters: dict) -> RawObservation` | Recibe los parámetros de la tarea y devuelve una observación estructurada. |
| Construcción del plugin | El gestor instancia la clase sin argumentos para cada ejecución de tarea. |

El gestor verifica que la salida sea una instancia de `RawObservation`. No acepta una lista, un informe ni una `Evidence` como sustitutos. La estructura del paquete permite cargarlo, pero **no lo incorpora automáticamente al plan**.

## 3. Parámetros y catálogo de capacidades

`ExecutionTask` transporta `plugin_id` y `parameters`. El catálogo estático de capacidades define las plantillas que utiliza el Planner. Los nombres de parámetros pertenecen al contrato de cada herramienta; no hay una clave universal `target`.

Ejemplos existentes:

| Tarea | Parámetros construidos por el catálogo |
| --- | --- |
| WHOIS para dominio | `domain` |
| RDAP para dominio / IP | `domain` / `ip`, según el tipo de objetivo |
| DNSRecon para DMARC | `domain` y `mode="dmarc"` |

La CLI consulta el mismo catálogo para mostrar capacidades. Esa consulta no ejecuta plugins ni demuestra la disponibilidad de las dependencias o fuentes externas. La incorporación de una herramienta requiere actualizar explícitamente las capacidades aplicables; no se descubre un plan nuevo por instrucciones al LLM.

## 4. RAW, normalización y persistencia

`RawObservation` conserva `source` (`EvidenceSource`), `data` y `collected_at`. Es un objeto de aplicación anterior al conocimiento de dominio. No debe inventarse una observación vacía para ocultar un error de adquisición.

El Core coordina la persistencia RAW antes de crear evidencias. `EvidenceManager` selecciona el normalizador por fuente y construye `Evidence` conservando su procedencia y tiempo de recogida. Una fuente sin normalizador registrado se rechaza. Los normalizadores estabilizan representación y vocabulario; las conclusiones pertenecen a `RuleEngine`.

Para una nueva fuente, revisa `EvidenceSource` y la selección de normalizadores en `EvidenceManager`. Una nueva herramienta no exige por sí sola nuevas reglas: estas se justifican por preguntas del dominio. Consulta [`RULES_AND_RULE_ENGINE.md`](RULES_AND_RULE_ENGINE.md) y [`STORAGE.md`](STORAGE.md).

## 5. Errores y dependencias externas

`PluginManager` conserva `PluginExecutionError` y envuelve otras excepciones manteniendo su causa. `Executor` transforma los fallos de esa frontera en `ExecutionFailure` y continúa con las tareas siguientes. Las categorías son `timeout`, `unavailable`, `upstream_error`, `invalid_output` y `execution_error`.

El fallo no entra en normalización ni se convierte en evidencia de ausencia. Una excepción posterior durante normalización o persistencia es un fallo del pipeline, con el tratamiento descrito en [`CORE_RUNTIME.md`](CORE_RUNTIME.md).

Las herramientas de proceso externo se invocan mediante argumentos explícitos, sin `shell=True`, con timeout y tratamiento de salida. Sus archivos auxiliares no sustituyen la persistencia oficial. La distribución Docker separa las dependencias incompatibles de DNSRecon, Sublist3r y TheHarvester en entornos propios; ese aislamiento de dependencias no constituye un sandbox por plugin. Los plugins instalados forman parte de la base de confianza.

## 6. Secuencia de integración

1. Define la capacidad pasiva y autorizada que añade la fuente, los parámetros y los errores esperados.
2. Implementa el contrato del paquete y prepara muestras RAW representativas sin datos sensibles innecesarios.
3. Define la fuente y su normalización; conserva el RAW original y prueba datos ausentes, tipos y variantes reales.
4. Integra las plantillas necesarias en el catálogo de capacidades y verifica su representación en la CLI.
5. Actualiza las dependencias y los locks del runtime correspondiente si hacen falta; evita mezclar entornos incompatibles.
6. Valida plugin, normalizador, integración, persistencia y recorrido completo conforme a [`TESTING.md`](TESTING.md). Cuando se dependa de una herramienta externa, valida también el runtime real.
7. Actualiza cobertura y documentación pública, manteniendo las reglas independientes del formato de la herramienta.

## 7. Referencias de implementación

- [`base_plugin.py`](../src/centaurus/plugins/base_plugin.py): interfaz del plugin.
- [`plugin_manager.py`](../src/centaurus/plugin_manager/plugin_manager.py): validación, carga e invocación.
- [`catalog.py`](../src/centaurus/capabilities/catalog.py): capacidades y plantillas de tareas.
- [`raw_observation.py`](../src/centaurus/evidence/raw_observation.py): contrato RAW.
- [`evidence_manager.py`](../src/centaurus/evidence/evidence_manager.py): selección de normalización.
- [`execution_failure.py`](../src/centaurus/executor/execution/execution_failure.py): clasificación de fallos.
