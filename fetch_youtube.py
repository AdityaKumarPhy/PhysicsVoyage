import os
import json
import urllib.request

def load_env():
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env_vars[key] = val
    return env_vars

def main():
    env = load_env()
    api_key = env.get('YOUTUBE_API_KEY')
    channel_id = env.get('YOUTUBE_CHANNEL_ID')
    uploads_playlist_id = env.get('YOUTUBE_UPLOADS_PLAYLIST_ID')

    if not api_key or not channel_id or not uploads_playlist_id:
        print("Skipping YouTube fetch: Missing API key or Channel IDs in .env")
        return

    try:
        # 1. Fetch Latest Video (from Uploads Playlist)
        latest_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist_id}&maxResults=1&key={api_key}"
        with urllib.request.urlopen(latest_url) as response:
            latest_data = json.loads(response.read().decode())
        
        latest_video_id = latest_data['items'][0]['snippet']['resourceId']['videoId']
        latest_title = latest_data['items'][0]['snippet']['title']

        # 2. Fetch Most Popular Video
        popular_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&order=viewCount&maxResults=1&type=video&key={api_key}"
        with urllib.request.urlopen(popular_url) as response:
            popular_data = json.loads(response.read().decode())
        
        popular_video_id = popular_data['items'][0]['id']['videoId']
        popular_title = popular_data['items'][0]['snippet']['title']

        video_data = {
            "latest": {"id": latest_video_id, "title": latest_title},
            "popular": {"id": popular_video_id, "title": popular_title}
        }

        # Write to the root so Quarto can copy it to _site/docs, but actually 
        # it's best to write it into the docs/ directory or root? 
        # If we write to root, Quarto might ignore it unless it's in resources.
        # Let's write it to root and also include it in index.qmd Javascript properly.
        with open('youtube-data.json', 'w') as f:
            json.dump(video_data, f, indent=2)
            
        print("Successfully fetched YouTube data and saved to youtube-data.json")

    except Exception as e:
        print(f"Error fetching YouTube data: {e}")

if __name__ == '__main__':
    main()
