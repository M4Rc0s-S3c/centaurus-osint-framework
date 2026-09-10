# Guía de desarrollo

[Inicio](README.md) · [Arquitectura](ARCHITECTURE.md) · [Estándares](STANDARDS.md)

## 1. Flujo de trabajo

```text
necesidad
  ↓
análisis
  ↓
diseño
  ↓
implementación
  ↓
pruebas
  ↓
revisión
  ↓
commit
```

Un componente nuevo no debe incorporarse sin responsabilidad y contrato definidos.

## 2. Principios

- diseñar antes de implementar;
- YAGNI / KISS / SRP;
- contratos públicos mínimos;
- bajo acoplamiento;
- alta cohesión;
- Core neutral respecto a herramientas;
- dominio independiente de infraestructura;
- configuración operacional separada de semántica analítica;
- evolución incremental basada en necesidad real.

## 3. Dependencias y colaboraciones

Una dependencia directa entre componentes es válida cuando forma parte del contrato arquitectónico.

Ejemplos:

```text
Core → Planner
Core → Executor
Executor → PluginManager
PluginManager → BasePlugin
Core → EvidenceManager
Core → RuleEngine
Core → ReportManager
```

No se permiten:

- dependencias laterales ad hoc;
- acceso directo a implementaciones saltándose contratos;
- modificación de `Investigation` fuera del Core;
- inversión accidental de ownership.

## 4. Añadir un plugin

Una nueva herramienta debe:

1. implementar el contrato de `BasePlugin`;
2. producir `RawObservation` o un fallo contractual estable;
3. disponer de normalizador cuando corresponda;
4. no crear directamente `Evidence`, `Finding` o `Report`;
5. no introducir lógica específica de herramienta en Core o `RuleEngine`;
6. documentar el mapping RAW → Evidence;
7. incluir pruebas focales;
8. incluir prueba de integración/runtime cuando dependa de una herramienta externa.

## 5. Añadir una Rule

Una nueva `Rule` debe empezar por una pregunta objetiva del dominio.

Solo debe ampliarse `RuleEngine` cuando una regla real no pueda representarse mediante las capacidades existentes.

## 6. LLM

Los cambios relacionados con LLM deben respetar:

- separación LLM #1 / LLM #2;
- `Target` determinista;
- no tool-calling;
- grounding de LLM #2;
- salida LLM #2 no autoritativa;
- ausencia de persistencia de la asistencia;
- fail-soft posterior al `Report`.

Los parámetros operacionales solo deben modificarse cuando exista una necesidad demostrada.

## 7. Persistencia

- no introducir rutas físicas en objetos de dominio;
- persistir RAW antes de normalizar;
- mantener `Evidence`, `Finding` y `Report` diferenciados;
- mantener `ExecutionFailure` fuera del Knowledge Pipeline;
- no sobrescribir conocimiento histórico.

Consulta [`STORAGE.md`](STORAGE.md).

## 8. Entorno de desarrollo

El proyecto requiere Python 3.12 o superior según la configuración versionada.

Ejemplo de entorno local:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-core.lock
python -m pip install --no-deps -e .
python -m pip check
```

En Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-core.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pip check
```

## 9. Pruebas

Ejecutar la suite:

```bash
python -m pytest
```

Para cambios Python, comprobar además sintaxis:

```bash
python -m compileall -q src tests
```

Antes del commit:

```bash
git diff --check
```

No realizar staging/commit mientras existan pruebas fallando.

## 10. Revisión Git

Flujo recomendado:

```bash
git status
git diff
git diff --check
python -m pytest

git add <rutas>
git diff --cached
git status

git commit -m "<tipo>: <descripción>"
git push
```

Tras el push:

```bash
git status
```

El árbol de trabajo debe quedar limpio.

## 11. Convención de commits

Se recomienda utilizar mensajes compactos y descriptivos.

Ejemplos:

```text
feat: add new OSINT capability
fix: handle upstream timeout
test: add plugin integration coverage
docs: update deployment guide
refactor: simplify evidence mapping
```

## 12. Qué no hacer

- lógica de negocio global sin responsabilidad definida;
- acoplar `RuleEngine` a RAW específico de una herramienta;
- introducir settings libres para semántica analítica;
- permitir al LLM seleccionar/ejecutar herramientas;
- convertir errores operacionales en conocimiento;
- reabrir arquitectura solo por estética;
- versionar workspaces, modelos, logs, secretos o artefactos generados.

## 13. Contribuciones

Antes de proponer un cambio:

1. limitar el alcance;
2. mantener la compatibilidad contractual;
3. añadir/actualizar pruebas;
4. actualizar documentación pública afectada;
5. comprobar licencias de dependencias incorporadas;
6. respetar [`LICENSE`](LICENSE) y [`NOTICE.md`](NOTICE.md).

## 14. Documentación relacionada

- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`STANDARDS.md`](STANDARDS.md)
- [`SPECIFICATION.md`](SPECIFICATION.md)
- [`INSTALL.md`](INSTALL.md)
