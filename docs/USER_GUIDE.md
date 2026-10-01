# CENTAURUS · Guía de uso

[Inicio](../README.md) · [Instalación](INSTALL.md) · [Persistencia](STORAGE.md)

**Versión documental:** 1.0

**Público:** usuarios y analistas que comienzan a trabajar con CENTAURUS.

**Alcance:** operación de la aplicación, lectura de resultados y consulta de informes. La instalación se trata en la documentación de despliegue.

## 1. Qué puedes hacer con CENTAURUS

CENTAURUS permite investigar la exposición pública de un dominio o consultar la información disponible para una dirección IP. Recoge observaciones de distintas fuentes, normaliza los datos y aplica reglas explícitas para producir conclusiones trazables.

El resultado principal es un informe determinista. La asistencia de un modelo de lenguaje puede ayudarte a entenderlo, pero las conclusiones del informe proceden de las reglas del framework.

| Objeto de investigación | Cobertura de la versión documentada |
|---|---|
| Dominio (`DOMAIN`) | Plan de 7 tareas sobre 6 herramientas |
| Dirección IP (`IP`) | Consulta limitada mediante RDAP |
| Correo electrónico (`EMAIL`) | Sin investigación directa disponible |
| Certificado (`CERTIFICATE`) | Investigación directa diferida |

La consulta de Certificate Transparency forma parte del análisis de dominios. Eso no implica que se pueda iniciar una investigación independiente de un certificado. La cobertura de dominios tampoco equivale a una auditoría exhaustiva de seguridad.

## 2. Identifica dónde estás escribiendo

La distribución distingue el terminal del sistema y el shell de la aplicación. El mismo nombre `centaurus` puede corresponder a puntos de entrada distintos según el entorno.

| Contexto | Cómo reconocerlo | Qué debes escribir |
|---|---|---|
| Terminal Linux de la appliance OVA/USB | Prompt del sistema, antes de entrar en la aplicación | `centaurus`, sin argumentos |
| Shell de CENTAURUS | Prompt `centaurus>` | Metacomandos como `/help` o una petición en lenguaje natural |
| Entorno de desarrollo o ejecución con el paquete instalado | Terminal preparado para usar la CLI del paquete | Comandos como `centaurus --help` o `centaurus capabilities` |

En la appliance, el acceso normal es el primer recorrido. No añadas `capabilities`, `shell` ni `investigate` al comando host: ese wrapper acepta cero argumentos.

Para Git + Docker sobre Linux, utiliza el contexto de ejecución indicado por el despliegue; no presupongas que el host dispone del wrapper de la appliance. Consulta [Instalación y despliegue](INSTALL.md).

## 3. Primera sesión en la appliance

### 3.1 Entrar

Inicia sesión en Linux con el usuario operativo `centaurus`. Desde su terminal, ejecuta:

```bash
centaurus
```

Introduce la contraseña del usuario cuando se solicite. El acceso requiere una terminal interactiva y pide autenticación de nuevo en cada sesión.

Cuando aparezca `centaurus>`, ya estás dentro de la aplicación. Los ejemplos siguientes muestran solamente lo que debes escribir, sin incluir el prompt.

### 3.2 Consultar la ayuda y las capacidades

```text
/help
```

Para ver los tipos de objetivo, las herramientas y el catálogo de reglas:

```text
/capabilities --rules
```

También puedes consultar cada parte por separado:

| Entrada | Resultado |
|---|---|
| `/capabilities` | Capacidades de la distribución |
| `/rules` | Catálogo de reglas productivas |
| `/capabilities --rules` | Ambas vistas |
| `/help` | Ayuda del shell |
| `/exit` o `/quit` | Fin de la sesión |

Estas consultas muestran información estática: no ejecutan herramientas ni crean una investigación. El catálogo contrastado contiene 11 reglas. Poder ver las capacidades no demuestra que las fuentes externas o el servicio LLM estén disponibles.

### 3.3 Formular la petición

Escribe una petición clara, con un único objetivo dentro del alcance de tu trabajo. Ejemplo de redacción:

```text
Investiga la exposición pública de example.com
```

`example.com` ilustra el formato; sustitúyelo por el dominio de tu investigación. Este ejemplo no viene acompañado de resultados reales ni garantiza un número determinado de hallazgos.

La aplicación interpreta la petición, valida el objetivo y el propósito, y entrega la solicitud al Core. El plan de herramientas lo decide el framework a partir de sus capacidades; no se elige libremente mediante instrucciones al modelo de lenguaje.

Cada petición ejecutada abre una investigación nueva, incluso si repites el mismo dominio. Repetirla no reanuda ni actualiza el caso anterior.

### 3.4 Esperar al resultado

En una terminal interactiva se muestra la actividad, el tiempo transcurrido, la posición de la tarea en el plan y la herramienta o modo en curso. Las marcas de finalización y degradación permiten seguir el proceso.

No hay porcentaje global ni estimación de tiempo restante. La duración depende de las fuentes consultadas y de los recursos disponibles. Tras las tareas de adquisición puede continuar la elaboración o presentación del resultado; una pausa visible, por sí sola, no demuestra que la aplicación se haya bloqueado.

## 4. Cómo leer el resultado

Empieza por el objetivo y el estado; después revisa los fallos de fuentes y los hallazgos. Conserva el identificador de la investigación si vas a consultar sus artefactos o comunicar una incidencia.

| Campo visible | Cómo interpretarlo |
|---|---|
| `Investigation` | Identificador del caso |
| `Target` | Tipo y valor del objetivo investigado |
| `Intent` | Propósito admitido; el catálogo contrastado usa `public_exposure_assessment` |
| `Status` | Estado presentado para la ejecución |
| `Evidence` | Número de evidencias normalizadas |
| `Findings` | Número de conclusiones producidas por reglas |
| `Rule` / `Conclusion` | Regla y conclusión de cada hallazgo |
| `Tool execution failures` | Fuentes o tareas que fallaron y su diagnóstico |
| `LLM analyst assistance — ephemeral` | Explicación generativa, cuando está disponible |

### Evidencia, hallazgo e informe

Una **evidencia** representa un dato normalizado obtenido de una fuente. Un **hallazgo** representa lo que puede concluirse al aplicar una regla a una o varias evidencias. El **informe** consolida los hallazgos del caso.

Por ejemplo, una fuente puede observar un subdominio. Si otra fuente lo corrobora y se cumplen los criterios de la regla correspondiente, el framework puede producir una conclusión de corroboración. Esa conclusión no demuestra por sí misma que el subdominio sea vulnerable.

El número de hallazgos no es una puntuación global de riesgo. Un resultado con cero hallazgos tampoco certifica que el objetivo carezca de exposición o problemas: debe interpretarse junto con la cobertura y las evidencias disponibles.

### Ejecución parcial

`PARTIAL — completed with reduced tool coverage` indica que hubo cobertura reducida por fallos operacionales. Si se produjo un informe válido, conserva utilidad dentro de esa cobertura.

Revisa qué fuente falló antes de extraer conclusiones. Que una fuente no responda no demuestra que el dato buscado no exista. Un fallo operacional se registra por separado y no se convierte en un hallazgo.

### Investigación fallida

Si se presenta `FAILED` y se indica que no se produjo un informe final, no trates el caso como completado. Pueden conservarse observaciones, evidencias o hallazgos persistidos antes del fallo; sirven para revisión y diagnóstico, pero no sustituyen al informe final ausente.

## 5. Qué resultado conservar y dónde encontrarlo

| Artefacto | Para qué sirve |
|---|---|
| `report.json` | Representación estructurada autoritativa del informe |
| `report.md` | Lectura humana determinista del mismo informe |
| Evidencias normalizadas | Revisar los datos que sustentan el análisis |
| Observaciones RAW | Consultar las respuestas originales conservadas |
| Fallos de ejecución | Explicar la cobertura que faltó |
| Texto de asistencia LLM | Ayuda de lectura efímera; no forma parte del informe persistido |

Las rutas de los informes, relativas al workspace configurado, son:

```text
investigations/<investigation-id>/reports/report.json
investigations/<investigation-id>/reports/report.md
```

En el runtime de contenedor, la ubicación habitual es `/workspace`. La ruta del host que respalda ese volumen depende del despliegue: no debe confundirse con una carpeta necesariamente accesible al usuario de la appliance.

La CLI de esta versión no ofrece un navegador histórico ni un comando para abrir o exportar informes anteriores. Para recuperar los ficheros, utiliza el acceso al workspace previsto por tu instalación o solicita al responsable del entorno una copia del directorio del caso. Consulta el [modelo de persistencia](STORAGE.md) para las demás rutas.

Al entregar un resultado, acompaña el informe con su identificador, el objetivo y las limitaciones de cobertura relevantes. No presentes una captura de la explicación LLM como sustituto del informe.

## 6. Qué papel tiene la asistencia LLM

El modelo interviene en dos momentos distintos:

| Momento | Función | Qué implica un fallo |
|---|---|---|
| Interpretación de la petición, LLM #1 | Ayudar a obtener una solicitud con propósito admitido | Puede impedir iniciar la investigación por el recorrido natural |
| Asistencia posterior, LLM #2 | Explicar el informe ya producido y persistido | Puede faltar la explicación, conservándose el informe determinista |

Si aparece `LLM analyst assistance unavailable; the deterministic Report remains the authoritative persisted result.`, consulta el informe. El mensaje no implica que debas repetir automáticamente toda la investigación.

Las recomendaciones del modelo son orientativas. Para fundamentar una decisión, vuelve al hallazgo, la regla y las evidencias. Si la explicación generativa discrepa del informe, prevalece el informe determinista.

## 7. Incidencias habituales

| Situación | Comprobación o siguiente paso |
|---|---|
| El acceso host rechaza `centaurus capabilities` | En la appliance ejecuta solo `centaurus`; dentro usa `/capabilities` |
| El acceso a la appliance falla antes de mostrar `centaurus>` | Revisa el mensaje y comunícalo al responsable del entorno; puede requerir intervención sobre los servicios |
| Aparece `Invalid request` | Revisa el objetivo y formula una petición simple dentro de los tipos admitidos |
| Aparece un error LLM durante la interpretación | Conserva el mensaje; solicita revisar la disponibilidad y configuración de Ollama antes de repetir |
| Una herramienta falla y el resultado es parcial | Lee la tabla de fallos y documenta la cobertura reducida |
| No se producen hallazgos | Revisa evidencias y cobertura; cero hallazgos no equivale a ausencia de riesgo |
| Falta la asistencia LLM después del informe | Utiliza el informe persistido; la explicación adicional puede haber fallado |
| No encuentras una investigación anterior desde el shell | No hay consulta histórica en la CLI; utiliza el acceso al workspace definido por el despliegue |

Para comunicar una incidencia, indica la modalidad de uso, el punto donde ocurrió, el mensaje exacto y el identificador del caso si llegó a generarse. Incluye solo los datos necesarios para el diagnóstico.

## 8. Terminar la sesión y apagar la appliance

Para salir de la aplicación:

```text
/exit
```

También se admite `/quit`. Volverás al terminal Linux; salir de la aplicación no apaga la appliance ni elimina sus informes persistidos.

Si quieres apagar la appliance OVA/USB documentada, ejecuta desde el terminal Linux:

```bash
centaurus-poweroff
```

El comando requiere una terminal interactiva, acepta cero argumentos y vuelve a solicitar la contraseña del usuario operativo. No existe `/poweroff` dentro del shell de CENTAURUS.

## 9. Referencia de la CLI del paquete

Esta sección corresponde a un entorno donde se ejecuta directamente el paquete, como desarrollo o el contexto de contenedor preparado. No corresponde al wrapper host de la appliance.

```bash
centaurus --help
centaurus --version
centaurus capabilities
centaurus capabilities --rules
centaurus rules
centaurus shell
python -m centaurus --help
```

El subcomando `investigate` recibe la petición en lenguaje natural como argumento. Consulta su ayuda con `centaurus investigate --help` en ese contexto de ejecución.

| Código de salida de una investigación directa | Significado |
|---|---|
| `0` | Resultado utilizable; incluye una ejecución parcial con informe válido |
| `1` | Error interno o configuración inválida |
| `2` | Petición inválida |
| `3` | Fallo operacional que impide completar el resultado utilizable |

Estos códigos no deben usarse para deducir el resultado de todas las peticiones hechas dentro de una sesión interactiva: el shell permite continuar después de una petición fallida y su salida normal devuelve `0`.
