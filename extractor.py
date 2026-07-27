import subprocess
import os
import json
import time
from datetime import datetime

def extraer_metadatos(url):
    try:
        # Comando LIGERO: solo metadatos, no toca el CDN
        cmd = ['yt-dlp', '--no-warnings', '--print', '%(title)s\t%(url)s', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split('\t', 1)
            if len(parts) == 2:
                return {'titulo': parts[0].strip(), 'url': parts[1].strip()}
        
        error_msg = result.stderr.strip()[:100] if result.stderr else "Sin detalle"
        print(f"   ⚠️ Falló: {error_msg}")
        return None
        
    except subprocess.TimeoutExpired:
        print(f"   ⏱️ Timeout (60s)")
        return None
    except Exception as e:
        print(f"   ⚠️ Excepción: {e}")
        return None

print("="*60)
print("🎬 EXTRACTOR - METADATOS POR CATEGORÍA")
print("="*60)

if not os.path.exists('urls.txt'):
    print("❌ No existe urls.txt")
    exit(1)

with open('urls.txt', 'r', encoding='utf-8') as f:
    lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

print(f"📥 {len(lines)} líneas encontradas")

categorias = {}
for line in lines:
    if '|' in line:
        parts = line.split('|', 1)
        categoria = parts[0].strip()
        url = parts[1].strip()
    else:
        categoria = 'general'
        url = line.strip()
    
    if categoria not in categorias:
        categorias[categoria] = []
    
    print(f"🔄 [{categoria}] {url[:50]}...")
    metadatos = extraer_metadatos(url)
    
    if metadatos:
        categorias[categoria].append({
            'titulo': metadatos['titulo'],
            'url': metadatos['url'],
            'fecha_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"   ✅ {metadatos['titulo'][:40]}...")
    else:
        print(f"   ❌ Falló")
    
    time.sleep(0.5)

os.makedirs('peliculas', exist_ok=True)

for categoria, datos in categorias.items():
    nombre_archivo = "".join(x for x in categoria if x.isalnum() or x in (' ', '_', '-')).strip()
    if not nombre_archivo:
        nombre_archivo = 'general'
    json_path = os.path.join('peliculas', f'{nombre_archivo}.json')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {json_path} ({len(datos)} videos)")

print(f"\n🎉 {len(categorias)} categorías procesadas")
