import sys
import os
import urllib.parse
import urllib.request
import gzip
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import json
import time
import re
import xml.etree.ElementTree as ET

# --- Configuration (Kodi Engine) ---
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

ADDON_DATA_PATH = xbmcvfs.translatePath("special://profile/addon_data/plugin.video.tv_free/")
if not xbmcvfs.exists(ADDON_DATA_PATH):
    xbmcvfs.mkdir(ADDON_DATA_PATH)

def check_iptv_simple_client():
    """Skontroluje, či je PVR IPTV Simple Client nainštalovaný a povolený."""
    try:
        query = {
            "jsonrpc": "2.0",
            "method": "Addons.GetAddonDetails",
            "params": {"addonid": "pvr.iptvsimple", "properties": ["enabled"]},
            "id": 1
        }
        response = xbmc.executeJSONRPC(json.dumps(query))
        result = json.loads(response)
        
        if "result" in result and "addon" in result["result"]:
            addon_details = result["result"]["addon"]
            if addon_details.get("enabled"):
                return True
            else:
                xbmcgui.Dialog().ok("Upozornenie", "PVR IPTV Simple Client máš nainštalovaný, ale je zakázaný.\nProsím, povoľ ho v nastaveniach doplnkov Kodi.")
                return False
        else:
            xbmcgui.Dialog().ok("Chýba PVR Klient", "Na sledovanie cez TV sprievodcu potrebuješ mať nainštalovaný doplnok:\n\n-> PVR IPTV Simple Client <-\n\nNájdeš ho v Kodi repozitári medzi PVR klientmi.")
            return False
    except Exception:
        return True

def clean_name(name):
    """Zjednoduší názov stanice pre presné porovnanie."""
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r'\.sk|\.cz|tv|hd|sk|cz|\s+|-|_', '', name)
    return name

def get_pvr_epg_path():
    """Zistí nastavenú cestu k XMLTV súboru priamo z nastavení IPTV Simple Clienta."""
    try:
        # Prečítame settings súbor klienta priamo z Kodi profilu
        settings_path = xbmcvfs.translatePath("special://profile/addon_data/pvr.iptvsimple/settings.xml")
        if xbmcvfs.exists(settings_path):
            with xbmcvfs.File(settings_path, 'r') as f:
                xml_text = f.read()
                # Vyhľadáme nastavenie pre XMLTV cestu (epgUrl alebo epgPath)
                url_match = re.search(r'id="epgUrl"[^>]*>(.*?)<', xml_text)
                if url_match and url_match.group(1):
                    return url_match.group(1)
                
                path_match = re.search(r'id="epgPath"[^>]*>(.*?)<', xml_text)
                if path_match and path_match.group(1):
                    return path_match.group(1)
    except:
        pass
    return None

def get_xmltv_epg():
    """Načíta a spracuje lokálne alebo sieťové EPG z nastavení PVR klienta."""
    epg_dict = {}
    epg_source = get_pvr_epg_path()
    
    if not epg_source:
        return epg_dict

    try:
        xml_content = ""
        # Ak ide o internetovú adresu, stiahneme ju
        if epg_source.startswith("http://") or epg_source.startswith("https://"):
            req = urllib.request.Request(epg_source, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                if epg_source.endswith(".gz"):
                    with gzip.GzipFile(fileobj=response) as uncompressed:
                        xml_content = uncompressed.read().decode('utf-8', errors='ignore')
                else:
                    xml_content = response.read().decode('utf-8', errors='ignore')
        else:
            # Ak ide o lokálny súbor v zariadení
            local_path = xbmcvfs.translatePath(epg_source)
            if xbmcvfs.exists(local_path):
                with xbmcvfs.File(local_path, 'r') as f:
                    if local_path.endswith(".gz"):
                        # Ošetrenie lokálneho gzip súboru v Kodi prostredí
                        import io
                        raw_data = f.read()
                        with gzip.GzipFile(fileobj=io.BytesIO(raw_data.encode('utf-8', errors='ignore'))) as uncompressed:
                            xml_content = uncompressed.read().decode('utf-8', errors='ignore')
                    else:
                        xml_content = f.read()

        if xml_content:
            now_utc = time.gmtime(time.time())
            now_str = time.strftime("%Y%m%d%H%M%S", now_utc)
            
            # Robustný Regex na postupné vyťahovanie programov bez pádu na veľkých súboroch
            pattern = r'<programme start="(\d+)[^"]*" stop="(\d+)[^"]*" channel="([^"]*)">.*?<title[^>]*>(.*?)</title>'
            matches = re.findall(pattern, xml_content, re.DOTALL)
            
            for start, stop, channel_id, title in matches:
                if start <= now_str <= stop:
                    clean_ch = clean_name(channel_id)
                    try:
                        # Vytiahneme len hodiny a minúty pre čistý zoznam
                        start_time = f"{start[8:10]}:{start[10:12]}"
                        end_time = f"{stop[8:10]}:{stop[10:12]}"
                    except:
                        start_time, end_time = "??:??", "??:??"
                        
                    epg_dict[clean_ch] = f"({start_time} - {end_time}) {title.strip()}"
    except Exception as e:
        xbmc.log(f"[TV Free] Chyba pri spracovaní PVR EPG: {str(e)}", xbmc.LOGERROR)
    return epg_dict

def add_directory_item(label, action, icon=None, is_folder=True, video_url=None, tvg_id="", epg_dict=None):
    """Vytvorí položku a automaticky spáruje EPG podľa XMLTV dát."""
    query = {'action': action}
    if video_url:
        query['url'] = video_url
        query['title'] = label
        
    url = f"{BASE_URL}?{urllib.parse.urlencode(query)}"
    display_label = label
    plot_info = "Živé vysielanie."
    
    if not is_folder and epg_dict:
        clean_label = clean_name(label)
        clean_tid = clean_name(tvg_id)
        
        # Hľadáme zhodu v našom očistenom slovníku programu
        current_program = epg_dict.get(clean_label) or epg_dict.get(clean_tid)
        
        if current_program:
            display_label = f"{label}  |  {current_program}"
            plot_info = f"Práve beží:\n{current_program}"

    list_item = xbmcgui.ListItem(label=display_label)
    
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {
            'title': display_label,
            'plot': plot_info,
        })
        list_item.setProperty('tvg-id', tvg_id)
        list_item.setProperty('tvg-logo', icon)

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

# --- ZOZNAMY STANÍC ---
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

def generate_pvr_playlist():
    if not check_iptv_simple_client():
        return
    m3u_path = os.path.join(ADDON_DATA_PATH, "playlist.m3u")
    try:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            all_channels = CHANNELS_SK + CHANNELS_CZ
            for name, logo, tid, url in all_channels:
                f.write(f'#EXTINF:-1 tvg-id="{tid}" tvg-name="{name}" tvg-logo="{logo}",{name}\n{url}\n')
        xbmcgui.Dialog().ok("PVR Playlist", f"Playlist úspešne vytvorený!\nCesta: {m3u_path}")
    except Exception as e:
        xbmcgui.Dialog().error("Chyba", f"Zlyhalo generovanie: {str(e)}")

def show_main_menu():
    add_directory_item("Živé vysielania", "live_menu", is_folder=True)
    add_directory_item("Nastaviť playlist do PVR IPTV Simple Client priamo z pluginu", "set_pvr_playlist", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def show_live_menu():
    add_directory_item("Slovenské TV", "list_sk", is_folder=True)
    add_directory_item("České TV", "list_cz", is_folder=True)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_channels():
    xbmcplugin.setContent(HANDLE, 'files')
    epg_dict = get_xmltv_epg() # Načíta program z tvojho lokálneho/nastaveného PVR odkazu
    for name, logo, tid, url in CHANNELS_SK:
        add_directory_item(name, "play", icon=logo, is_folder=False, video_url=url, tvg_id=tid, epg_dict=epg_dict)
    xbmcplugin.endOfDirectory(HANDLE)

def list_czech_channels():
    xbmcplugin.setContent(HANDLE, 'files')
    epg_dict = get_xmltv_epg()
    for name, logo, tid, url in CHANNELS_CZ:
        add_directory_item(name, "play", icon=logo, is_folder=False, video_url=url, tvg_id=tid, epg_dict=epg_dict)
    xbmcplugin.endOfDirectory(HANDLE)

def play_video(stream_url, title):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    referer = "https://www.joj.sk/"
    final_url = f"{stream_url}|User-Agent={urllib.parse.quote(user_agent)}&Referer={urllib.parse.quote(referer)}"
    list_item = xbmcgui.ListItem(path=final_url)
    list_item.setInfo('video', {'title': title})
    xbmcplugin.setResolvedUrl(HANDLE, True, list_item)

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
    else:
        show_main_menu()
    
