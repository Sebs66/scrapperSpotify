''' This is a test to connect to the Spotify API using client credentials flow.
https://developer.spotify.com/documentation/general/guides/authorization/client-credentials/
https://prettystatic.com/automate-the-spotify-api-with-python/
https://developer.spotify.com/documentation/web-api
'''

import base64
import requests
import json

def get_token(client_id,client_secret):
    url = 'https://accounts.spotify.com/api/token'
    #/ La autorizacion debe realizarse en headers, y debe ser una string codificada en Base64 con el client id y secret.
    auth_string = bytes('{}:{}'.format(client_id,client_secret),'utf-8')
    b64_auth_string = base64.b64encode(auth_string).decode('utf-8')
    headers = {'Authorization' : 'Basic '+b64_auth_string}
    data = {'grant_type' : 'client_credentials'}
    response = requests.post(url=url,headers=headers,data=data)
    #print(json.dumps(response.json(), indent=2))
    return response.json()['access_token']

def get_playlist(token,playlist_id):
    #/ Playlist endpoint: https://api.spotify.com/v1/playlists/{playlistId}
    endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {
        "Authorization": "Bearer " + token
    }
    res = requests.get(url=endpoint, headers=headers)
    #print(json.dumps(res.json(), indent=2)) #/ To see the json object.
    return res.json()

def get_song(token,song_id):
    endpoint = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = {
        "Authorization": "Bearer " + token
    }
    res = requests.get(url=endpoint, headers=headers)
    #print(json.dumps(res.json(), indent=2)) #/ To see the json object.
    return res.json()

def get_artist(token,artist_id):
    endpoint = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {
        "Authorization": "Bearer " + token
    }
    res = requests.get(url=endpoint, headers=headers)
    #print(json.dumps(res.json(), indent=2)) #/ To see the json object.
    return res.json()


if __name__ == '__main__':
    import credentials
    client_id = credentials.CLIENT_ID
    client_secret = credentials.CLIENT_SECRET
    token = get_token(client_id=client_id,client_secret=client_secret)
    playlistId = '37i9dQZEVXbKAbrMR8uuf7' #/ Top50 Chile
    song_id = '6pD0ufEQq0xdHSsRbg9LBK'
    #playlist = get_playlist(token,playlistId)
    #print(playlist) #/ dict_keys(['collaborative', 'description', 'external_urls', 'followers', 'href', 'id', 'images', 'name', 'owner', 'primary_color', 'public', 'snapshot_id', 'tracks', 'type', 'uri'])
    #print(playlist['name'])
    # artist = get_artist(token,'1fIJZfSmqQkuqfKNRmrS1V')
    # print(artist)
    song = get_song(token,song_id)
    print(song)