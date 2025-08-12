# Playlists Analyser
## Description
A tool that visualises the qualities of songs in a set of Spotify playlists and converts this into a readable form to create a physical manifestation of this visualisation. 

## Current functionality
The application currently takes a list of Spotify playlists and returns a flat list of tracks with their names, artists and qualities from the [Track Analysis API](https://rapidapi.com/soundnet-soundnet-default/api/track-analysis/playground/apiendpoint_78b81b32-03a1-4044-aa46-ac17aa2528fe). It then aggregates the tracks' data by their playlist.

The tracklist data exports to a csv so visualisations can be experimented with outside of a Python environment. The aggregated playlist data is visualised in some basic graphs and saved as images.

## Future functionality
1. Create tree map or bar chart of artists with artist images in background.
1. All visualisations will be converted into a form readable by software that engraves the graphs into a material.
1. Other additions to existing charts may be experimented with. For example, plotting the plotting individual track qualities on their release dates (instead of on an x-axis point representing the whole playlist) and using other aggregations such as min, max, median, deviation.
1. Charts may be made out of other data. For example, most common keys used, most common release month/season.

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
1. Change chart positioning, gridlines and legends to be appropriate so the graphs can be look good when stacked on top of each other.
    1. Allow customisation of what numbers y-axis starts and finishes on.
    1. Allow customisation of legend names.
1. Add error handling for API calls.
1. Add limit to how many times the Track Analysis API can be called.
1. Store data from [other Track Analysis API](https://rapidapi.com/music-metrics-music-metrics-default/api/spotify-audio-features-track-analysis), compare (including check whether happiness is the same as valence between different APIs) and use both in visualisations to see if either set of data produces better visualisations.
1. Add error handling for reading in files. Abort when variables.json doesn't exist and handle appropriately where data in `variables.json` or `tracklist_data.json` is stored incorrectly or missing.

