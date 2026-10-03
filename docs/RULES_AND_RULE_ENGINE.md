# Reglas y motor de reglas

[Español](RULES_AND_RULE_ENGINE.md) | [English](RULES_AND_RULE_ENGINE.en.md)

[Inicio](../README.md) · [USER_GUIDE.md](USER_GUIDE.md) · [ARCHITECTURE.md](ARCHITECTURE.md)

## 1. Función del motor

`RuleEngine` evalúa reglas declarativas sobre `Evidence` normalizada y produce `Finding`. El flujo autoritativo es `Evidence -> Finding -> Report`; el LLM no define las condiciones ni decide qué hallazgos se persisten.

Los hallazgos describen lo observado en las fuentes consultadas. No constituyen por sí mismos una vulnerabilidad, una atribución, una puntuación de riesgo ni una recomendación operativa.

### Qué significa un resultado determinista

Con las mismas evidencias normalizadas, incluidos sus tiempos de recogida, las mismas reglas y orden de evaluación y la misma implementación, el motor produce los mismos hallazgos. Los criterios pueden inspeccionarse y volver a evaluarse sin pedir a un LLM que decida la conclusión.

Esto no garantiza la exactitud de una fuente ni que dos investigaciones en vivo obtengan resultados idénticos: las fuentes, la cobertura y las observaciones pueden cambiar. Tampoco implica informes idénticos byte a byte entre investigaciones, que tienen identificadores y tiempos de generación propios. `report.md` es una proyección determinista de un `Report` concreto.

### Ejemplo controlado: corroboración con RL-014

Supongamos que la evidencia normalizada de Sublist3r contiene `api.example.com` y `www.example.com`, mientras que la de crt.sh contiene `api.example.com` y `mail.example.com`. Evaluar únicamente `RL-014` produce un hallazgo para `api.example.com`, observado en dos fuentes distintas. Conserva la regla y ambas evidencias de apoyo.

Los otros nombres no satisfacen este criterio de corroboración. Eso no demuestra que no existan ni que sean seguros. El ejemplo utiliza datos controlados, no observaciones en vivo de `example.com`. Ilustra cómo unos criterios explícitos convierten observaciones en una conclusión cuyo fundamento puede revisarse mediante [`STORAGE.md`](STORAGE.md#9-trazabilidad).

## 2. Catálogo productivo

El catálogo contiene once reglas, ordenadas por su identificador numérico.

| ID | Versión | Condición observada |
| --- | --- | --- |
| `RL-001` | `1.1` | `registrar` presente con valor `None`. |
| `RL-002` | `1.1` | `name_servers` presente con valor `None`. |
| `RL-003` | `1.1` | `creation_date` o `expiration_date` presente con valor `None`; cada campo se evalúa por separado. |
| `RL-004` | `1.1` | `dnssec` igual a `signedDelegation` o `unsigned`. |
| `RL-005` | `1.1` | `registrant_name` presente con valor `None` o exactamente `[REDACTED]`. |
| `RL-006` | `1.1` | Dominio creado menos de 30 días antes de la recogida de la evidencia. |
| `RL-007` | `1.0` | `spf_records` igual a `[]`. |
| `RL-008` | `1.0` | Más de un elemento en `subdomains`. |
| `RL-009` | `1.0` | Más de un elemento en `emails`. |
| `RL-010` | `1.0` | `dmarc_records` igual a `[]` en la consulta directa a `_dmarc` del dominio objetivo. |
| `RL-014` | `1.0` | Un mismo subdominio observado en al menos dos fuentes de evidencia distintas. |

`RL-011`, `RL-012` y `RL-013` no forman parte del catálogo productivo. La secuencia de identificadores no implica que existan catorce reglas disponibles.

Las reglas de registro trabajan con evidencia normalizada de WHOIS/RDAP; las de DNS, con DNSRecon; y las de exposición pública, con las colecciones normalizadas de las fuentes correspondientes. Una herramienta disponible no garantiza que una consulta produzca todos los campos o hallazgos.

## 3. Semántica de evaluación

- `missing` requiere que la clave exista y su valor sea `None`. Una clave ausente no equivale a una observación de ausencia.
- `redacted` reconoce el marcador explícito; no infiere censura a partir de cualquier cadena vacía.
- Las condiciones de una regla se evalúan individualmente. No forman una conjunción implícita: `RL-003` puede producir hallazgos separados para las dos fechas.
- Las condiciones temporales usan `Evidence.collected_at`, no la fecha actual del equipo. Así se conserva la referencia temporal de la observación.
- Una regla puede producir varios hallazgos, por condición y evidencia coincidente. El número de hallazgos no equivale al número de reglas ejecutadas.

`RL-014` agrega colecciones y cuenta valores distintos de `EvidenceSource`. Repetir observaciones de la misma fuente no aumenta el número de fuentes. Genera un hallazgo por subdominio corroborado, con orden estable de los elementos y referencias a la primera evidencia de apoyo de cada fuente distinta.

## 4. Cómo interpretar los resultados

`RL-004` registra un estado DNSSEC reconocido, incluido `signedDelegation`; no significa necesariamente ausencia de DNSSEC.

`RL-010` describe la consulta directa a `_dmarc` del objetivo. No prueba que falte cualquier política aplicable por herencia ni representa una evaluación completa de DMARC.

La ausencia de SPF observado, un registro reciente o varias direcciones públicas tampoco demuestran una explotación o actividad maliciosa. Contrasta cada conclusión con sus evidencias y con los fallos de ejecución mostrados por separado en la CLI y conservados en `execution/failures/`. Estos fallos no forman parte de `Report`; consulta [`STORAGE.md`](STORAGE.md).

Que no se produzcan hallazgos no certifica la seguridad del objetivo. Puede reflejar condiciones no cumplidas, datos no observados o cobertura limitada de fuentes.

## 5. Inspección y mantenimiento

En la CLI del Core, `centaurus capabilities --rules` permite consultar las reglas disponibles sin iniciar una investigación. Para acceder al Core mediante Compose, utiliza los comandos de [`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md). En el shell de la appliance, consulta la ayuda de capacidades descrita en [`USER_GUIDE.md`](USER_GUIDE.md); el wrapper del host acepta cero argumentos.

El catálogo y sus condiciones se mantienen en código. Un cambio de semántica debe preservar identificadores y versiones de forma explícita, incluir pruebas con evidencia normalizada y revisar el efecto en los informes. Consulta [`DEVELOPMENT.md`](DEVELOPMENT.md) y [`STANDARDS.md`](STANDARDS.md).

## 6. Referencias

- [`rule_engine.py`](../src/centaurus/rules/rule_engine.py)
- [`catalog.py`](../src/centaurus/rules/catalog.py)
- [`registration_rules.py`](../src/centaurus/rules/registration_rules.py)
- [`dns_rules.py`](../src/centaurus/rules/dns_rules.py)
- [`exposure_rules.py`](../src/centaurus/rules/exposure_rules.py)
- [`STORAGE.md`](STORAGE.md)
