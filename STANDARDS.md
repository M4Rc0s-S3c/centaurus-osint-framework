# Estándares del proyecto

[Inicio](README.md) · [Arquitectura](ARCHITECTURE.md) · [Desarrollo](DEVELOPMENT.md)

## 1. Arquitectura

1. `Investigation` es la unidad central del dominio.
2. El Core gobierna su ciclo de vida.
3. Los componentes colaboran mediante contratos públicos explícitos.
4. Core mantiene la orquestación macroscópica sin necesidad de mediar físicamente en cada colaboración autorizada.
5. Cada componente mantiene una responsabilidad clara.
6. El dominio no depende de filesystem, Docker, Ollama, CLI o plugins concretos.
7. Las herramientas se integran mediante plugins.
8. No se introduce lógica específica de herramienta en Core o `RuleEngine`.
9. Los recursos pesados se adquieren/liberan bajo demanda cuando corresponda.
10. La seguridad se aplica en las fronteras donde existe el riesgo.

## 2. Dominio

1. `Investigation` referencia `Target` e `Intent`.
2. `Rule` pertenece al dominio.
3. `RuleEngine` produce `Findings`.
4. `Evidence` representa hechos normalizados.
5. `Finding` representa una conclusión determinista.
6. `Report` consolida conocimiento.
7. Un `Finding` debe ser explicable mediante su `Rule` y las `Evidence` que lo soportan.
8. `RawObservation`, `ExecutionPlan`, `ExecutionTask`, `ExecutionFailure` y la salida de LLM #2 no son conocimiento de dominio.

## 3. Knowledge Pipeline

1. RAW se persiste antes de normalizar.
2. La normalización estabiliza representación; no interpreta.
3. Un fallo de adquisición no se convierte en Evidence de ausencia.
4. `RuleEngine` trabaja sobre `Evidence`.
5. `Finding` se persiste de forma independiente.
6. `Report` se construye y persiste antes de LLM #2.
7. `ExecutionFailure` permanece en una rama operacional separada.

## 4. Plugins

Una nueva herramienta debe:

- implementar el contrato del plugin;
- devolver `RawObservation` o un fallo contractual estable;
- disponer de normalizador cuando corresponda;
- no crear directamente `Evidence`, `Finding` o `Report`;
- no acoplar Core a esquemas específicos de herramienta;
- incluir pruebas adecuadas.

## 5. Rules

Una nueva `Rule` debe expresar una pregunta objetiva del dominio.

Solo se amplía `RuleEngine` cuando una necesidad real no puede representarse mediante sus capacidades existentes.

## 6. LLM

1. LLM #1 clasifica `Intent`.
2. `Target` se construye de forma determinista.
3. LLM #1 no planifica herramientas.
4. LLM #2 opera únicamente después de `Report`.
5. La salida de LLM #2 es grounded, efímera y no autoritativa.
6. Structured output controla forma, no verdad semántica.
7. Un timeout/error de LLM #2 no invalida el informe determinista.

Perfil actual de LLM #2:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

## 7. Persistencia

1. `investigation_id` es el eje de trazabilidad.
2. Los objetos de dominio no conocen rutas físicas.
3. RAW, Evidence, Finding y Report se materializan como artefactos diferenciados.
4. RAW se conserva bajo `evidences/raw/`.
5. Evidence normalizada se conserva bajo `evidences/normalized/`.
6. `ExecutionFailure` permanece bajo `execution/failures/`.
7. El conocimiento histórico no se sobrescribe en el flujo normal.
8. La salida LLM #2 no se persiste.

## 8. Testing

1. Probar comportamiento observable y contratos.
2. Preferir APIs públicas.
3. Mantener pruebas focales por responsabilidad.
4. Los refactors internos no deben romper pruebas basadas únicamente en detalles de implementación.
5. No hacer commit con pruebas fallando.
6. Lo que depende del runtime real requiere validación del runtime real.

## 9. Git

Antes de integrar cambios:

```bash
git diff --check
python -m pytest
```

Según el alcance, revisar además:

- suite focal;
- smoke tests;
- runtime real;
- cambios preparados;
- estado limpio del árbol de trabajo.

## 10. Documentación

1. La documentación pública debe describir el comportamiento vigente.
2. Los literales técnicos no se traducen ni reinterpretan.
3. Las rutas, comandos, flags, hashes y nombres de componentes se mantienen exactos.
4. Una discrepancia entre documentación e implementación debe resolverse explícitamente.
5. La documentación del repositorio debe ser útil para usuarios y desarrolladores sin depender de material interno de proyecto.

## 11. Seguridad y uso responsable

- no introducir credenciales privadas en el repositorio;
- no registrar contenido sensible de prompts o informes en telemetría;
- aplicar mínimo privilegio;
- mantener separadas las fronteras de administración y operación;
- utilizar CENTAURUS únicamente en contextos legítimos y autorizados.

## 12. Licencia

Las contribuciones y redistribuciones deben respetar [`LICENSE`](LICENSE) y [`NOTICE`](NOTICE).
