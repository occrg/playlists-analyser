import json
import requests
from itertools import repeat
import time

def get_spotify_access_token(spotify_auth):
    url = "https://accounts.spotify.com/api/token"

    auth_form_data = {
        "grant_type": "client_credentials",
        "client_id": spotify_auth["client_id"],
        "client_secret": spotify_auth["client_secret"]
    }

    auth_response = requests.post(url, data=auth_form_data)
    access_token = auth_response.json()["access_token"]

    return access_token

def get_spotify_playlist_tracks(spotify_access_token, playlist_id):
    spotify_url = "https://api.spotify.com/v1/"
    playlist_endpoint = "playlists/"
    playlist_url = spotify_url + playlist_endpoint + playlist_id

    standard_request_header = {
        "Authorization": f"Bearer {spotify_access_token}"
    }
    playlist_request_parameters = {
        "fields": "name,tracks.items(track(id,name,artists(id,name)))"
    }

    playlist_response = requests.get(playlist_url, params=playlist_request_parameters, headers=standard_request_header)
    
    return playlist_response.json()

def flatten_song_data(playlist_track_data, playlist_name):
    playlist_track_data.update({"playlist_name": playlist_name})
    return playlist_track_data

def create_tracklist_for_all_spotify_playlists(spotify_access_token, playlist_ids):
    tracklist_for_all_spotify_playlists = []
    for playlist_id in playlist_ids:
        playlist_data = get_spotify_playlist_tracks(spotify_access_token, playlist_id)
        playlist_track_data = playlist_data["tracks"]["items"]
        playlist_flat_track_data = list(map(flatten_song_data, playlist_track_data, repeat(playlist_data["name"])))
        tracklist_for_all_spotify_playlists.extend(playlist_flat_track_data)
    return tracklist_for_all_spotify_playlists

def get_track_qualities(track_analysis_auth, track):
    track_analysis_url = "https://track-analysis.p.rapidapi.com/pktx/"
    track_analysis_endpoint = "spotify/"
    track_url = track_analysis_url + track_analysis_endpoint + track["track"]["id"]
    
    standard_request_header = {
        "x-rapidapi-key": track_analysis_auth["api_key"]
    }

    track_analysis_response = requests.get(track_url, headers=standard_request_header)

    time.sleep(2)

    return track_analysis_response.json()


def add_track_quality_to_tracklist(track_analysis_auth, track):
    track_qualities = get_track_qualities(track_analysis_auth, track)
    
    track.update({
        "track_qualities": {
            "key": track_qualities["key"],
            "mode": track_qualities["mode"],
            "tempo": track_qualities["tempo"],
            "popularity": track_qualities["popularity"],
            "energy": track_qualities["energy"],
            "danceability": track_qualities["danceability"],
            "happiness": track_qualities["happiness"],
            "acousticness": track_qualities["acousticness"],
            "instrumentalness": track_qualities["instrumentalness"],
            "liveness": track_qualities["liveness"],
            "speechiness": track_qualities["speechiness"],
            "loudness": track_qualities["loudness"]
        }
    })

    return track

def run_script():
    with open("variables.json", "r") as file:
        env_vars = file.read()
    
    env_vars_json = json.loads(env_vars)

    spotify_access_token = get_spotify_access_token(env_vars_json["spotify_auth"])
    tracklist_for_all_playlists = create_tracklist_for_all_spotify_playlists(spotify_access_token, env_vars_json["playlist_ids"])
    tracklist_for_all_playlists_with_track_qualities = list(map(add_track_quality_to_tracklist, repeat(env_vars_json["x_rapid_auth"]), tracklist_for_all_playlists))

    print(json.dumps(tracklist_for_all_playlists_with_track_qualities))

run_script()