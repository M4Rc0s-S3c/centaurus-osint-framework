# Arquitectura LLM

[Español](LLM_ARCHITECTURE.md) | [English](LLM_ARCHITECTURE.en.md)

[Inicio](../README.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`DEVELOPMENT.md`](DEVELOPMENT.md)

## 1. Dos roles, una autoridad determinista

CENTAURUS utiliza Ollama para dos roles lógicos separados. Pueden compartir servicio y modelo físico, pero tienen contratos y perfiles independientes. El LLM no selecciona herramientas, ejecuta acciones ni produce hallazgos autoritativos.

| Rol | Entrada | Salida aceptada | Efecto de un fallo |
| --- | --- | --- | --- |
| LLM #1 | Petición en lenguaje natural | Un `Intent` permitido | Puede impedir iniciar la investigación por ese recorrido. |
| LLM #2 | Proyección limitada del `Report` ya persistido | Asistencia validada y efímera | Un error LLM gestionado deja disponible el informe determinista. |

Los valores operacionales y sus diferencias por modalidad están en [`CONFIGURATION.md`](CONFIGURATION.md). La gestión de la ejecución pertenece a [`CORE_RUNTIME.md`](CORE_RUNTIME.md).

## 2. Interpretación de la petición

`RequestInterpreter` construye primero el Target mediante `TargetFactory`, de forma determinista, y después solicita al proveedor la clasificación del Intent. Ambos se integran en `StructuredRequest`.

LLM #1 recibe la petición del usuario. Su contrato exige un objeto JSON con la única clave `intent`, cuyo valor debe pertenecer al catálogo permitido. Una respuesta inválida se rechaza; no se adivinan campos ni se convierte texto libre en un plan. El Intent actual es `public_exposure_assessment`.

La validación de `StructuredRequest` comprueba tipo de objetivo, Intent y normalización. El catálogo operacional determina qué objetivos se pueden investigar. La existencia conceptual de EMAIL o CERTIFICATE no los convierte en objetivos operativos.

## 3. Qué recibe LLM #2

`LLMManager` delega en un proveedor que serializa el informe mediante una lista explícita de campos. Esa proyección es distinta del JSON persistido.

| Incluido en la proyección | Excluido como campo de la proyección |
| --- | --- |
| `investigation_id` | `analyst_question`, `generated_at`, `target`, `target_type`, `intent` |
| Referencia y conclusión de cada hallazgo | `Evidence.data` y observaciones RAW |
| Identificador, versión, nombre, categoría y descripción de la regla | Condiciones completas de la regla |
| `source` y `collected_at` de las evidencias de apoyo | Fallos operacionales y logs |

La exclusión de campos no es anonimización: una conclusión puede contener valores específicos del objetivo. Tampoco elimina esos datos del informe persistido. `report.json` conserva reglas, evidencias de apoyo y contexto; la petición original puede aparecer en ambos informes. Consulta [`STORAGE.md`](STORAGE.md).

## 4. Contrato de presentación

La respuesta estructurada contiene exactamente `executive_summary`, `finding_summaries`, `risk_considerations` y `recommendations`.

Las referencias `F-001`, `F-002`, etc. se asignan por el orden de los hallazgos del informe. El resumen ejecutivo debe referenciar todos los hallazgos; debe existir exactamente un resumen por hallazgo, sin referencias desconocidas ni duplicadas. Los resúmenes se ordenan de forma determinista antes de presentarse.

Cada lista orientativa admite un máximo de cinco elementos. Un informe sin hallazgos no admite consideraciones de riesgo ni recomendaciones. La estructura JSON controla la forma de la respuesta; no demuestra por sí sola la veracidad de su contenido.

## 5. Validación y omisiones

| Frontera | Comportamiento |
| --- | --- |
| JSON, campos, tipos o referencias inválidos | Rechazo de la respuesta mediante `LLMResponseError`. |
| Contenido factual obligatorio que no supera el grounding | Rechazo de la presentación; no se acepta un resumen factual parcial. |
| Elemento orientativo estructuralmente válido que no supera el control semántico | Omisión individual; los elementos aceptados pueden presentarse. |
| Omisiones orientativas | El renderer informa del número de elementos omitidos, sin mostrar ni persistir su texto. |

La omisión individual se aplica después de validar la estructura. No significa que cualquier respuesta mal formada sea recuperable. Los controles deterministas contrastan el texto con el contexto permitido y rechazan determinadas afirmaciones incompatibles; no verifican de forma independiente las fuentes ni garantizan toda afirmación generada.

No hay un mecanismo automático de reparación o repetición semántica para conseguir una salida aceptable. La asistencia no modifica `Evidence`, `Finding` ni `Report` y no se persiste como informe.

## 6. Perfiles y recursos

Los perfiles de interpretación y asistencia son objetos separados e inmutables. Los parámetros de muestreo están versionados en [`inference_profile.py`](../src/centaurus/llm/inference_profile.py); no son ajustes libres del analista.

La composición del runtime aplica a LLM #2 sus ajustes específicos de timeout, contexto y límite opcional de generación. Sus valores se mantienen en [`CONFIGURATION.md`](CONFIGURATION.md), sin duplicarlos aquí. No se trasladan automáticamente a LLM #1.

El proveedor de asistencia solicita `keep_alive=0` para liberar el modelo después de la generación. Esta solicitud no garantiza recuperación de cualquier falta de memoria ni demuestra que el servidor haya terminado su trabajo cuando el cliente agota un timeout. La compatibilidad y el consumo requieren comprobación del entorno real.

## 7. Errores y observabilidad

Los errores gestionados de transporte, HTTP y validación se expresan mediante excepciones LLM. El Core registra la incidencia después de persistir el informe y continúa sin asistencia. Esta política no convierte cualquier excepción inesperada o caída del proceso en un fallo recuperable.

La telemetría del proveedor utiliza duración, estado HTTP, causa y contadores cuando están disponibles. No vuelca el prompt, la proyección del informe ni la respuesta completa. Los logs generales pueden contener contexto operativo y deben revisarse antes de compartirlos.

Los límites de confianza se describen en [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md), y las comprobaciones funcionales en [`TESTING.md`](TESTING.md).

## 8. Referencias de implementación

- [`request_interpreter.py`](../src/centaurus/llm/request_interpreter.py)
- [`ollama_intent_provider.py`](../src/centaurus/llm/ollama_intent_provider.py)
- [`serialization.py`](../src/centaurus/llm/serialization.py): proyección para LLM #2.
- [`presentation.py`](../src/centaurus/llm/presentation.py): esquema, validación y renderer.
- [`ollama_provider.py`](../src/centaurus/llm/ollama_provider.py)
- [`llm_manager.py`](../src/centaurus/llm/llm_manager.py)
