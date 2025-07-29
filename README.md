# Playlists Analyser
## Description
A tool that analyses the songs in Spotify playlists and how the features of the songs differ in each.

## Current functionality
The application currently takes a list of Spotify playlists and returns the Spotify IDs, artists and names of the songs within each playlists.

## Future functionality
1. The application should call the [Track Analysis API](https://rapidapi.com/soundnet-soundnet-default/api/track-analysis/playground/apiendpoint_78b81b32-03a1-4044-aa46-ac17aa2528fe) to get qualities of each track.
1. Each playlist will have their tracks' qualities aggregated.
1. The playlists aggregated qualities will be visualised.

## Pre-requisites
* You have Python installed on your computer.
* You have a Spotify account.
* You have playlists you want to analyse and have [found their Spotify IDs](https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids).
* You have [made a Spotify API application](https://developer.spotify.com/documentation/web-api/concepts/apps) that can access the Spotify Web API.

## Instructions
1. Copy the `variables.example.json` file and give it the name `vairables.json` and replace the values with your own values.
1. Run the `playlist-analyser.py` file.

