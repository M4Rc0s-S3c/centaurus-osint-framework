# Estándares oficiales del proyecto

**Estado:** FINAL · derivado de Constitución v2 y contratos vigentes

## 1. Arquitectura

1. `Investigation` es la unidad central del dominio y Core es su único custodio/lifecycle authority.
2. Los componentes especializados colaboran únicamente mediante **contratos públicos explícitos**. Están prohibidas las dependencias laterales no documentadas, no las colaboraciones contractuales válidas (`Executor → PluginManager`).
3. Core conserva la orquestación macroscópica y la integración del dominio; no necesita mediar físicamente en cada llamada interna autorizada.
4. Cada componente mantiene responsabilidad única y contrato público mínimo.
5. El dominio es independiente de filesystem, Docker, Ollama, CLI y plugins concretos.
6. Las tools se integran mediante plugins; Core y RuleEngine no contienen lógica tool-specific.
7. Los recursos pesados se adquieren/liberan bajo demanda cuando el contrato lo requiere.
8. La seguridad mantiene autoridad clara y controles en las fronteras donde existe el riesgo; no se dispersa lógica arbitraria ni se fuerza un único módulo técnico de seguridad.

## 2. Dominio

1. Investigation es raíz del agregado.
2. Solo Core crea/modifica su lifecycle e integra Evidence/Finding/Report.
3. Target e Intent son referenciados por Investigation, forman parte de su identidad conceptual y permanecen estables.
4. `Rule` es Value Object del dominio; RuleEngine es servicio de dominio y único productor de Findings.
5. Evidence conserva hechos; Finding conserva conclusiones; Report consolida conocimiento.
6. Todo Finding debe ser explicable mediante Rule y Evidence soporte.
7. `RawObservation`, `ExecutionPlan`, `ExecutionTask`, `ExecutionFailure` y salida LLM #2 no son conocimiento del dominio.

## 3. Knowledge Pipeline

1. RAW se persiste antes de normalizar.
2. Normalización estabiliza representación; no interpreta.
3. Un fallo de adquisición no se convierte en Evidence de ausencia.
4. RuleEngine trabaja sobre Evidence normalizada, no sobre RAW.
5. Finding se persiste de forma independiente de Report.
6. Report se construye/persiste antes de LLM #2.
7. ExecutionFailure se persiste en una rama operacional separada y nunca alimenta Rules.

## 4. Desarrollo

1. Primero se diseña; después se implementa.
2. No se introduce infraestructura para futuros hipotéticos.
3. Un componente nuevo requiere responsabilidad y contrato definidos.
4. Una nueva tool no reabre el dominio.
5. Una nueva Rule requiere una pregunta objetiva del dominio.
6. Una nueva capacidad de RuleEngine requiere necesidad demostrada por Rules reales.
7. Una dependencia entre componentes debe corresponder a una colaboración ya aprobada o requerir decisión arquitectónica explícita.

## 5. Testing

1. Tests por comportamiento observable y contrato.
2. Preferir API pública.
3. Un test verifica una responsabilidad clara.
4. Refactors internos sin cambio contractual no deben romper la suite por detalles internos.
5. No se hace staging/commit con tests fallando.
6. Lo que depende del runtime real requiere validación en el runtime real.

## 6. Persistencia

1. `investigation_id` es el eje lógico de trazabilidad.
2. Los objetos de dominio no conocen rutas físicas.
3. RAW/Evidence/Finding/Report son artefactos diferenciados.
4. RAW se materializa en `evidences/raw/` y Evidence normalizada en `evidences/normalized/` según la referencia de implementación real vigente.
5. ExecutionFailure se conserva fuera de esas ramas de conocimiento, bajo persistencia operacional separada.
6. El conocimiento histórico no se sobrescribe ni elimina en el flujo normal.
7. La salida LLM #2 no se persiste.

## 7. LLM

1. LLM #1 clasifica Intent; no detecta Target ni planifica tools.
2. Target se construye de forma determinista.
3. LLM #2 opera únicamente después de Report.
4. Hechos target-specific deben estar grounded en Report.
5. Salida LLM #2 es efímera/no autoritativa.
6. Structured output controla forma, no verdad semántica.
7. No usar repair/retry probabilístico como frontera de seguridad semántica.

### Perfil operacional LLM #2 post-D2

1. LLM #2 usa un perfil operacional separado: `timeout=300`, `num_ctx=8192`, `num_predict=UNSET`.
2. LLM #1 conserva su perfil previo; D2 no traslada estos parámetros al rol de interpretación.
3. `think=false`, `keep_alive=0` y la ausencia de reintentos automáticos permanecen como decisiones vigentes.
4. Un timeout/error de LLM #2 después de existir Report es un fallo operacional de asistencia: `report.json`/`report.md` siguen siendo válidos y autoritativos.
5. La telemetría puede registrar metadatos operacionales seguros, pero no contenido de prompt, Report ni pregunta del analista.

## 8. Documentación

1. Autoridad temática + última decisión aprobada.
2. Constitución v2 gobierna principios transversales; documentos especializados gobiernan sus materias.
3. Versiones sustituidas permanecen históricas, no simultáneamente normativas.
4. Un documento no se declara FINAL si todavía depende de un hito de aceptación abierto.
5. Una discrepancia entre documentación e implementación real debe quedar explícitamente reconciliada.

## Base documental

Constitución Arquitectónica v2.0; ADR v3.2; Modelo Conceptual v3.5; contratos consolidados; Runtime v2.10; Runtime Configuration v1.4; Reporting v1.5; Tools-Plugins v2.4; OLLAMA-D2 R2; filosofía de testing/desarrollo vigente.
