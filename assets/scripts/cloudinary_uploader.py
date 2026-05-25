#!/usr/bin/env python3
import os
import re
import sys
import time
import uuid
import hashlib
import shutil
import mimetypes
import json
import urllib.request
import urllib.error

# Load environment variables from .env
def load_env(repo_root):
    env_vars = {}
    env_path = os.path.join(repo_root, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    env_vars[key.strip()] = val.strip().strip('"\'')
    return env_vars

# Check if a path looks like a remote URL or a template variable
def is_external_or_template(path):
    if path.startswith(('http://', 'https://', '//')):
        return True
    if '{{<' in path or '}}' in path or '<%' in path or '%>' in path:
        return True
    # If no dot in filename, it's probably not a real file path
    basename = os.path.basename(path)
    if '.' not in basename:
        return True
    # Whitelist of media and document extensions
    ext = os.path.splitext(basename)[1].lower()
    media_extensions = [
        # Images & Graphs
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.tiff', '.ico',
        # Documents
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        # Video/Audio
        '.mp4', '.webm', '.mov', '.avi', '.mkv', '.mp3', '.wav', '.ogg'
    ]
    if ext not in media_extensions:
        return True
    return False

# Resolve local image paths
def resolve_local_path(file_dir, repo_root, path):
    # Try resolving relative to the file directory
    p1 = os.path.abspath(os.path.join(file_dir, path))
    if os.path.isfile(p1) and p1.startswith(repo_root):
        return p1
    # Try resolving relative to the repo root
    p2 = os.path.abspath(os.path.join(repo_root, path))
    if os.path.isfile(p2) and p2.startswith(repo_root):
        return p2
    return None

# Generate Cloudinary signature
def generate_signature(params, api_secret):
    # Sort keys alphabetically
    sorted_keys = sorted(params.keys())
    # Join key=value pairs with &
    param_str = "&".join(f"{k}={params[k]}" for k in sorted_keys if params[k] is not None and params[k] != "")
    # Append the API secret directly to the end of the string
    sign_str = param_str + api_secret
    # Compute SHA-1
    return hashlib.sha1(sign_str.encode('utf-8')).hexdigest()

# Direct HTTP POST upload to Cloudinary using pure urllib
def upload_to_cloudinary(file_path, cloud_name, api_key, api_secret, folder=None, public_id=None):
    timestamp = str(int(time.time()))
    
    # 1. Gather parameters to sign
    params = {
        "timestamp": timestamp
    }
    if folder:
        params["folder"] = folder
    if public_id:
        params["public_id"] = public_id
        
    # 2. Generate signature
    signature = generate_signature(params, api_secret)
    
    # 3. Create multipart/form-data boundary
    boundary = f"----CloudinaryBoundary{uuid.uuid4().hex}"
    
    # Read file content
    with open(file_path, "rb") as f:
        file_content = f.read()
        
    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"
        
    # Build payload parts
    body_parts = []
    
    # Regular parameters
    fields = {
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature,
        "resource_type": "auto"
    }
    if folder:
        fields["folder"] = folder
    if public_id:
        fields["public_id"] = public_id
        
    for name, value in fields.items():
        body_parts.append(f"--{boundary}".encode("utf-8"))
        body_parts.append(f'Content-Disposition: form-data; name="{name}"'.encode("utf-8"))
        body_parts.append(b"")
        body_parts.append(str(value).encode("utf-8"))
        
    # File parameter
    body_parts.append(f"--{boundary}".encode("utf-8"))
    body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode("utf-8"))
    body_parts.append(f"Content-Type: {mime_type}".encode("utf-8"))
    body_parts.append(b"")
    body_parts.append(file_content)
    
    # End boundary
    body_parts.append(f"--{boundary}--".encode("utf-8"))
    body_parts.append(b"")
    
    body = b"\r\n".join(body_parts)
    
    # Send Request
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    req.add_header("Content-Length", str(len(body)))
    
    with urllib.request.urlopen(req) as res:
        res_data = json.loads(res.read().decode("utf-8"))
        return res_data

def main():
    # Resolve project directories
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, '../..'))
    
    env = load_env(repo_root)
    cloud_name = env.get('CLOUDINARY_CLOUD_NAME')
    api_key = env.get('CLOUDINARY_API_KEY')
    api_secret = env.get('CLOUDINARY_API_SECRET')
    folder = env.get('CLOUDINARY_FOLDER', 'physics_voyage')
    
    if not cloud_name or not api_key or not api_secret:
        print("Cloudinary credentials are not configured in your .env file.")
        print("To enable automatic image uploads, add the following variables:")
        print("  CLOUDINARY_CLOUD_NAME")
        print("  CLOUDINARY_API_KEY")
        print("  CLOUDINARY_API_SECRET")
        print("Skipping Cloudinary upload step.\n")
        return
        
    print("--- Starting Cloudinary Auto-Upload Process ---")
    print(f"Cloud Name: {cloud_name}")
    print(f"Target Folder: {folder}")
    
    # Track statistics
    stats = {
        "files_scanned": 0,
        "images_uploaded": 0,
        "upload_failures": 0,
        "files_modified": 0
    }
    
    # Keep track of files uploaded in this execution to avoid duplicating uploads
    uploaded_cache = {}
    
    # Walk directory to find .qmd and .md files
    # Focus on folders: Blog, Courses, Projects and root
    target_dirs = ['Blog', 'Courses', 'Projects']
    files_to_scan = []
    
    # Add target directory files
    for t_dir in target_dirs:
        dir_path = os.path.join(repo_root, t_dir)
        if os.path.isdir(dir_path):
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    if filename.endswith(('.qmd', '.md')):
                        files_to_scan.append(os.path.join(root, filename))
                        
    # Add root level qmd files
    for filename in os.listdir(repo_root):
        if filename.endswith(('.qmd', '.md')) and filename != 'README.md':
            files_to_scan.append(os.path.join(repo_root, filename))
            
    # Process files
    for file_path in files_to_scan:
        stats["files_scanned"] += 1
        file_dir = os.path.dirname(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue
            
        modified = False
        
        # Define the path resolution and upload/backup wrapper
        def process_path(path):
            nonlocal modified
            if is_external_or_template(path):
                return None
                
            # Check cache before checking file existence (in case it was already moved to backup)
            p1 = os.path.abspath(os.path.join(file_dir, path))
            if p1 in uploaded_cache: return uploaded_cache[p1]
            p2 = os.path.abspath(os.path.join(repo_root, path))
            if p2 in uploaded_cache: return uploaded_cache[p2]
                
            full_local_path = resolve_local_path(file_dir, repo_root, path)
            if not full_local_path:
                return None
                
            # If already uploaded in this run
            if full_local_path in uploaded_cache:
                return uploaded_cache[full_local_path]
                
            # Upload to Cloudinary
            try:
                base_name = os.path.splitext(os.path.basename(full_local_path))[0]
                # Clean public_id
                public_id = re.sub(r'[^a-zA-Z0-9_\-]', '-', base_name).lower()
                public_id = re.sub(r'-+', '-', public_id).strip('-')
                
                print(f"Uploading {os.path.relpath(full_local_path, repo_root)}...")
                res_data = upload_to_cloudinary(
                    file_path=full_local_path,
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret,
                    folder=folder,
                    public_id=public_id
                )
                
                url = res_data.get("secure_url")
                if not url:
                    raise Exception("No secure_url returned")
                    
                print(f"  └─► Success: {url}")
                stats["images_uploaded"] += 1
                
                # Move to backups
                backup_root = os.path.join(repo_root, ".local_image_backup")
                rel_path = os.path.relpath(full_local_path, repo_root)
                backup_path = os.path.join(backup_root, rel_path)
                
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.move(full_local_path, backup_path)
                
                uploaded_cache[full_local_path] = url
                modified = True
                return url
                
            except Exception as upload_err:
                print(f"  └─► Failed to upload {os.path.relpath(full_local_path, repo_root)}: {upload_err}")
                stats["upload_failures"] += 1
                return None

        # 1. Replace YAML image fields: image: "path/to/img.png"
        yaml_pattern = re.compile(r'^(\s*image:\s*)(["\']?)([^"\'\n\r]+)(["\']?)', re.MULTILINE)
        def yaml_replacer(match):
            prefix = match.group(1)
            quote_start = match.group(2)
            path = match.group(3).strip()
            quote_end = match.group(4)
            
            new_url = process_path(path)
            if new_url:
                return f'{prefix}"{new_url}"'
            return match.group(0)
            
        content = yaml_pattern.sub(yaml_replacer, content)
        
        # 2. Replace Markdown images: ![alt](path)
        markdown_pattern = re.compile(r'(!\[[^\]]*\]\()([^)]+)(\))')
        def markdown_replacer(match):
            prefix = match.group(1)
            path_part = match.group(2).strip()
            suffix = match.group(3)
            
            # Clean path from possible markdown parameters or titles
            path_match = re.match(r'^([^\s"\']+)', path_part)
            if not path_match:
                return match.group(0)
                
            path = path_match.group(1)
            new_url = process_path(path)
            if new_url:
                new_path_part = path_part.replace(path, new_url, 1)
                return f'{prefix}{new_path_part}{suffix}'
            return match.group(0)
            
        content = markdown_pattern.sub(markdown_replacer, content)
        
        # 3. Replace HTML images: <img src="path">
        html_pattern = re.compile(r'(<img\s+[^>]*src=)(["\'])([^"\']+)(["\'])')
        def html_replacer(match):
            prefix = match.group(1)
            quote_start = match.group(2)
            path = match.group(3).strip()
            quote_end = match.group(4)
            
            new_url = process_path(path)
            if new_url:
                return f'{prefix}{quote_start}{new_url}{quote_end}'
            return match.group(0)
            
        content = html_pattern.sub(html_replacer, content)
        
        # Save modifications
        if modified:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Updated file: {os.path.relpath(file_path, repo_root)}\n")
                stats["files_modified"] += 1
            except Exception as e:
                print(f"Error saving changes to {file_path}: {e}")
                
    # Print Run Summary
    print("\n--- Cloudinary Auto-Upload Run Summary ---")
    print(f"Files scanned:    {stats['files_scanned']}")
    print(f"Files modified:   {stats['files_modified']}")
    print(f"Images uploaded:  {stats['images_uploaded']}")
    if stats['upload_failures'] > 0:
        print(f"Upload failures:  {stats['upload_failures']}")
    print("-------------------------------------------\n")

if __name__ == '__main__':
    main()
