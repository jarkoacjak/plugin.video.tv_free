import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# --- Configuration (Kodi Engine) ---
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def add_directory_item(label, action, icon=None, is_folder=True, video_url=None):
    """Vytvorí položku v menu Kodi."""
    query = {'action': action}
    if video_url:
        query['url'] = video_url
        query['title'] = label
        
    url = f"{BASE_URL}?{urllib.parse.urlencode(query)}"
    list_item = xbmcgui.ListItem(label=label)
    
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': label})

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

# --- MENU STRUKTÚRA ---

def show_main_menu():
    """Hlavné menu doplnku."""
    add_directory_item("Živé vysielania", "live_menu", is_folder=True)
    # Položky z tvojho obrázka:
    add_directory_item("Nastaviť playlist do PVR IPTV Simple Client priamo z pluginu", "set_pvr_playlist", is_folder=False)
    add_directory_item("Nastaviť generované epg do PVR IPTV Simple Client", "set_pvr_epg", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def show_live_menu():
    """Menu pod Živými vysielaniami."""
    add_directory_item("Slovenské TV", "list_sk", is_folder=True)
    add_directory_item("České TV", "list_cz", is_folder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_channels():
    """Zoznam slovenských staníc."""
    add_directory_item("TV JOJ", "play", icon="https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8")
    add_directory_item("JOJ Plus", "play", icon="https://i.ibb.co/21Xx2nnd/joj-plus.png", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/plus-1080.m3u8")
    add_directory_item("JOJ KRIMI", "play", icon="https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8")
    add_directory_item("JOJ 24", "play", icon="https://img.joj.sk/38a52c95-84ce-4c04-b70a-2289a9fd1541", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/joj_news-1080.m3u8")
    add_directory_item("JOJ Šport", "play", icon="https://img.joj.sk/rx660n/662097da-11c1-434a-a923-3e00cdcb81e7", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/joj_sport-1080.m3u8")
    add_directory_item("Jojko", "play", icon="https://i.ibb.co/TxFWhc1J/jojko.png", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/jojko-1080.m3u8")
    add_directory_item("JOJ Family", "play", icon="https://i.ibb.co/hJgjKqpF/joj-family.png", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/family-1080.m3u8")
    add_directory_item("JOJ Cinema", "play", icon="http://www.mediaguru.cz/wp-content/uploads/2016/06/Joj-Cinema_akt.png", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/cinema-1080.m3u8")
    add_directory_item("CS History", "play", icon="https://img.joj.sk/418430b1-b598-40d1-8552-39b473c73836", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/cs_history-1080.m3u8")
    add_directory_item("CS Film", "play", icon="https://staticeu.sweet.tv/images/cache/channel_icons/BCTQOIAK/935-cs-film-hd.png", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/cs_film-1080.m3u8")
    add_directory_item("CS Mystery", "play", icon="https://www.jojgroup.sk/wp-content/uploads/CS-mistery.png", is_folder=False, video_url="https://live.cdn.joj.sk/live/andromeda/cs_mystery-1080.m3u8")
    add_directory_item("Prima Love", "play", icon="https://www.recenzer.cz/wp-content/uploads/2023/10/prima-love-logo.jpg", is_folder=False, video_url="http://88.212.15.19/live/prima_love_avc_25p/playlist.m3u8")
    add_directory_item("TV LUX", "play", icon="https://213.sk/wp-content/uploads/2020/11/tvlux.jpg", is_folder=False, video_url="https://stream.tvlux.sk/luxtv/luxtv-livestream/playlist.m3u8")
    add_directory_item("TV Liptov", "play", icon="https://yt3.googleusercontent.com/JJ6maA0dhvLU3z45Jhbgcc1brVZQswuPfYS6Da-Gli4MxXEPlhz5yuLkJlp7VL7mG7eSIxBORA=s900-c-k-c0x00ffffff-no-rj", is_folder=False, video_url="http://95.105.255.137:1935/tvturiec/tvliptov.stream/playlist.m3u8")
    add_directory_item("TV Nitrička", "play", icon="https://www.satelitnatv.sk/wp-content/uploads/2013/04/nitricka.jpg", is_folder=False, video_url="https://dash4.antik.sk/live/test_nitricka/playlist.m3u8")
    add_directory_item("TV9", "play", icon="https://www.fotelka.tv/image/cache/catalog/Regionalne/TV9-240x234.jpg", is_folder=False, video_url="https://dash4.antik.sk/live/test_tv9/playlist.m3u8")
    add_directory_item("TV 8", "play", icon="https://www.digislovakia.sk/wp-content/uploads/2023/04/TV8-logo-2-300x231.png", is_folder=False, video_url="http://109.74.145.11:1935/tv8/ngrp:tv8.stream_all/playlist.m3u8")
    add_directory_item("Senzi TV", "play", icon="https://static.wikia.nocookie.net/cstv/images/8/85/Senzi.png", is_folder=False, video_url="https://lb.streaming.sk/senzi/stream/playlist.m3u8")
    xbmcplugin.endOfDirectory(HANDLE)

def list_czech_channels():
    """Zoznam českých staníc."""
    add_directory_item("Minimax", "play", icon="https://www.minimaxcz.tv/storage/images/cWiGhWyxj8fFnyWQZxEX.png", is_folder=False, video_url="http://88.212.15.19/live/test_minimax/playlist.m3u8")
    add_directory_item("Óčko", "play", icon="https://parasite.cz/wp-content/uploads/2013/02/ocko1.jpg", is_folder=False, video_url="https://ocko-live-dash.ssl.cdn.cra.cz/cra_live2/ocko.stream.1.smil/playlist.m3u8")
    add_directory_item("ČT 24", "play", icon="https://pecka.tv/wp-content/uploads/2025/12/studio-ct24-400x600.jpg", is_folder=False, video_url="https://dash2.antik.sk/live/ct24_avc_25p/playlist.m3u8")
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(stream_url, title):
    """Spustí video."""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    referer = "https://www.joj.sk/"
    final_url = f"{stream_url}|User-Agent={urllib.parse.quote(user_agent)}&Referer={urllib.parse.quote(referer)}"
    list_item = xbmcgui.ListItem(path=final_url)
    list_item.setInfo('video', {'title': title})
    xbmcplugin.setResolvedUrl(HANDLE, True, list_item)

# --- Router ---
if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    action = params.get('action')
    if action == 'live_menu':
        show_live_menu()
    elif action == 'list_sk':
        list_slovak_channels()
    elif action == 'list_cz':
        list_czech_channels()
    elif action == 'play':
        play_video(params.get('url'), params.get('title'))
    elif action in ['set_pvr_playlist', 'set_pvr_epg']:
        xbmcgui.Dialog().notification('PVR', 'Funkcia sa pripravuje...', xbmcgui.NOTIFICATION_INFO, 5000)
    else:
        show_main_menu()
        
