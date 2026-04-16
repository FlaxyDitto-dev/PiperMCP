import os
import subprocess
import requests
import traceback
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("PiperTTS")

VOICE_REGISTRY = {
    "en_US-lessac-medium": {
        "name": "Lessac",
        "tags": "American, US, Female, clear, expressive",
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    },
    "en_US-amy-medium": {
        "name": "Amy",
        "tags": "American, US, Female, conversational, smooth",
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
    },
    "en_US-ryan-medium": {
        "name": "Ryan",
        "tags": "American, US, Male, deep, audiobook, clear",
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json"
    },
    "en_GB-alba-medium": {
        "name": "Alba",
        "tags": "British, Scottish, UK, Female, distinct, professional",
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alba/medium/en_GB-alba-medium.onnx.json"
    },
    "en_GB-alan-medium": {
        "name": "Alan",
        "tags": "British, English, UK, Male, mature, calm",
        "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx",
        "json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
    }
}

CACHE_DIR = Path(__file__).parent / "PiperMCP-voices"

def download_file(url: str, dest_path: Path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    with requests.get(url, stream=True, headers=headers, allow_redirects=True) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
    if str(dest_path).endswith(".onnx") and dest_path.stat().st_size < 15000000:
        dest_path.unlink()
        raise RuntimeError("Downloaded ONNX model was corrupted.")

def resolve_voice_id(query: str) -> str:
    query_lower = query.lower().strip()
    if query in VOICE_REGISTRY: return query
    for voice_id, meta in VOICE_REGISTRY.items():
        if query_lower == meta["name"].lower(): return voice_id

    query_words = set(query_lower.split())
    filler_words = {"voice", "use", "a", "an", "the", "with", "sound", "like", "accent"}
    meaningful_words = query_words - filler_words
    
    best_match = None
    highest_score = 0
    for voice_id, meta in VOICE_REGISTRY.items():
        search_profile = f"{voice_id} {meta['name']} {meta['tags']}".lower()
        score = sum(1 for word in meaningful_words if word in search_profile)
        if score > highest_score:
            highest_score = score
            best_match = voice_id

    if best_match and highest_score > 0: return best_match
    raise ValueError(f"Could not find a voice matching '{query}'.")

def ensure_voice_downloaded(voice_id: str) -> str:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    onnx_path = CACHE_DIR / f"{voice_id}.onnx"
    json_path = CACHE_DIR / f"{voice_id}.onnx.json"
    
    if not onnx_path.exists() or onnx_path.stat().st_size < 15000000:
        download_file(VOICE_REGISTRY[voice_id]["onnx"], onnx_path)
    
    if not json_path.exists() or json_path.stat().st_size < 100:
        download_file(VOICE_REGISTRY[voice_id]["json"], json_path)
        
    return str(onnx_path)

@mcp.tool()
def generate_speech(text: str, voice_query: str = "lessac", output_filename: str = "output.wav") -> str:
    try:
        if not text or text.strip() == "":
            raise ValueError("The text provided to synthesize was empty.")

        resolved_voice_id = resolve_voice_id(voice_query)
        onnx_path = ensure_voice_downloaded(resolved_voice_id)
        
        # Safe Output Path
        output_path = Path(output_filename)
        if not output_path.is_absolute():
            output_path = Path.home() / "Downloads" / output_filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # --- THE FIX: USE SUBPROCESS PIPER CLI ---
        # This accurately mimics: echo "text" | piper --model model.onnx --output_file output.wav
        print(f"Invoking Piper CLI for: {output_path}")
        
        command = [
            "piper", # Assuming 'piper' is in your system PATH since it worked in your terminal
            "--model", str(onnx_path),
            "--output_file", str(output_path)
        ]
        
        # Run the command and pass the text through stdin
        process = subprocess.run(
            command, 
            input=text.encode('utf-8'), # The 'echo' equivalent
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Check if the Piper CLI failed
        if process.returncode != 0:
            error_msg = process.stderr.decode('utf-8', errors='ignore')
            raise RuntimeError(f"Piper CLI failed with error:\n{error_msg}")
            
        if not output_path.exists() or output_path.stat().st_size < 100:
            raise RuntimeError("Piper CLI finished, but the audio file is empty.")
            
        return f"Success! Audio saved to: {output_path} (Voice: {resolved_voice_id})"
    
    except Exception as e:
        error_details = traceback.format_exc()
        return f"ERROR generating speech: {str(e)}\n\nTraceback:\n{error_details}"

@mcp.tool()
def list_available_voices() -> str:
    lines = ["Available voices for dynamic download:"]
    for v_id, meta in VOICE_REGISTRY.items():
        lines.append(f"- ID: {v_id} | Name: {meta['name']} | Profile: {meta['tags']}")
    return "\n".join(lines)

if __name__ == "__main__":
    mcp.run()
