import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
# Your YouTube API Key is correctly placed here.
YOUTUBE_API_KEY = "YOUR_API_KEY" 
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def find_youtube_resources(skill_name: str, max_results: int = 3) -> list:
    """
    Finds learning resources for a given skill using the YouTube Data API.
    """
    # THIS IS THE CORRECTED CHECK: It now looks for the original placeholder.
    if not YOUTUBE_API_KEY or "PASTE_YOUR_API_KEY_HERE" in YOUTUBE_API_KEY:
        print("WARNING: YouTube API key is not configured. Cannot fetch dynamic resources.")
        return []

    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)

        # Construct a search query focused on tutorials
        search_query = f"{skill_name} tutorial for beginners"

        # Call the search.list method to retrieve results
        search_response = youtube.search().list(
            q=search_query,
            part="snippet",
            maxResults=max_results,
            type="video",
            relevanceLanguage="en"
        ).execute()

        resources = []
        for item in search_response.get("items", []):
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            
            # Format the output to be consistent with our resources.json structure
            resources.append({
                "title": video_title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "type": "Video Tutorial"
            })
        
        return resources

    except HttpError as e:
        # This will now give you a more descriptive error if the key is invalid
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

