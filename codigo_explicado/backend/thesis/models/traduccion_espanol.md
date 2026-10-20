# Explicación de Código: `backend/thesis/models/__init__.py`

## 1. Propósito y ¿Qué hace?
Centraliza la exportación de todos los modelos del sistema, expone alias canónicos en español (`Usuario`, `Proyecto`, `PerfilInvestigacion`, `Capitulo`, `FilaConsistencia`, etc.) y aplica el diccionario de mapeo físico `COLUMNAS_FISICAS`, traduciendo cada atributo del ORM a nombres de columnas SQL en español en PostgreSQL.

## 2. Justificación Técnica y ¿Por qué lo hace?
* **Compatibilidad Mixta:** Para mantener compatibilidad con convenciones internas de Django y permitir futuras sincronizaciones de migraciones con el proyecto completo, las clases del ORM pueden conservar internamente atributos estándar de Python mientras que la base de datos física habla 100% en español.
* **Centralización de Metadatos:** En lugar de ensuciar las definiciones de modelos con docenas de parámetros `db_column` manuales, este módulo aplica la traducción física en el momento de inicialización del paquete de modelos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Importa todas las clases de modelos desde `accounts.py`, `projects.py`, `research.py` y `chapters.py`.
2. Define el diccionario `COLUMNAS_FISICAS: dict[type[Model], dict[str, str]]`, que especifica la traducción física exacta (ej. `PerfilInvestigacion: {"approach": "enfoque", "lock_version": "version_bloqueo", "ods_code": "codigo_ods"}`).
3. Itera sobre cada modelo y campo, inyectando `campo.column = columna_espanola` dinámicamente antes de que Django compile el esquema de base de datos.
4. Exporta los modelos con sus nombres en español mediante `__all__`.

## 4. Componentes y Funciones Clave
* `COLUMNAS_FISICAS`: Diccionario maestro de mapeo campo ORM -> columna física PostgreSQL.
* `__all__`: Lista de exportación de modelos con alias en español.

## 5. Relaciones con Otras Capas y Tablas
* **Base de datos:** Define los nombres físicos reales auditados en PostgreSQL por [`scripts/verify_project.py`](../../scripts/verify_project.py).
* **Migraciones:** Garantiza que [`0001_inicial.py`](../../backend/thesis/migrations/0001_inicial.py) genere tablas con columnas en español.
