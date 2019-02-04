import os
import json
import spotipy
from spotipy import SpotifyException
import spotipy.util as util
from json.decoder import JSONDecodeError

from random import randint


def sort_artists(artists):
    """Takes the list of artists and returns a list of their ids
    artists: list of Artist objects
    return: list of Artist IDs"""
    list_of_artists = []
    for artist in artists:
        artist_id = artist['id']
        list_of_artists.append(artist_id)
    return list_of_artists


def find_related_artists_songs(artists, variety=5):
    """Takes a list of artists IDs and returns a list of each of those artists top song ID
    artists: list of Artist's by ID
    variety: Level of variety in results
    return: list of related artists song ID's"""
    list_of_songs = []
    for artist in artists:
        rand = randint(0, (variety * 4) - 1)
        related_artist = spotifyObject.artist_related_artists(artist)['artists'][rand]['id']
        top_song = get_artist_top_song(related_artist, variety)
        list_of_songs.append(top_song)
    return list_of_songs


def get_artist_top_song(artist, variety=5):
    """Takes in an artists id and returns one of their tops songs
    artist: An artist's ID
    variety: Level of variety in results
    return: One of the given artist's song IDs"""
    rand = randint(0, (variety * 2) - 1)
    try:
        top_song = spotifyObject.artist_top_tracks(artist)['tracks'][rand]['id']
    except IndexError:
        top_song = spotifyObject.artist_top_tracks(artist)['tracks'][0]['id']
    return top_song


# Takes in the username, id, and client secret from the terminal
username = input("Please enter your spotify username: ")
client_id = input("Please enter your spotify client_id: ")
client_password = input("Please enter your spotify client_password: ")

# Scope for what the user needs to authorize
scope = 'playlist-modify-public user-read-playback-state user-top-read user-modify-playback-state'

# Erase the current cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope, client_id,
                                       client_password, 'http://google.com/')
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, client_id,
                                       client_password, 'http://google.com/')

# Create our spotifyObject with permissions
spotifyObject = spotipy.Spotify(auth=token)

time = ''
# Find out what time frame the user wants their related artists to come from
while True:
    timeframe = input('Would you like your top artists to based on a short-term, medium-term, ' +
                      'or long-term?: ')
    if timeframe == 'short-term':
        time = 'short_term'
        break
    elif timeframe == 'medium-term':
        time = 'medium_term'
        break
    elif timeframe == 'long-term':
        time = 'long_term'
        break
    else:
        print("Invalid user input! Please specify a correct option ('short-term', 'medium-term', " +
              "'long-term').")

# Find out how large of a playlist the user wants
while True:
    playlist_size = int(input("How large would you like this new playlist to be? (Maximum 50 songs): "))
    if playlist_size < 1 or playlist_size > 50:
        print('Error: ' + str(playlist_size) + ' is not a valid playlist size')
    else:
        break

while True:
    try:
        randomness = int(input('On a scale of 1 being more well known results to 5 being a wider variety of results,' +
                               ' how well known do you want\nthe songs in the playlist to be?: '))
    except ValueError:
        print('That is not an integer, please insert an integer between 1 and 5')
    else:
        if randomness < 1 or randomness > 5:
            print('That is not a valid input, please insert an integer between 1 and 5')
        else:
            break

# Access the users top artists
top_artists = spotifyObject.current_user_top_artists(limit=playlist_size, time_range=time)

# Retrieve top artists IDs
artist_ids = sort_artists(top_artists['items'])

# Retrieve related artists top song ID's
related_artists_songs = find_related_artists_songs(artist_ids, randomness)

# Find out what the user wants to name their new playlist
playlist_name = input("Please enter a name for this new playlist: ")

# Create a new playlist
new_playlist = spotifyObject.user_playlist_create(username, playlist_name)
new_playlist_uri = new_playlist['uri']
new_playlist_id = new_playlist['id']

# Add songs to that playlist
spotifyObject.user_playlist_add_tracks(username, new_playlist_id, related_artists_songs)

while True:
    # Prompts the user if they'd like to start playing their new playlist if possible.
    play = input("Success! Would you like to start playing " + playlist_name + " now? (Y/n): ")
    if play == 'Y' or play == 'y':
        try:
            devices = spotifyObject.devices()
            deviceID = devices['devices'][0]['id']
        except SpotifyException:
            # If the user is not currently using a spotify device.
            print("No device currently playing.")
            print("Playlist creation completed.")
            break
        else:
            spotifyObject.start_playback(deviceID, new_playlist_uri)
            print("Playlist creation completed.")
            break
    elif play == 'n':
        print('Playlist creation completed.')
        break
    else:
        print("Invalid input, try again")

# print(json.dumps(VARIABLE, sort_keys=True, indent=4))
