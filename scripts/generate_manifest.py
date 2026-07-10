"""
Regenerate ARTIFACT_MANIFEST_V12.csv
Computes SHA256 checksums and file sizes for all non-ignored files in the workspace.
"""

import os
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = {
    ".git",
    ".gemini",
    "__pycache__",
    ".idea",
    ".vscode",
    ".antigravitycli",
    ".venv",
    "venv",
    "env",
    "data",
    "replay",
    "cache" # Exclude any cache folders (like data-backtest/cache)
}

EXCLUDED_FILES = {
    "ARTIFACT_MANIFEST_V12.csv",
    ".env",
    "dashboard.py",
    "test_log.py",
    "hyperliquid_client.py",
    "Dockerfile",
    "ai_decisions.csv",
    "portfolio_state.csv",
    "trade_history.csv",
    "ai_messages.csv",
    "portfolio_state.json",
    "backtest_results.json",
    "generate_manifest.py" # Exclude itself
}

def get_sha256(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def should_exclude(filepath: Path) -> bool:
    # Get relative parts
    rel_path = filepath.relative_to(PROJECT_ROOT)
    parts = rel_path.parts
    
    # 1. Exclude any file that starts with run- in data-backtest (from gitignore)
    if len(parts) >= 2 and parts[0] in ("data-backtest", "data-backtest2") and parts[1].startswith("run-"):
        return True
        
    # 2. Exclude specific directory names
    for p in parts[:-1]:
        if p in EXCLUDED_DIRS:
            return True
            
    # 3. Exclude specific file names
    if parts[-1] in EXCLUDED_FILES:
        return True
        
    # 4. Check extensions
    ext = filepath.suffix.lower()
    if ext in (".pyc", ".pyo", ".pyd", ".log"):
        return True
        
    return False

def generate():
    manifest_entries = []
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Prune excluded directories in place
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        for file in files:
            filepath = Path(root) / file
            if should_exclude(filepath):
                continue
                
            rel_path = filepath.relative_to(PROJECT_ROOT).as_posix()
            size_bytes = filepath.stat().st_size
            sha256_hash = get_sha256(filepath)
            
            manifest_entries.append({
                "relative_path": rel_path,
                "size_bytes": size_bytes,
                "sha256": sha256_hash
            })
            
    # Sort alphabetically by relative path
    manifest_entries.sort(key=lambda x: x["relative_path"])
    
    manifest_file = PROJECT_ROOT / "ARTIFACT_MANIFEST_V12.csv"
    with open(manifest_file, "w", encoding="utf-8", newline="") as f:
        f.write("relative_path,size_bytes,sha256\n")
        for entry in manifest_entries:
            f.write(f"{entry['relative_path']},{entry['size_bytes']},{entry['sha256']}\n")
            
    print(f"Successfully generated manifest at {manifest_file} with {len(manifest_entries)} files.")

if __name__ == "__main__":
    generate()
