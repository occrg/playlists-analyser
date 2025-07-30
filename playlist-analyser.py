import json
import requests
from itertools import repeat

with open("variables.json", "r") as file:
    env_vars = file.read()

env_vars_json = json.loads(env_vars)

def get_spotify_auth_header():
    url = "https://accounts.spotify.com/api/token"

    auth_form_data = {
        "grant_type": "client_credentials",
        "client_id": env_vars_json["spotify_auth"]["client_id"],
        "client_secret": env_vars_json["spotify_auth"]["client_secret"]
    }

    auth_response = requests.post(url, data=auth_form_data)
    access_token = auth_response.json()["access_token"]

    return access_token

def get_spotify_playlist_tracks(playlist_id):
    spotify_url = "https://api.spotify.com/v1/"
    playlist_endpoint = "playlists/"
    playlist_url = spotify_url + playlist_endpoint + playlist_id

    standard_request_header = {
        "Authorization": f"Bearer {get_spotify_auth_header()}"
    }
    playlist_request_parameters = {
        "fields": "name,tracks.items(track(id,name,artists(id,name)))"
    }

    playlist_response = requests.get(playlist_url, params=playlist_request_parameters, headers=standard_request_header)
    
    return playlist_response.json()

def flatten_song_data(playlist_track_data, playlist_name):
    playlist_track_data.update({"playlist_name": playlist_name})
    return playlist_track_data

def create_tracklist_for_all_spotify_playlists():
    tracklist_for_all_spotify_playlists = []
    for playlist_id in env_vars_json["playlist_ids"]:
        playlist_data = get_spotify_playlist_tracks(playlist_id)
        playlist_track_data = playlist_data["tracks"]["items"]
        playlist_flat_track_data = list(map(flatten_song_data, playlist_track_data, repeat(playlist_data["name"])))
        tracklist_for_all_spotify_playlists.extend(playlist_flat_track_data)
    print(json.dumps(tracklist_for_all_spotify_playlists))

create_tracklist_for_all_spotify_playlists()