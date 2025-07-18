import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
import unicodedata

# Load environment variables
load_dotenv()

# Set up Spotify API access
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

# Load and normalize CSV column names
df = pd.read_csv('spotify-2023.csv', encoding='ISO-8859-1')
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

# Check column names
# print("Columns:", df.columns)

# Clean non-ASCII characters and split artist name
def clean_text(text):
    return (
        unicodedata.normalize("NFKD", str(text))
        .encode("ascii", "ignore")
        .decode("utf-8")
        .strip()
    )

# Define function to get cover URL
def get_cover_url(track_name, artist_name):
    try:
        clean_track = clean_text(track_name)
        clean_artist = clean_text(artist_name.split(',')[0])  # Use only the first artist
        query = f'track:{clean_track} artist:{clean_artist}'
        result = sp.search(q=query, type='track', limit=1)
        items = result.get('tracks', {}).get('items', [])
        if items:
            return items[0]['album']['images'][0]['url']
        else:
            print(f"No result for: {track_name} by {artist_name}")
            return None
    except Exception as e:
        print(f"Error fetching {track_name} by {artist_name}: {e}")
        return None


# Optional: limit rows during testing
# df = df.head(50)

# Apply the function
df['cover_url'] = df.apply(lambda row: get_cover_url(row['track_name'], row['artist(s)_name']), axis=1)

# Save updated dataset
df.to_csv('spotify_with_covers.csv', index=False)

print("✅ Done. Saved as spotify_with_covers.csv")
