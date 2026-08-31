# Guía de desarrollo

**Estado:** FINAL

## 1. Disciplina

```text
Diseño
→ análisis arquitectónico
→ aprobación
→ implementación
→ tests
→ revisión
→ commit
```

Un componente nuevo no se incorpora sin responsabilidad y contrato definidos.

## 2. Principios

- diseñar antes de implementar;
- YAGNI/KISS/SRP;
- contratos públicos mínimos;
- bajo acoplamiento y alta cohesión;
- Core neutral respecto a tools;
- dominio independiente de infraestructura;
- configuración operacional separada de semántica analítica;
- evolución incremental basada en necesidad demostrada.

## 3. Dependencias y colaboraciones

No existe una prohibición absoluta de dependencias directas entre componentes. La regla vigente es:

> una colaboración directa solo es válida si forma parte del contrato arquitectónico aprobado y respeta la responsabilidad de ambos extremos.

Ejemplos canónicos:

- Core → Planner;
- Core → Executor;
- Executor → PluginManager;
- PluginManager → BasePlugin;
- Core → EvidenceManager / RuleEngine / ReportManager / stores;
- Core → RuntimeProgressReporter opcional.

No se permiten:

- dependencias laterales ad hoc para “acortar” el flujo;
- acceso a una implementación concreta saltándose el contrato;
- componentes que modifiquen directamente Investigation fuera de Core;
- inversión accidental de ownership.

## 4. Plugins

Una nueva tool debe:

- implementar `BasePlugin.execute(parameters: dict) -> RawObservation`;
- producir RAW válido o fallo contractual estable;
- disponer de normalizador específico cuando corresponda;
- no crear Evidence/Finding/Report;
- no introducir lógica tool-specific en Core o RuleEngine;
- documentar mapping RAW → Evidence;
- incluir pruebas focales, integración y runtime real cuando dependa de tool externa.

## 5. Rules

Una Rule nueva comienza por una pregunta objetiva del dominio. Solo si una Rule real no puede expresarse con los operadores existentes se justifica ampliar RuleEngine.

## 6. LLM

Prompts, schemas, grounding y perfiles respetan la separación LLM #1 / LLM #2. Parámetros semánticos permanecen versionados en código salvo necesidad operacional demostrada.

## 7. Persistencia

- no codificar rutas físicas en objetos de dominio;
- persistir RAW antes de normalizar;
- conservar Evidence/Finding/Report como artefactos diferenciados;
- persistir `ExecutionFailure` en la rama operacional separada;
- no sobrescribir conocimiento histórico para “corregir” resultados.

## 8. Git y calidad

No realizar staging/commit mientras exista algún test fallando. Cada cierre revisa, según riesgo:

- diff de alcance;
- `git diff --check`;
- suite focal;
- suite global;
- smoke/runtime real cuando corresponda;
- staging explícito;
- revisión cached;
- commit/push;
- working tree limpio.

## 9. Qué no hacer

- funciones globales con lógica de negocio sin justificación arquitectónica;
- acoplar RuleEngine a RAW/tool-specific schemas;
- convertir variabilidad analítica en settings libres por comodidad;
- reabrir arquitectura por estética;
- convertir fallos operacionales en conocimiento;
- permitir a LLM planificar/ejecutar fuera de contrato;
- duplicar Target/Intent en artefactos efímeros si no existe necesidad contractual;
- reintroducir la antigua regla de que toda llamada debe pasar físicamente por Core.

## Base documental

Constitución Arquitectónica v2.0; ADR v3.2; Ciclo de Cierre v1.16; Core/Plugin/Rule/LLM contracts consolidados; cierre OLLAMA-D2 R2.
