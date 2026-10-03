# Estrategia de pruebas

[Español](TESTING.md) | [English](TESTING.en.md)

[Inicio](../README.md) · [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`DEVELOPMENT.md`](DEVELOPMENT.md)

## 1. Propósito y preparación

Las pruebas verifican contratos y comportamiento observable. Deben permitir refactorizaciones que preserven esos contratos, evitando depender innecesariamente de detalles privados. Una prueba focal debe tener un objetivo claro y una causa de fallo interpretable.

La preparación del entorno, la instalación de `pytest` y los comandos de suite, sintaxis y revisión Git se mantienen en [`DEVELOPMENT.md`](DEVELOPMENT.md). Este documento explica qué comprobar y cómo interpretar los resultados; no declara una ejecución reciente ni un número vigente de pruebas superadas.

## 2. Niveles y límites

| Nivel | Qué demuestra | Qué no demuestra por sí solo |
| --- | --- | --- |
| Unitario / contractual | Tipos, invariantes, validadores, reglas, serialización y contratos de componentes. | Disponibilidad real de una fuente, herramienta o modelo. |
| Integración | Colaboración entre componentes y persistencia en un entorno controlado. | Equivalencia entre todos los sistemas operativos o modalidades de despliegue. |
| Recorrido completo reproducible | Paso por CLI, Core, adquisición adaptada, conocimiento, informes y presentación, con fronteras externas controladas. | Una investigación real contra servicios externos si estos están simulados. |
| Runtime real | Comportamiento de Docker, herramientas, Ollama, permisos, recursos y plataforma efectivamente ensayada. | Compatibilidad universal o rendimiento de hardware no probado. |

Los dobles deben situarse en las fronteras que la prueba no pretende validar. Sustituir HTTP o un proceso externo permite repetir escenarios sin convertir una prueba local en una afirmación sobre la fuente real. Los tests de `tests/test_e2e.py` incluyen sustituciones de esas dependencias externas.

## 3. Cobertura por responsabilidad

| Área | Comprobaciones relevantes | Referencias de la suite |
| --- | --- | --- |
| Entrada y capacidades | Target determinista, Intent permitido, catálogo y rechazo de entrada inválida. | [`test_request_input.py`](../tests/test_request_input.py), [`test_capabilities.py`](../tests/test_capabilities.py) |
| Plugins y normalización | Parámetros, RAW representativo, errores de adquisición y representación normalizada. | [`test_plugin_manager.py`](../tests/test_plugin_manager.py), [`test_theharvester_normalizer.py`](../tests/test_theharvester_normalizer.py) |
| Reglas | Coincidencia/no coincidencia, tipos, ausencia explícita, tiempos y corroboración entre fuentes. | [`test_rule_engine.py`](../tests/test_rule_engine.py), [`test_exposure_rules.py`](../tests/test_exposure_rules.py) |
| Core y ejecución | Secuencia, validación del plan, resultado parcial, fallo total y autoridad del ciclo. | [`test_core.py`](../tests/test_core.py), [`test_executor.py`](../tests/test_executor.py) |
| Persistencia | Artefactos separados, trazabilidad, rechazo de sobrescritura y fallos de escritura. | [`test_persistence_extended.py`](../tests/test_persistence_extended.py), [`test_raw_observation_store.py`](../tests/test_raw_observation_store.py) |
| LLM | Esquema, referencias, proyección minimizada, rechazo factual y omisiones orientativas. | [`test_llm.py`](../tests/test_llm.py), [`test_inference_profile.py`](../tests/test_inference_profile.py) |
| Presentación y observabilidad | Informe Markdown, códigos de salida, progreso y logging. | [`test_report_markdown.py`](../tests/test_report_markdown.py), [`test_cli_app.py`](../tests/test_cli_app.py), [`test_runtime_progress.py`](../tests/test_runtime_progress.py) |
| Distribución y controles host | Contratos de scripts, configuración, suministro y wrappers. | [`test_linux_distribution.py`](../tests/test_linux_distribution.py), [`test_ova_runtime_broker.py`](../tests/test_ova_runtime_broker.py), [`test_ova_poweroff_helper.py`](../tests/test_ova_poweroff_helper.py) |

Son puntos de entrada representativos, no una lista exhaustiva ni una afirmación de cobertura porcentual.

## 4. Casos de fallo que deben distinguirse

- Una tarea fallida produce `ExecutionFailure`, no una evidencia vacía inventada.
- Un resultado `partial` puede terminar con `InvestigationStatus.COMPLETED` e informe válido.
- Un fallo estructural después de adquirir datos marca la investigación como fallida y conserva los artefactos previos válidos; no se espera rollback global.
- Cero hallazgos puede ser un resultado válido.
- Un error LLM #2 gestionado deja intacto el informe ya persistido.
- La estructura inválida o el contenido factual obligatorio rechazado invalidan la presentación LLM; el filtrado individual corresponde al contenido orientativo validado estructuralmente.
- Los fallos de progreso no deben cambiar conocimiento ni códigos de salida.

Los contratos se detallan en [`CORE_RUNTIME.md`](CORE_RUNTIME.md), [`LLM_ARCHITECTURE.md`](LLM_ARCHITECTURE.md) y [`STORAGE.md`](STORAGE.md).

## 5. Validación sobre el entorno real

Para cambios que afecten a despliegue o dependencias externas, registra el entorno concreto y comprueba los controles relevantes: identidad de imágenes/modelo, permisos, montajes, redes, ejecutables y persistencia. Un test que inspecciona el texto de Compose no demuestra que Docker aplique ese control en ejecución.

La aceptación de OVA/USB requiere ensayos de importación o escritura, arranque, uso del entrypoint, investigación y persistencia tras reinicio en la plataforma objetivo. En USB incluye la red Ethernet real. Los procedimientos operativos se mantienen en sus guías; no se deduce una nueva aceptación física por ejecutar la suite Python.

Las funciones LLM requieren comprobar compatibilidad de salida, casos pequeños y grandes, duración y memoria. Una suite con proveedor simulado no mide consumo de Ollama. La evaluación GPU conserva el alcance experimental de [`GPU_OLLAMA_DOCKER.md`](GPU_OLLAMA_DOCKER.md).

## 6. Registro e interpretación de resultados

Para que una validación sea revisable, conserva commit, entorno, versiones de dependencias, comandos, resultados y limitaciones. Registra por separado pruebas fallidas, omitidas y no ejecutadas; no presentes una herramienta ausente como una suite superada.

Selecciona pruebas focales según el cambio y respeta las comprobaciones de integración de [`STANDARDS.md`](STANDARDS.md). No integres con pruebas fallando. Si no puede ejecutarse una comprobación, deja constancia del motivo y del alcance no demostrado.

En documentación, comprueba rutas, anclajes, navegación ES/EN, literales técnicos y renderizado de diagramas cuando cambien. Esas comprobaciones no sustituyen la validación funcional cuando también cambia el software.

Los recuentos y métricas de cierres históricos describen su commit y plataforma. No deben publicarse como resultado de la versión actual sin una nueva ejecución identificada.

## 7. Documentación relacionada

- [`DEVELOPMENT.md`](DEVELOPMENT.md)
- [`STANDARDS.md`](STANDARDS.md)
- [`PLUGIN_SYSTEM.md`](PLUGIN_SYSTEM.md)
- [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md)
