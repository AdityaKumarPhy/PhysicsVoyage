#!/usr/bin/env python3
"""
cloudinary_sync.py
==================
Dedicated sync script for the `assets/Media/` drop zone.

DROP any file (image, PDF, video, audio, etc.) into `assets/Media/`
and run this script (or just `quarto render`). It will:

  1. Scan `assets/Media/` for new/changed files.
  2. Compute a SHA-256 hash for each file.
  3. Check the local cache (`assets/Media/.cloudinary_cache.json`) for
     a matching hash — if found, the file is SKIPPED (no re-upload).
  4. Upload new / changed files to Cloudinary.
  5. Save the Cloudinary URL + hash to the cache file.
  6. Move the original local file to `.local_image_backup/assets/Media/`
     (gitignored) so your GitHub repo stays lightweight.

The cache file IS committed to git, so Cloudinary URLs are always
available to your blog posts on any machine.

Usage (standalone):
    python3 assets/scripts/cloudinary_sync.py

Usage (automatic):
    Runs automatically as a Quarto pre-render hook (see _quarto.yml).
"""

import os
import re
import sys
import json
import time
import uuid
import shutil
import hashlib
import mimetypes
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths (resolved relative to this script's location)
# ---------------------------------------------------------------------------
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT   = os.path.abspath(os.path.join(SCRIPT_DIR, "../.."))
MEDIA_DIR   = os.path.join(REPO_ROOT, "assets", "Media")
CACHE_FILE  = os.path.join(MEDIA_DIR, ".cloudinary_cache.json")
BACKUP_ROOT = os.path.join(REPO_ROOT, ".local_image_backup", "assets", "Media")

# Supported media extensions (everything Cloudinary can handle)
MEDIA_EXTENSIONS = {
    # Images & Graphics
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
    ".bmp", ".tiff", ".ico", ".avif", ".heic", ".raw",
    # Documents
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    # Video
    ".mp4", ".webm", ".mov", ".avi", ".mkv", ".flv",
    # Audio
    ".mp3", ".wav", ".ogg", ".aac", ".flac",
    # Data / Other common assets
    ".zip", ".json", ".csv",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_env() -> dict:
    """Load variables from .env file in repo root."""
    env_vars = dict(os.environ)
    env_path = os.path.join(REPO_ROOT, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_vars[key.strip()] = val.strip().strip("\"'")
    return env_vars


def sha256_of_file(path: str) -> str:
    """Return the SHA-256 hex digest of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cache() -> dict:
    """Load the upload cache from CACHE_FILE (returns {} if missing/corrupt)."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_cache(cache: dict) -> None:
    """Persist the upload cache to CACHE_FILE."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
        f.write("\n")


def generate_signature(params: dict, api_secret: str) -> str:
    """Generate a Cloudinary API v1 signature (SHA-1 of sorted params)."""
    sorted_keys = sorted(params.keys())
    param_str = "&".join(
        f"{k}={params[k]}"
        for k in sorted_keys
        if params[k] is not None and params[k] != ""
    )
    sign_str = param_str + api_secret
    return hashlib.sha1(sign_str.encode("utf-8")).hexdigest()


def upload_to_cloudinary(
    file_path: str,
    cloud_name: str,
    api_key: str,
    api_secret: str,
    folder: str,
    public_id: str,
) -> dict:
    """
    Upload a file to Cloudinary using multipart/form-data (pure urllib).
    Returns the parsed JSON response dict.
    """
    timestamp = str(int(time.time()))

    # Only sign params that Cloudinary expects in the signature
    # (resource_type, overwrite, api_key are NOT part of the signature)
    sign_params = {"folder": folder, "public_id": public_id, "timestamp": timestamp}
    signature = generate_signature(sign_params, api_secret)

    boundary = f"----CloudinaryBoundary{uuid.uuid4().hex}"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    # Build multipart body
    fields = {
        "api_key":       api_key,
        "timestamp":     timestamp,
        "signature":     signature,
        "folder":        folder,
        "public_id":     public_id,
        "resource_type": "auto",
        # Note: overwrite not needed — unique public_ids prevent collisions
    }

    body_parts: list[bytes] = []
    for name, value in fields.items():
        body_parts.append(f"--{boundary}".encode())
        body_parts.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        body_parts.append(b"")
        body_parts.append(str(value).encode("utf-8"))

    # File part
    body_parts.append(f"--{boundary}".encode())
    body_parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode()
    )
    body_parts.append(f"Content-Type: {mime_type}".encode())
    body_parts.append(b"")
    body_parts.append(file_bytes)
    body_parts.append(f"--{boundary}--".encode())
    body_parts.append(b"")

    body = b"\r\n".join(body_parts)

    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/auto/upload"
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))

    with urllib.request.urlopen(req, timeout=120) as res:
        return json.loads(res.read().decode("utf-8"))


def make_public_id(filename: str) -> str:
    """Derive a clean Cloudinary public_id from a filename (no extension)."""
    base = os.path.splitext(filename)[0]
    # Replace anything that isn't alphanumeric, dash, underscore, or slash
    cleaned = re.sub(r"[^\w\-/]", "_", base)
    # Collapse multiple underscores / dashes
    cleaned = re.sub(r"[_\-]{2,}", "_", cleaned)
    return cleaned.strip("_-").lower()


def move_to_backup(file_path: str) -> None:
    """Move an uploaded file from MEDIA_DIR to BACKUP_ROOT."""
    rel = os.path.relpath(file_path, MEDIA_DIR)
    dst = os.path.join(BACKUP_ROOT, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(file_path, dst)
    print(f"  └─📦 Backed up to: {os.path.relpath(dst, REPO_ROOT)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    env = load_env()
    cloud_name = env.get("CLOUDINARY_CLOUD_NAME", "").strip()
    api_key    = env.get("CLOUDINARY_API_KEY", "").strip()
    api_secret = env.get("CLOUDINARY_API_SECRET", "").strip()
    folder     = env.get("CLOUDINARY_FOLDER", "physics_voyage").strip()

    if not cloud_name or not api_key or not api_secret:
        print("⚠️  Cloudinary credentials missing from .env — skipping Media sync.")
        print("   Add: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
        return

    if not os.path.isdir(MEDIA_DIR):
        print(f"ℹ️  Media folder not found ({MEDIA_DIR}) — nothing to sync.")
        return

    print("=" * 55)
    print("   📡  Cloudinary Media Sync — assets/Media/")
    print("=" * 55)
    print(f"   Cloud: {cloud_name}  |  Folder: {folder}")
    print()

    cache = load_cache()

    stats = dict(scanned=0, uploaded=0, skipped=0, failed=0)

    # Walk the entire MEDIA_DIR tree
    for dirpath, _, filenames in os.walk(MEDIA_DIR):
        for filename in sorted(filenames):
            # Skip hidden files (like the cache itself)
            if filename.startswith("."):
                continue

            ext = os.path.splitext(filename)[1].lower()
            if ext not in MEDIA_EXTENSIONS:
                continue

            file_path = os.path.join(dirpath, filename)
            stats["scanned"] += 1

            # Compute hash for deduplication
            file_hash = sha256_of_file(file_path)

            # ----------------------------------------------------------------
            # DEDUPLICATION CHECK
            # Check both by filename AND by hash so renamed-but-same files are
            # also caught.
            # ----------------------------------------------------------------
            already_uploaded = False
            for cached_name, cached_data in cache.items():
                # Skip metadata/comment keys (strings, not dicts)
                if not isinstance(cached_data, dict):
                    continue
                if cached_data.get("sha256") == file_hash:
                    already_uploaded = True
                    print(f"⏭️  SKIP  {filename}")
                    print(f"   └─ Already on Cloudinary: {cached_data['cloudinary_url']}")
                    stats["skipped"] += 1
                    break

            if already_uploaded:
                # Move to backup anyway so it doesn't sit in the media dir
                move_to_backup(file_path)
                continue

            # ----------------------------------------------------------------
            # UPLOAD
            # ----------------------------------------------------------------
            rel_to_media = os.path.relpath(file_path, MEDIA_DIR)
            # Build public_id preserving subfolder structure within Media/
            rel_no_ext = os.path.splitext(rel_to_media)[0]
            public_id  = make_public_id(rel_no_ext)

            print(f"⬆️  UPLOAD  {rel_to_media}")

            try:
                result = upload_to_cloudinary(
                    file_path=file_path,
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    folder=folder,
                    public_id=public_id,
                )

                url = result.get("secure_url", "")
                if not url:
                    raise ValueError(f"No secure_url in response: {result}")

                print(f"   └─✅ {url}")

                # Persist to cache
                cache[filename] = {
                    "sha256":         file_hash,
                    "cloudinary_url": url,
                    "public_id":      result.get("public_id", ""),
                    "resource_type":  result.get("resource_type", ""),
                    "format":         result.get("format", ext.lstrip(".")),
                    "uploaded_at":    datetime.now(timezone.utc).isoformat(),
                }
                save_cache(cache)
                stats["uploaded"] += 1

                # Move local file to backup
                move_to_backup(file_path)

            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                print(f"   └─❌ HTTP {e.code}: {body}")
                stats["failed"] += 1
            except Exception as exc:
                print(f"   └─❌ Error: {exc}")
                stats["failed"] += 1

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print()
    print("─" * 55)
    print(f"  Scanned : {stats['scanned']}")
    print(f"  Uploaded: {stats['uploaded']}")
    print(f"  Skipped : {stats['skipped']}  (already on Cloudinary)")
    if stats["failed"]:
        print(f"  Failed  : {stats['failed']}  ← check credentials / file")
    print("─" * 55)

    if stats["uploaded"] == 0 and stats["scanned"] == 0:
        print("ℹ️  No media files found in assets/Media/ — nothing to do.")

    if stats["uploaded"] > 0:
        print()
        print(f"📋 Cloudinary URLs saved to:")
        print(f"   assets/Media/.cloudinary_cache.json")
        print()
        print("   Copy the URL from the cache and paste it into your blog post.")


if __name__ == "__main__":
    main()
