import os
import requests
import psycopg2
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


# === CONFIG ===
load_dotenv()
GITHUB_MCP_ENDPOINT = os.getenv("GITHUB_MCP_ENDPOINT", "https://api.github-mcp-server.local")
GITHUB_REPO = os.getenv("GITHUB_REPO", "usuario/repositorio")
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "dbname=wp user=wpuser password=secret host=localhost")

# === MODELO ===
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# === FUNCIONES (Tools) ===
def fetch_wp_version(_: str) -> str:
    """Obtiene la última versión estable de WordPress desde la API oficial."""
    url = "https://api.wordpress.org/core/version-check/1.7/"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    version = data["offers"][0]["current"]
    return f"La versión actual de WordPress es {version}"

def get_last_db_version(_: str) -> str:
    """Consulta la última versión registrada en la base de datos Postgres."""
    conn = psycopg2.connect(POSTGRES_DSN)
    cur = conn.cursor()
    cur.execute("SELECT version FROM wp_versions ORDER BY created_at DESC LIMIT 1;")
    row = cur.fetchone()
    conn.close()
    if row:
        return f"La última versión registrada en BD es {row[0]}"
    return "No hay versiones registradas en BD"

def mcp_git_update_env(input_text: str) -> str:
    """Actualiza la variable WP_VERSION en el archivo .env del repositorio vía GitHub MCP."""
    # Se espera que el input contenga algo como: "6.7.2"
    version = input_text.strip().split()[-1]
    payload = {
        "tool": "update_env",
        "params": {
            "repo": GITHUB_REPO,
            "file_path": ".env",
            "variable": "WP_VERSION",
            "value": version
        }
    }
    r = requests.post(f"{GITHUB_MCP_ENDPOINT}/tool", json=payload,
                      headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"})
    r.raise_for_status()
    return f"Archivo .env actualizado con WP_VERSION={version}"

def mcp_git_commit_push(input_text: str) -> str:
    """Hace commit y push de los cambios en el repo mediante GitHub MCP."""
    message = input_text or "Update WP version"
    payload = {
        "tool": "commit_and_push",
        "params": {"repo": GITHUB_REPO, "message": message}
    }
    r = requests.post(f"{GITHUB_MCP_ENDPOINT}/tool", json=payload,
                      headers={"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"})
    r.raise_for_status()
    return "Commit y push ejecutados correctamente."

def register_new_version_db(input_text: str) -> str:
    """Registra la nueva versión en la base de datos."""
    version = input_text.strip().split()[-1]
    conn = psycopg2.connect(POSTGRES_DSN)
    cur = conn.cursor()
    cur.execute("INSERT INTO wp_versions (version, created_at) VALUES (%s, NOW());", (version,))
    conn.commit()
    conn.close()
    return f"Versión {version} registrada en BD."

# === TOOLS ===
tools = [
    Tool(
        name="fetch_wp_version",
        func=fetch_wp_version,
        description="Obtiene la versión actual de WordPress desde su API oficial."
    ),
    Tool(
        name="get_last_db_version",
        func=get_last_db_version,
        description="Consulta la última versión guardada en la base de datos."
    ),
    Tool(
        name="mcp_git_update_env",
        func=mcp_git_update_env,
        description="Actualiza el valor de WP_VERSION en el archivo .env mediante MCP."
    ),
    Tool(
        name="mcp_git_commit_push",
        func=mcp_git_commit_push,
        description="Hace commit y push de los cambios del repositorio mediante MCP."
    ),
    Tool(
        name="register_new_version_db",
        func=register_new_version_db,
        description="Registra la nueva versión detectada en la base de datos."
    ),
]
# === PROMPT BASE ===
system_prompt = """
Eres un agente ReAct responsable de mantener actualizado el archivo .env del repositorio {repo}
según la última versión de WordPress. Usa las herramientas disponibles para:
1. Consultar la versión actual de WordPress (fetch_wp_version).
2. Consultar la versión guardada en BD (get_last_db_version).
3. Si hay una versión más reciente, actualiza el .env (mcp_git_update_env),
   luego haz commit y push (mcp_git_commit_push),
   y finalmente registra la nueva versión en BD (register_new_version_db).
4. Muestra tus pensamientos, acciones y observaciones de forma transparente.
"""

# === AGENTE ===
agent = initialize_agent(
    tools,
    llm,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)

# === MAIN ===
def main():
    query = f"Revisa si hay una nueva versión de WordPress y actúa según el flujo descrito. Repo: {GITHUB_REPO}"
    print("🤖 Ejecutando agente...\n")
    response = agent.run(query)
    print("\n=== RESULTADO FINAL ===")
    print(response)

if __name__ == "__main__":
    main()
