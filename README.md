# wp_update_AI

Automatización inteligente para mantener un entorno de WordPress actualizado mediante un agente ReAct que integra la API de versiones de WordPress, una base de datos PostgreSQL y un mecanismo de actualización de repositorio vía MCP de GitHub.

## 🧩 Descripción

Este proyecto implementa un agente autónomo que:

- Consulta la versión actual de WordPress mediante la API oficial.  
- Comprueba la última versión registrada en una base de datos PostgreSQL.  
- Si detecta que la versión oficial es más reciente, actualiza el archivo `.env` del repositorio, hace un commit + push y registra la nueva versión en la base de datos.  
- Utiliza el patrón **ReAct** (Reasoning + Action) para decidir dinámicamente qué herramienta ejecutar.  
- Se integra con un MCP (Model Context Protocol) de GitHub para operaciones seguras sobre el repositorio.

## ✅ Funcionalidades clave

- Detección automática de nuevas versiones de WordPress.  
- Registro histórico de versiones en PostgreSQL.  
- Automatización de actualizaciones en el repositorio: modificar `.env` → commit → push.  
- Arquitectura modular: el agente decide qué herramientas usar.  
- Trazabilidad de acciones: cada “pensamiento”, “acción” y “observación” puede quedar registrada.

## 🛠️ Requisitos

- Python 3.10 o superior  
- API Key de OpenAI (o proveedor compatible)  
- PostgreSQL accesible con una tabla definida para registrar versiones (ejemplo provisto)  
- MCP de GitHub configurado para permitir operaciones: actualización de archivos, commit y push  
- Dependencias instaladas desde `requirements.txt`

## 📦 Instalación rápida

1. Clona el repositorio:

   ```bash
   git clone https://github.com/JeffersonRiobueno/wp_update_AI.git
   cd wp_update_AI
   ```

2. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:

   ```env
   OPENAI_API_KEY=tu_openai_key
   POSTGRES_DSN=dbname=wp user=usuario password=tu_pass host=host_servidor port=5432
   GITHUB_MCP_ENDPOINT=https://tu_mcp_endpoint
   GITHUB_TOKEN=tu_token_github
   GITHUB_REPO=usuario/repositorio
   ```

5. Asegúrate de tener la tabla SQL creada en PostgreSQL.

## ▶️ Uso

Para ejecutar el agente, simplemente:

```bash
python main.py
```

El agente hará:

- Llamada a la API de WordPress para obtener la versión actual.  
- Consulta de la última versión en PostgreSQL.  
- Si encuentra una versión más reciente, realizará la actualización en el repositorio vía MCP y registrará el nuevo valor.  
- Si no hay nueva versión, se detendrá sin realizar cambios.

## 🔍 Arquitectura del flujo

1. **fetch_wp_version** — Herramienta que obtiene la versión oficial de WordPress.  
2. **get_last_db_version** — Herramienta que lee la versión más reciente registrada en PostgreSQL.  
3. El LLM razona sobre la comparación.  
4. Si procede, **mcp_git_update_env** → modifica `.env`.  
5. Luego, **mcp_git_commit_push** → commit y push al repositorio.  
6. Finalmente, **register_new_version_db** → registra la nueva versión.  
7. El agente registra cada paso para auditoría.

## 📌 Consideraciones

- Asegúrate de que las credenciales y tokens estén seguros: no los incluyas en el código.  
- Verifica que el MCP tenga los permisos necesarios para el repositorio (modificación de archivos, commit, push).  
- La comparación de versiones es simple; si usas versiones con semántica compleja, podrías tener que adaptarla.  
- Considera manejar errores y excepciones: fallos en la conexión, token inválido, API inaccesible, etc.

## 💡 Futuras mejoras

- Añadir notificaciones cuando ocurra una actualización.  
- Integración con monitoreo o alertas si el proceso falla.  
- Soporte para múltiples repositorios o servicios de WordPress.

## 📄 Licencia

Puedes añadir aquí la licencia que prefieras (por ejemplo MIT).
