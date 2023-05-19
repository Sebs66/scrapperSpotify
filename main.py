import datetime
import time
import json
import credentials
import codecs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import bs4
from bs4 import BeautifulSoup

import spotifyAPI

def get_song_data(data:bs4.element.Tag):
    '''
    Returns an object: {'ranking':int,'title':str,'artists':list[str],'plays':int,'album':str}
    '''
    info = data.find_all('div',recursive=False) #/ 5 divs.
    ranking = int(info[0].text)
    title = info[1].div.div.text
    if len(info[1].div.find_all('span',recursive=False)) == 2: #/ La cancion tiene tag explicito.
        artists = info[1].div.span.next_sibling.text.split(',')
    else:
        artists = info[1].div.span.text.split(',')
    plays = int(info[2].text.replace(',',''))
    album = info[3].text
    return {'ranking':ranking,'title':title,'artists':artists,'plays':plays,'album':album}

def get_song_data_V2(data:bs4.element.Tag,info_API:dict):
    '''
    Returns an object with the structure:
    {   
        "ranking": int,
        "name": str,
        "artists": [{"name": str,"artist_id": str}],
        "plays": int,
        "album": { "name": str, "album_id": str, "release_date": "2023-03-02" },
        "popularity": int,
        "song_id": str
    }
    '''
    info = data.find_all('div',recursive=False) #/ 5 divs.
    ranking = int(info[0].text)
    plays = int(info[2].text.replace(',',''))
    album = {'name':info_API['album']['name'],'album_id':info_API['album']['id'],'release_date':info_API['album']['release_date']}
    song_id = info_API['id']
    name = info_API['name']
    popularity = info_API['popularity']
    artists = [{'name':info['name'],'artist_id':info['id']} for info in info_API['artists']]
    return {'ranking':ranking,'name':name,'artists':artists,'plays':plays,'album':album,'popularity':popularity,'song_id':song_id}

def get_top_50_info(driver:webdriver.Chrome,country:str,playlist_id:str,token:str):
    '''
    Returns an object as : 
    {   country: str,
        date: 'YYYY/MM/DD'
        totalPlays : int,
        data: [
            {'ranking':int,'title':str,'artists':list[str],'plays':int,'album':str},
            {'ranking':int,'title':str,'artists':list[str],'plays':int,'album':str}
        ]    
    }
    '''
    driver.get(f'https://open.spotify.com/playlist/{playlist_id}')
    try:
        elements = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.contentSpacing')))
        containers = driver.find_elements(By.CSS_SELECTOR,'div.contentSpacing')
        while len(containers) < 4:
            time.sleep(1)
            print('Waiting')
            containers = driver.find_elements(By.CSS_SELECTOR,'div.contentSpacing')

        songs = containers[2].find_elements(By.CSS_SELECTOR,'[data-testid="tracklist-row"]')
        index = 0

        elements = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'[data-testid="tracklist-row"]')))
        while len(songs) < 50:
            try:
                index += 5
                songs = containers[2].find_elements(By.CSS_SELECTOR,'[data-testid="tracklist-row"]')
                driver.execute_script("arguments[0].scrollIntoView(true);",songs[index] )
                #print(len(songs))
            except Exception as err:
                print('No pudimos encontrar las 50 canciones.')
                raise Exception('No pudimos encontrar las 50 canciones.')


        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        main_container = soup.find('div',class_='main-view-container').find('div',class_='GlueDropTarget--tracks')
        songs_info = main_container.find_all('div',{'data-testid':'tracklist-row'}) #/ From webscrapping.

        playlist_from_API = spotifyAPI.get_playlist(token,playlist_id)

        top_50 = []
        total_plays = 0
        for index,song_info_tag in enumerate(songs_info):
            song_info = get_song_data(song_info_tag)
            total_plays += int(song_info['plays'])
            top_50.append(song_info)

        return {
            'name': playlist_from_API['name'],
            'country': country,
            'playlist_id': playlist_from_API['id'],
            'date': str(datetime.date.today()),
            'totalPlays' : total_plays,
            'songs': top_50 
            }
    
    except Exception as err:
        print('Ha ocurrido una excepción.')
        print(err)
        return False

def get_top_50_scrapper_and_API_info(driver:webdriver.Chrome,country:str,playlist_id:str,token:str):
    '''
    Returns an object as : 
    {   country: str,
        date: 'YYYY/MM/DD'
        totalPlays : int,
        data: [
            {song_data},
            {song_data}
        ]    
    }
    '''
    try:
        songs = []
        tries = 0
        while len(songs) < 50:
            driver.get(f'https://open.spotify.com/playlist/{playlist_id}')
            print(f'Intentos: {tries}')
            if tries > 10: break
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.contentSpacing'))) #/ Esperamos a que se carguen los elementos.
                containers = driver.find_elements(By.CSS_SELECTOR,'div.contentSpacing')
                while len(containers) < 4:
                    time.sleep(1)
                    print('Waiting')
                    containers = driver.find_elements(By.CSS_SELECTOR,'div.contentSpacing')

                songs = containers[2].find_elements(By.CSS_SELECTOR,'[data-testid="tracklist-row"]')
                index = 0
                while len(songs) < 50 and tries < 10:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,'[data-testid="tracklist-row"]')))
                    index += 1
                    songs = containers[2].find_elements(By.CSS_SELECTOR,'[data-testid="tracklist-row"]')
                    driver.execute_script("arguments[0].scrollIntoView(true);",songs[index] )
                    #print(f'Songs scrapping len(songs): {len(songs)}')
                tries += 1

            except Exception as err:
                print(f'No pudimos encontrar las 50 canciones. intento numero: {tries}')
                tries += 1 #/ si sale por los tries guardara la cantidad de canciones que haya encontrado...

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        main_container = soup.find('div',class_='main-view-container').find('div',class_='GlueDropTarget--tracks')
        songs_info = main_container.find_all('div',{'data-testid':'tracklist-row'}) #/ From webscrapping.

        playlist_from_API = spotifyAPI.get_playlist(token,playlist_id)

        top_50 = []
        total_plays = 0
    
        for index,song_info_tag in enumerate(songs_info):
            info_API = playlist_from_API['tracks']['items'][index]['track']

            song_info = get_song_data_V2(song_info_tag,info_API)
            total_plays += int(song_info['plays'])
            top_50.append(song_info)

        print(len(top_50))
        if len(top_50) < 50:
            print('Hay menos de 50 canciones')

        return {
            'name': playlist_from_API['name'],
            'country': country,
            'playlist_id': playlist_from_API['id'],
            'date': str(datetime.date.today()),
            'totalPlays' : total_plays,
            'songs_qty': len(top_50),
            'data': top_50 
            }
    
    except Exception as err:
        print('Ha ocurrido una excepción.')
        print(err)
        return False

def get_artist_top_info(playlist_info:dict[str|dict]):
    print('get_artist_top_info()') 
    artists_data = {}
    for song_info in playlist_info['data']:
        for artist_info in song_info['artists']:
            id = artist_info['artist_id']
            if id in artists_data.keys(): #/ Ya hay una entrada para este artista. sumamos info!
                artists_data[id]['songs'].append({
                    'name':song_info['name'],
                    'song_id':song_info['song_id'],
                    'plays':song_info['plays'],
                    'popularity':song_info['popularity'],
                    'ranking':song_info['ranking']
                })
                artists_data[id]['totalPlays'] = artists_data[id]['totalPlays']+song_info['plays']
                artists_data[id]['songsQty'] = len(artists_data[id]['songs']) 
            else:
                artists_data[id] = {
                    'songs':[{
                        'name':song_info['name'],
                        'song_id':song_info['song_id'],
                        'plays':song_info['plays'],
                        'popularity':song_info['popularity'],
                        'ranking':song_info['ranking']
                        }],
                    'name': artist_info['name'],
                    'totalPlays': song_info['plays'],
                    'artist_id': artist_info['artist_id'],
                    'songsQty' : 1,
                    }  
    return {
        'date':playlist_info['date'],
        'country':playlist_info['country'],
        'artist_qty': len(list(artists_data.values())),
        'artist': artists_data
    }

class IsoJsonEncoder(json.JSONEncoder):
    '''
    Clase para poder guardar los JSON files con caracteres latinos como ñ o acentos ó á é
    '''
    def encode(self, obj):
        encoded = super().encode(obj)
        return encoded.encode('ISO-8859-1').decode('ISO-8859-1')
    
playlists = {
    'Argentina':'37i9dQZEVXbMMy2roB9myp',
    'Chile':'37i9dQZEVXbL0GavIqMTeb',
    'Colombia':'37i9dQZEVXbOa2lmxNORXQ',
    'España':'37i9dQZEVXbNFJfN1Vw8d9',
    'Global':'37i9dQZEVXbMDoHDwVN2tF',
    'República Dominicana': '37i9dQZEVXbKAbrMR8uuf7',
    'Ecuador': '37i9dQZEVXbJlM6nvL1nD1',
    'México': '37i9dQZEVXbO3qyFxbkOE1',
    'Perú': '37i9dQZEVXbJfdy5b0KP7W'
    }

client_id = credentials.CLIENT_ID
client_secret = credentials.CLIENT_SECRET

token = spotifyAPI.get_token(client_id,client_secret)

service = Service('./chromedriver.exe')
options = Options()
#options.add_argument('--headless') # Set the browser in headless mode
driver = webdriver.Chrome(service=service,options=options)

start = time.time()
for key,playlist_id in playlists.items():
    print(key,playlist_id)
    playlist_info = False
    while not playlist_info:
        playlist_info = get_top_50_scrapper_and_API_info(driver,key,playlist_id,token)
    #/ Saving top50 data info
    file_name = f"../test/TOP50_{key}_{datetime.date.today()}.json"
    with codecs.open(file_name, "w", encoding = 'UTF-8') as outfile:
        json.dump(playlist_info, outfile, indent=2, cls=IsoJsonEncoder, ensure_ascii=False)
    print(f'saved at {file_name}')
    #/ Saving artist top50 info
    artists_data = get_artist_top_info(playlist_info)
    artists_file_name = f"../test/Artists_TOP50_{key}_{datetime.date.today()}.json"
    with codecs.open(artists_file_name, "w", encoding = 'UTF-8') as outfile:
        json.dump(artists_data, outfile, indent=2, cls=IsoJsonEncoder, ensure_ascii=False)
    print(f'saved at {artists_file_name}')

print(f'Tiempo transcurrido: {int((time.time()-start)/60):02}:{int((time.time()-start)%60):02}')
