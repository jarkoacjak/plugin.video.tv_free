import sys
import os
import urllib.parse
import datetime
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs

# --- Configuration (Kodi Engine) ---
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

# Cesta k dátam doplnku tv_free, kam uložíme vygenerovaný playlist a epg
ADDON_DATA_PATH = xbmcvfs.translatePath("special://profile/addon_data/plugin.video.tv_free/")

if not xbmcvfs.exists(ADDON_DATA_PATH):
    xbmcvfs.mkdir(ADDON_DATA_PATH)

def add_directory_item(label, action, icon=None, is_folder=True, video_url=None, tvg_id=""):
    """Vytvorí položku v menu Kodi a priradí jej EPG značku."""
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
        list_item.setProperty('tvg-id', tvg_id)
        list_item.setProperty('tvg-logo', icon)

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

# --- ZOZNAMY STANÍC (Meno, Ikona, EPG ID, Stream URL) ---
CHANNELS_SK = [
    ("TV JOJ", "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj", "JOJ.sk", "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"),
    ("JOJ Plus", "https://i.ibb.co/21Xx2nnd/joj-plus.png", "JOJPlus.sk", "https://live.cdn.joj.sk/live/andromeda/plus-1080.m3u8"),
    ("JOJ KRIMI", "https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png", "JOJKrimi.sk", "https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8"),
    ("JOJ 24", "https://img.joj.sk/38a52c95-84ce-4c04-b70a-2289a9fd1541", "JOJ24.sk", "https://live.cdn.joj.sk/live/andromeda/joj_news-1080.m3u8"),
    ("JOJ Šport", "https://img.joj.sk/rx660n/662097da-11c1-434a-a923-3e00cdcb81e7", "JOJSport.sk", "https://live.cdn.joj.sk/live/andromeda/joj_sport-1080.m3u8"),
    ("JOJ Šport 2", "https://static.hnonline.sk/images/slike/2025/12/04/o_4878486_1024.png", "JOJSport2.sk", "https://live.cdn.joj.sk/live/andromeda/joj_sport2-1080.m3u8"),
    ("Jojko", "https://i.ibb.co/TxFWhc1J/jojko.png", "Jojko.sk", "https://live.cdn.joj.sk/live/andromeda/jojko-1080.m3u8"),
    ("JOJ Family", "https://i.ibb.co/hJgjKqpF/joj-family.png", "JOJFamily.sk", "https://live.cdn.joj.sk/live/andromeda/family-1080.m3u8"),
    ("JOJ Cinema", "http://www.mediaguru.cz/wp-content/uploads/2016/06/Joj-Cinema_akt.png", "JOJCinema.sk", "https://live.cdn.joj.sk/live/andromeda/cinema-1080.m3u8"),
    ("CS History", "https://img.joj.sk/418430b1-b598-40d1-8552-39b473c73836", "CSHistory.cz", "https://live.cdn.joj.sk/live/andromeda/cs_history-1080.m3u8"),
    ("CS Film", "https://staticeu.sweet.tv/images/cache/channel_icons/BCTQOIAK/935-cs-film-hd.png", "CSFilm.cz", "https://live.cdn.joj.sk/live/andromeda/cs_film-1080.m3u8"),
    ("CS Mystery", "https://www.jojgroup.sk/wp-content/uploads/CS-mistery.png", "CSMystery.cz", "https://live.cdn.joj.sk/live/andromeda/cs_mystery-1080.m3u8"),
    ("Prima Love", "https://www.recenzer.cz/wp-content/uploads/2023/10/prima-love-logo.jpg", "PrimaLove.cz", "http://88.212.15.19/live/prima_love_avc_25p/playlist.m3u8"),
    ("TV LUX", "https://213.sk/wp-content/uploads/2020/11/tvlux.jpg", "TVLux.sk", "https://stream.tvlux.sk/luxtv/luxtv-livestream/playlist.m3u8"),
    ("TV Liptov", "https://yt3.googleusercontent.com/JJ6maA0dhvLU3z45Jhbgcc1brVZQswuPfYS6Da-Gli4MxXEPlhz5yuLkJlp7VL7mG7eSIxBORA=s900-c-k-c0x00ffffff-no-rj", "TVLiptov.sk", "http://95.105.255.137:1935/tvturiec/tvliptov.stream/playlist.m3u8"),
    ("TV Nitrička", "https://www.satelitnatv.sk/wp-content/uploads/2013/04/nitricka.jpg", "TVNitricka.sk", "https://dash4.antik.sk/live/test_nitricka/playlist.m3u8"),
    ("TV9", "https://www.fotelka.tv/image/cache/catalog/Regionalne/TV9-240x234.jpg", "TV9.sk", "https://dash4.antik.sk/live/test_tv9/playlist.m3u8"),
    ("TV 8", "https://www.digislovakia.sk/wp-content/uploads/2023/04/TV8-logo-2-300x231.png", "TV8.sk", "http://109.74.145.11:1935/tv8/ngrp:tv8.stream_all/playlist.m3u8"),
    ("Senzi TV", "https://static.wikia.nocookie.net/cstv/images/8/85/Senzi.png", "Senzi.sk", "https://lb.streaming.sk/senzi/stream/playlist.m3u8"),
    ("Flow TV", "https://www.flowtv.sk/wp-content/uploads/2021/04/logo_flow_tv_web.png", "FlowTV.sk", "https://app.viloud.tv/hls/channel/04e456809c83928443e59f0a2fce8610.m3u8")
]

CHANNELS_CZ = [
    ("Minimax", "https://www.minimaxcz.tv/storage/images/cWiGhWyxj8fFnyWQZxEX.png", "Minimax.cz", "http://88.212.15.19/live/test_minimax/playlist.m3u8"),
    ("Óčko", "https://parasite.cz/wp-content/uploads/2013/02/ocko1.jpg", "Ocko.cz", "https://ocko-live-dash.ssl.cdn.cra.cz/cra_live2/ocko.stream.1.smil/playlist.m3u8"),
    ("ČT 24", "https://pecka.tv/wp-content/uploads/2025/12/studio-ct24-400x600.jpg", "CT24.cz", "https://dash2.antik.sk/live/ct24_avc_25p/playlist.m3u8"),
    ("ČT Sport", "https://www.itelka.sk/wp-content/uploads/2023/04/ct-sport.png", "CTSport.cz", "http://88.212.15.19/live/test_ctsport_25p/playlist.m3u8")
]

# --- GENERÁTORY PRE PVR KLIENTA ---

def generate_pvr_playlist():
    """Vygeneruje .m3u súbor s lokálnou cestou pre IPTV Simple Client."""
    m3u_path = os.path.join(ADDON_DATA_PATH, "playlist.m3u")
    try:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            all_channels = CHANNELS_SK + CHANNELS_CZ
            for name, logo, tid, url in all_channels:
                f.write(f'#EXTINF:-1 tvg-id="{tid}" tvg-logo="{logo}",{name}\n{url}\n')
        xbmcgui.Dialog().ok("PVR Playlist", f"Playlist vytvorený!\nCesta: {m3u_path}")
    except Exception as e:
        xbmcgui.Dialog().error("Chyba", str(e))

def generate_pvr_epg():
    """Generuje epg.xml priamo v doplnku a plní ho automatickým časovým programom."""
    epg_path = os.path.join(ADDON_DATA_PATH, "epg.xml")
    try:
        now = datetime.datetime.now()
        start_time = now.strftime("%Y%m%d000000 +0200")
        stop_time = (now + datetime.timedelta(days=1)).strftime("%Y%m%d235900 +0200")
        
        all_channels = CHANNELS_SK + CHANNELS_CZ
        
        with open(epg_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n')
            
            # Zapísanie kanálov
            for name, _, tid, _ in all_channels:
                f.write(f'  <channel id="{tid}"><display-name>{name}</display-name></channel>\n')
            
            # Zapísanie automatických programov (aby IPTV klient videl, dokedy bežia)
            for name, _, tid, _ in all_channels:
                f.write(f'  <programme start="{start_time}" stop="{stop_time}" channel="{tid}">\n')
                f.write(f'    <title>{name} - Živé vysielanie</title>\n')
                f.write(f'    <desc>Práve sledujete živé vysielanie stanice {name}.</desc>\n')
                f.write('  </programme>\n')
                
            f.write('</tv>\n')
            
        xbmcgui.Dialog().ok("PVR EPG", f"EPG sprievodca bol vygenerovaný!\nCesta: {epg_path}\n\nTeraz túto cestu nastav v IPTV Simple Clientovi.")
    except Exception as e:
        xbmcgui.Dialog().error("Chyba EPG", str(e))

# --- MENU STRUKTÚRA ---

def show_main_menu():
    """Hlavné menu doplnku."""
    add_directory_item("Živé vysielania", "live_menu", is_folder=True)
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
    for name, logo, tid, url in CHANNELS_SK:
        add_directory_item(name, "play", icon=logo, is_folder=False, video_url=url, tvg_id=tid)
    xbmcplugin.endOfDirectory(HANDLE)

def list_czech_channels():
    """Zoznam českých staníc."""
    for name, logo, tid, url in CHANNELS_CZ:
        add_directory_item(name, "play", icon=logo, is_folder=False, video_url=url, tvg_id=tid)
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
    elif action == 'set_pvr_playlist':
        generate_pvr_playlist()
    elif action == 'set_pvr_epg':
        generate_pvr_epg()
    else:
        show_main_menu()
        
