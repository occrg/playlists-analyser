# Playlists Analyser
## Description
A tool that analyses the songs in Spotify playlists and how the features of the songs differ in each.

## Current functionality
The application currently takes a list of Spotify playlists and returns a flat list of tracks with their names, artists and qualities from the [Track Analysis API](https://rapidapi.com/soundnet-soundnet-default/api/track-analysis/playground/apiendpoint_78b81b32-03a1-4044-aa46-ac17aa2528fe).

## Future functionality
1. Each playlist will have their tracks' qualities aggregated.
1. The playlists aggregated qualities will be visualised.

## Pre-requisites
* You have Python installed on your computer.
* You have a Spotify account.
* You have playlists you want to analyse and have [found their Spotify IDs](https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids).
* You have [made a Spotify API application](https://developer.spotify.com/documentation/web-api/concepts/apps) that can access the Spotify Web API.

## Instructions
1. Copy the `variables.example.json` file and give it the name `variables.json` and replace the values with your own values.
1. The script stores data from the Track Analysis API to ensure it doesn't have to call the API (which has rate limits) multiple times for the same data. If you do want to refresh the data using the API, delete the appropriate track's data from `tracklist_data.json` or delete the whole file if you want to refresh all the data.
1. Run the `playlist-analyser.py` file.

## To Do
This is a list of things to do for the project, not including implementing the "future functionality" above.
1. Add Spotify popularity and duration to qualities.
1. Check whether happiness is the same as valence between different APIs.
1. Ensure global constants are kept separately.
1. Add error handling for API calls.
1. Add limit to how many times the Track Analysis API can be called.
1. Store data from [other Track Analysis API](https://rapidapi.com/music-metrics-music-metrics-default/api/spotify-audio-features-track-analysis), compare and use both in visualisations to see if either set of data produces better visualisations.

