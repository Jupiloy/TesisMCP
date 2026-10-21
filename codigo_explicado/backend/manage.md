# Explicación de Código: `backend/manage.py`

## 1. Propósito y ¿Qué hace?
Es el script ejecutable de administración por línea de comandos para el backend Django. Configura el entorno de ejecución, define la variable de entorno `DJANGO_SETTINGS_MODULE` apuntando a `config.settings` y delega la ejecución de comandos (migraciones, pruebas, chequeos de salud y comandos personalizados) en `execute_from_command_line` de Django.

## 2. Justificación Técnica y ¿Por qué lo hace?
En proyectos Django desacoplados de gran escala, el punto de entrada administrativo no debe contener lógica de negocio ni código espurio. Permite a desarrolladores, contenedores Docker y scripts de verificación automatizada invocar utilidades del sistema (`check`, `migrate`, `makemigrations`, `emitir_token_mcp`) manteniendo consistencia en la carga de módulos.

## 3. Mecanismo Interno y ¿Cómo lo hace?
1. Define la función principal `main()`.
2. Establece `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')`.
3. Importa `from django.core.management import execute_from_command_line`. Si falla la importación, lanza un `ImportError` indicando si Django está instalado o si el entorno virtual está activo.
4. Invoca `execute_from_command_line(sys.argv)`.
5. Se invoca como script principal mediante `if __name__ == '__main__': main()`.

## 4. Componentes y Funciones Clave
* `main()`: Función principal sin argumentos que encapsula la inicialización y el despacho del CLI.
* `execute_from_command_line(sys.argv)`: Despachador nativo del núcleo de Django que analiza banderas y subcomandos.

## 5. Relaciones con Otras Capas y Tablas
* **Configuración:** Carga directamente [`backend/config/settings.py`](../../backend/config/settings.py).
* **Comandos personalizados:** Descubre automáticamente comandos en `backend/thesis/management/commands/` como [`emitir_token_mcp.py`](../../backend/thesis/management/commands/emitir_token_mcp.py).
* **Automatización:** Es invocado por la puerta determinista [`scripts/verify_project.py`](../../scripts/verify_project.py) para auditar `check` y `makemigrations`.
