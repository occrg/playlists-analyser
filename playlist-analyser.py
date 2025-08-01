import json
import requests
from itertools import repeat
import time
import os.path

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
        "fields": "name,tracks.items(track(id,name,popularity,duration_ms,artists(id,name)))"
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

def get_track_qualities_from_api(track_analysis_auth, track):
    track_analysis_url = "https://track-analysis.p.rapidapi.com/pktx/"
    track_analysis_endpoint = "spotify/"
    track_url = track_analysis_url + track_analysis_endpoint + track["track"]["id"]
    
    standard_request_header = {
        "x-rapidapi-key": track_analysis_auth["api_key"]
    }

    track_analysis_response = requests.get(track_url, headers=standard_request_header)

    time.sleep(2)

    return track_analysis_response.json()

def get_track_qualities_from_previous(previous_tracklist_data, current_track):
    track_analysis = {}
    previous_tracklist_data_filtered = [track for track in previous_tracklist_data if track["track"]["id"] == current_track["track"]["id"]]
    if len(previous_tracklist_data_filtered) == 1:
        track_analysis = previous_tracklist_data_filtered[0]["track_qualities"]
    return track_analysis

def get_track_qualities(track_analysis_auth, track, previous_tracklist_data):
    track_analysis = {}
    track_analysis = get_track_qualities_from_previous(previous_tracklist_data, track)
    if track_analysis == {}:
        track_analysis = get_track_qualities_from_api(track_analysis_auth, track)
    return track_analysis

def add_track_quality_to_tracklist(track_analysis_auth, track, previous_tracklist_data):
    track_qualities = get_track_qualities(track_analysis_auth, track, previous_tracklist_data)
    
    track.update({
        "track_qualities": {
            "key": track_qualities["key"],
            "mode": track_qualities["mode"],
            "tempo": track_qualities["tempo"],
            "popularity": track["track"]["popularity"],
            "duration_ms": track["track"]["duration_ms"],
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

    del track["track"]["popularity"]
    del track["track"]["duration_ms"]

    return track

def run_script():
    with open("variables.json", "r") as file:
        env_vars = file.read()
    env_vars_json = json.loads(env_vars)

    previous_tracklist_data = []
    previous_tracklist_data_json = []
    if os.path.isfile("tracklist_data.json"):
        with open("tracklist_data.json", "r") as file:
            previous_tracklist_data = file.read()
        previous_tracklist_data_json = json.loads(previous_tracklist_data)

    spotify_access_token = get_spotify_access_token(env_vars_json["spotify_auth"])
    tracklist_for_all_playlists = create_tracklist_for_all_spotify_playlists(spotify_access_token, env_vars_json["playlist_ids"])
    tracklist_for_all_playlists_with_track_qualities = list(map(add_track_quality_to_tracklist, repeat(env_vars_json["x_rapid_auth"]), tracklist_for_all_playlists, repeat(previous_tracklist_data_json)))

    with open("tracklist_data.json", "w+") as file:
        file.write(json.dumps(tracklist_for_all_playlists_with_track_qualities))

run_script()