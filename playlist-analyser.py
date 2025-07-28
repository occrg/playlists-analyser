import json
import requests

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

def get_spotify_playlist_tracks():
    spotify_url = "https://api.spotify.com/v1/"
    playlist_endpoint = "playlists/"
    playlist_url = spotify_url + playlist_endpoint + env_vars_json["playlist_id"]

    standard_request_header = {
        "Authorization": f"Bearer {get_spotify_auth_header()}"
    }
    playlist_request_parameters = {
        "fields": "tracks.items(track(id,name,artists(id,name)))"
    }

    playlist_response = requests.get(playlist_url, params=playlist_request_parameters, headers=standard_request_header)
    playlist_response_tracks = playlist_response.json()["tracks"]["items"]
    print(playlist_response_tracks)


get_spotify_playlist_tracks()