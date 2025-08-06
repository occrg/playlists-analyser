import json
import requests
from itertools import repeat
import time
import os.path
import statistics
import csv
import matplotlib.pyplot as plt
import numpy as np
import os

SPOTIFY_API_URL = "https://api.spotify.com/v1/"
SPOTIFY_API_PLAYLIST_ENDPOINT_URL = SPOTIFY_API_URL + "playlists/"
SPOTIFY_AUTH_ENDPOINT_URL = "https://accounts.spotify.com/api/token"

TRACK_ANALYSIS_API_URL = "https://track-analysis.p.rapidapi.com/pktx/"
TRACK_ANALYSIS_API_GET_ANALYSIS_ENDPOINT_URL = TRACK_ANALYSIS_API_URL + "spotify/"

OUTPUT_FOLDER_FILE_PATH = "outputs/"
TRACKLIST_DATA_FILE_PATH = "tracklist_data.json"
ENV_VARIABLES_FILE_PATH = "variables.json"


def get_spotify_access_token(spotify_auth):
    auth_form_data = {
        "grant_type": "client_credentials",
        "client_id": spotify_auth["client_id"],
        "client_secret": spotify_auth["client_secret"]
    }

    auth_response = requests.post(SPOTIFY_AUTH_ENDPOINT_URL, data=auth_form_data)
    access_token = auth_response.json()["access_token"]

    return access_token

def get_spotify_playlist_tracks(spotify_access_token, playlist_id):    
    playlist_url = SPOTIFY_API_PLAYLIST_ENDPOINT_URL + playlist_id

    standard_request_header = {
        "Authorization": f"Bearer {spotify_access_token}"
    }
    playlist_request_parameters = {
        "fields": "name,tracks.items(track(id,name,popularity,duration_ms,artists(id,name),album(id,name,album_type,release_date,release_date_precision)))"
    }

    playlist_response = requests.get(playlist_url, params=playlist_request_parameters, headers=standard_request_header)
    playlist_response_json = playlist_response.json()
    playlist_response_json.update({ "playlist_id": playlist_id })
    return playlist_response_json

def create_playlist_data_dict(spotify_playlist_data):
    playlist_data = {}
    for spotify_playlist in spotify_playlist_data:
        playlist_data.update({
            spotify_playlist["playlist_id"]: {
                "name": spotify_playlist["name"],
                "aggregated_track_qualities": {}
            }})
    return playlist_data

def add_playlist_id_to_track(playlist_track_data, playlist_id):
    playlist_track_data.update({ "playlist_id": playlist_id })
    return playlist_track_data

def create_tracklist_from_playlist_data(spotify_playlist_data):
    tracklist_for_all_spotify_playlists = []
    for playlist_data in spotify_playlist_data:
        playlist_track_data = playlist_data["tracks"]["items"]
        playlist_flat_track_data = list(map(add_playlist_id_to_track, playlist_track_data, repeat(playlist_data["playlist_id"])))
        tracklist_for_all_spotify_playlists.extend(playlist_flat_track_data)
    return tracklist_for_all_spotify_playlists

def get_track_qualities_from_api(track_analysis_auth, track):
    track_url = TRACK_ANALYSIS_API_GET_ANALYSIS_ENDPOINT_URL + track["track"]["id"]
    
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

    loudness = track_qualities["loudness"]
    if isinstance(track_qualities["loudness"], str):
        loudness  = int(float(track_qualities["loudness"][:-3]))
    
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
            "loudness": loudness
        }
    })

    del track["track"]["popularity"]
    del track["track"]["duration_ms"]

    return track

def calculate_playlist_aggregated_qualities(playlist_id_name_dict, tracklist, attributes_to_find_mean_for):
    playlist_data = playlist_id_name_dict
    for playlist_id in playlist_id_name_dict.keys():
        tracks_in_playlist = [track for track in tracklist if track["playlist_id"] == playlist_id]
        for key_name in attributes_to_find_mean_for.keys():
            key_values_in_playlist = [dict["track_qualities"][key_name] for dict in tracks_in_playlist]
            playlist_data[playlist_id]["aggregated_track_qualities"].update({
                key_name: {
                    "values": key_values_in_playlist,
                    "mean": statistics.mean(key_values_in_playlist)
                }
            })
    return playlist_data

def get_spotify_playlist_data(spotify_auth, playlist_ids):
    spotify_access_token = get_spotify_access_token(spotify_auth)
    spotify_playlist_data = list(map(get_spotify_playlist_tracks, repeat(spotify_access_token), playlist_ids))
    return spotify_playlist_data

def get_playlist_tracklist(spotify_playlist_data, x_rapid_auth):
    previous_tracklist_data = []
    previous_tracklist_data_json = []
    if os.path.isfile(TRACKLIST_DATA_FILE_PATH):
        with open(TRACKLIST_DATA_FILE_PATH, "r") as file:
            previous_tracklist_data = file.read()
        previous_tracklist_data_json = json.loads(previous_tracklist_data)

    tracklist = create_tracklist_from_playlist_data(spotify_playlist_data)
    tracklist = list(map(add_track_quality_to_tracklist, repeat(x_rapid_auth), tracklist, repeat(previous_tracklist_data_json)))

    return tracklist

def export_tracklist_to_csv(tracklist, playlist_data):
    tracklist_csv = [["track_id", "track_name", "playlist_id", "playlist_name", "release_id", "release_name", "release_type", "release_date", "key", "mode", "tempo", "popularity", "duration_min", "energy", "danceability", "happiness", "acousticness", "instrumentalness", "liveness", "speechiness", "loudness_dB"]]
    for track in tracklist:
        this_tracklist = []
        this_tracklist.append(track["track"]["id"])
        this_tracklist.append(track["track"]["name"])
        this_tracklist.append(track["playlist_id"])
        this_tracklist.append(playlist_data[track["playlist_id"]]["name"])
        this_tracklist.append(track["track"]["album"]["id"])
        this_tracklist.append(track["track"]["album"]["name"])
        this_tracklist.append(track["track"]["album"]["album_type"])
        this_tracklist.append(track["track"]["album"]["release_date"])
        this_tracklist.append(track["track_qualities"]["key"])
        this_tracklist.append(track["track_qualities"]["mode"])
        this_tracklist.append(track["track_qualities"]["tempo"])
        this_tracklist.append(track["track_qualities"]["popularity"])
        this_tracklist.append(track["track_qualities"]["duration_ms"] / 60000)
        this_tracklist.append(track["track_qualities"]["energy"])
        this_tracklist.append(track["track_qualities"]["danceability"])
        this_tracklist.append(track["track_qualities"]["happiness"])
        this_tracklist.append(track["track_qualities"]["acousticness"])
        this_tracklist.append(track["track_qualities"]["instrumentalness"])
        this_tracklist.append(track["track_qualities"]["liveness"])
        this_tracklist.append(track["track_qualities"]["speechiness"])
        this_tracklist.append(track["track_qualities"]["loudness"])

        tracklist_csv.append(this_tracklist)

        with open(OUTPUT_FOLDER_FILE_PATH + "tracklist.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(tracklist_csv)

def export_tracklist_to_json_file(tracklist):
    with open(TRACKLIST_DATA_FILE_PATH, "w+") as file:
        file.write(json.dumps(tracklist))

def visualise_playlist_data(playlist_data, attributes_to_find_mean_for):
    playlist_names = [dict["name"] for dict in playlist_data.values()]
    xticks = list(range(len(playlist_names)))
    xpoints = np.array(xticks)
    x_for_trend_lines = np.arange(0, len(playlist_names)-1, 0.01)
    for key_name in attributes_to_find_mean_for.keys():
        mean_values = [dict["aggregated_track_qualities"][key_name]["mean"] for dict in playlist_data.values()]
        ypoints = np.array(mean_values)

        polyreg = np.polyfit(xpoints, ypoints, attributes_to_find_mean_for[key_name]["polynomial_degree"])
        polypred = np.poly1d(polyreg)
        predp = polypred(x_for_trend_lines)

        fig, ax = plt.subplots()
        ax.scatter(xpoints, ypoints)
        ax.plot(x_for_trend_lines, predp)
        ax.set_xlabel("Playlist")
        ax.set_xticks(xticks, playlist_names)
        ax.set_ylabel(key_name)

        if attributes_to_find_mean_for[key_name]["value_parity"] == "negative":
            ax.set_ylim(ymax = 0.0)
        else:
            ax.set_ylim(ymin=0.0)

        fig.savefig(OUTPUT_FOLDER_FILE_PATH + key_name + "_visualisation")

def run_script():
    with open(ENV_VARIABLES_FILE_PATH, "r") as file:
        env_vars = file.read()
    env_vars_json = json.loads(env_vars)

    os.makedirs(OUTPUT_FOLDER_FILE_PATH, exist_ok=True)

    spotify_playlist_data = get_spotify_playlist_data(env_vars_json["spotify_auth"], env_vars_json["playlist_ids"])
    playlist_id_name_dict = create_playlist_data_dict(spotify_playlist_data)
    tracklist = get_playlist_tracklist(spotify_playlist_data, env_vars_json["x_rapid_auth"])
    export_tracklist_to_json_file(tracklist)
    export_tracklist_to_csv(tracklist, playlist_id_name_dict)

    playlist_data = calculate_playlist_aggregated_qualities(playlist_id_name_dict, tracklist, env_vars_json["attributes_to_find_mean_for"])
    visualise_playlist_data(playlist_data, env_vars_json["attributes_to_find_mean_for"])

run_script()