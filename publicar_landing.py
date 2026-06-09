import os
import subprocess
import requests
import json

# ===== CONFIGURACIÓN =====
GITHUB_TOKEN = "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"
GITHUB_USER = "onlyfansofseduction-source"
REPO_NAME = "nexus-landing"
LANDING_DIR = r"C:\karvis_landings"
GITHUB_PAGES_URL = f"https://{GITHUB_USER}.github.io/{REPO_NAME}/"
OLLAMA_URL = "http://localhost:11434/api/generate"

def generar_html(descripcion):
    print("🤖 Generando landing con IA...")
    prompt = f"""Crea una landing page HTML completa y profesional en español para: {descripcion}
    
    Requisitos:
    - Todo en un solo archivo HTML
    - CSS incluido en el mismo archivo
    - Diseño moderno y atractivo
    - Sección hero, beneficios, y botón de contacto
    - Responsive para móvil
    - Solo devuelve el código HTML, nada más
    """
    
    response = requests.post(OLLAMA_URL, json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })
    
    data = response.json()
    html = data["response"]
    
    # Limpiar si viene con markdown
    if "```html" in html:
        html = html.split("```html")[1].split("```")[0]
    elif "```" in html:
        html = html.split("```")[1].split("```")[0]
    
    return html.strip()

def publicar_github(html):
    print("📤 Publicando en GitHub Pages...")
    
    # Guardar HTML
    index_path = os.path.join(LANDING_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    # Git push
    os.chdir(LANDING_DIR)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "landing actualizada"], check=True)
    subprocess.run(["git", "push"], check=True)
    
    print(f"✅ GitHub Pages: {GITHUB_PAGES_URL}")
    return GITHUB_PAGES_URL

def publicar_ngrok(html):
    print("🚀 Publicando con ngrok...")
    
    # Guardar HTML en carpeta temporal
    temp_path = r"C:\karvis_landings\temp_landing"
    os.makedirs(temp_path, exist_ok=True)
    with open(os.path.join(temp_path, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    
    # Iniciar servidor HTTP simple
    server = subprocess.Popen(
        ["python", "-m", "http.server", "8080"],
        cwd=temp_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Iniciar ngrok
    ngrok_proc = subprocess.Popen(
        ["ngrok", "http", "8080"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    import time
    time.sleep(3)
    
    # Obtener URL de ngrok
    try:
        r = requests.get("http://localhost:4040/api/tunnels")
        tunnels = r.json()["tunnels"]
        url = tunnels[0]["public_url"]
        print(f"✅ ngrok: {url}")
        return url, server, ngrok_proc
    except:
        print("⚠️ No se pudo obtener URL de ngrok")
        return None, server, ngrok_proc

def crear_landing(descripcion):
    print(f"\n🎯 Creando landing para: {descripcion}\n")
    
    html = generar_html(descripcion)
    
    # Intentar GitHub Pages primero
    try:
        url = publicar_github(html)
        print(f"\n🌐 Landing publicada: {url}")
        print("⏳ GitHub Pages tarda 1-2 minutos en actualizar")
        return url
    except Exception as e:
        print(f"⚠️ GitHub falló: {e}")
        print("🔄 Usando ngrok como respaldo...")
        url, _, _ = publicar_ngrok(html)
        if url:
            print(f"\n🌐 Landing publicada: {url}")
            return url
        else:
            print("❌ Ambos métodos fallaron")
            return None

if __name__ == "__main__":
    descripcion = input("¿Para qué es la landing? Describí el negocio/producto: ")
    crear_landing(descripcion)