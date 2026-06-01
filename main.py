import sys
import os
import urllib.parse
import urllib.request
import gzip
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
import time
import re
from datetime import datetime, timezone, timedelta

# --- Configuration (Kodi Engine) ---
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

ADDON_DATA_PATH = xbmcvfs.translatePath("special://profile/addon_data/plugin.video.tv_free/")
if not xbmcvfs.exists(ADDON_DATA_PATH):
    xbmcvfs.mkdir(ADDON_DATA_PATH)

LOCAL_XML_PATH = os.path.join(ADDON_DATA_PATH, "epg-cz.xml")

# PRESNÁ MAPA: Spája tvoje tvg-id s ID kanálmi priamo z XML súboru epg-cz.xml.gz
MAP_EPG = {
    "JOJ.sk": "joj.cz",
    "JOJPlus.sk": "jojplus.cz",
    "JojKrimi.sk": "jojkrimi.cz",
    "JOJ24.sk": "joj24.cz",
    "JOJSport.sk": "jojsport.cz",
    "JOJSport2.sk": "jojsport2.cz",
    "Jojko.sk": "jojko.cz",
    "JOJFamily.sk": "jojfamily.cz",
    "JOJCinema.sk": "jojcinema.cz",
    "PrimaPlus.cz": "primask.cz",
    "CSHistory.cz": "cshistory.cz",
    "CSFilm.cz": "csfilm.cz",
    "CSMystery.cz": "csmystery.cz",
    "PrimaLove.cz": "primalove.cz",
    "TVLux.sk": "tvlux.cz",
    "TVLiptov.sk": "tvliptov.cz",
    "TVNitrička.sk": "tvnitricka.cz",
    "TV9.sk": "tv9.cz",
    "TV8.sk": "tv8.cz",
    "Senzi.sk": "senzi.cz",
    "FlowTV.sk": "flowtv.cz",
    "Minimax.cz": "minimax.cz",
    "Ocko.cz": "ocko.cz",
    "CT24.cz": "ct24.cz",
    "CTSport.cz": "ctsport.cz"
}

def download_and_save_xml():
    """Stiahne .gz súbor, rozbalí ho a uloží na disk pre okamžité načítanie."""
    url = "https://iptv-epg.org/files/epg-cz.xml.gz"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as response:
            with gzip.GzipFile(fileobj=response) as uncompressed:
                xml_content = uncompressed.read().decode('utf-8', errors='ignore')
                if xml_content and "<programme" in xml_content:
                    with open(LOCAL_XML_PATH, "w", encoding="utf-8") as f:
                        f.write(xml_content)
                    return True
    except Exception:
        pass
    return False

def parse_xmltv_timestamp(date_str):
    try:
        date_str = date_str.strip()
        match = re.match(r'^(\d{14})\s+([+-]\d{4})$', date_str)
        if match:
            time_part = match.group(1)
            zone_part = match.group(2)
            dt = datetime.strptime(time_part, "%Y%m%d%H%M%S")
            sign = 1 if zone_part[0] == '+' else -1
            hours = int(zone_part[1:3])
            minutes = int(zone_part[3:5])
            xml_tz = timezone(timedelta(hours=sign*hours, minutes=sign*minutes))
            return dt.replace(tzinfo=xml_tz).timestamp()
        elif len(date_str) >= 14:
            dt = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
            return dt.replace(tzinfo=timezone.utc).timestamp()
    except Exception:
        pass
    return None

def get_current_epg_dict():
    """Načíta XML z disku a bleskovo vybere programy pre aktuálny čas."""
    if not os.path.exists(LOCAL_XML_PATH):
        download_and_save_xml()
        
    current_epg = {}
    
    if os.path.exists(LOCAL_XML_PATH):
        try:
            with open(LOCAL_XML_PATH, "r", encoding="utf-8") as f:
                xml_data = f.read()
                
            if xml_data:
                now_ts = datetime.now(timezone.utc).timestamp()
                pattern = r'<programme start="([^"]*)" stop="([^"]*)" channel="([^"]*)">.*?<title[^>]*>(.*?)</title>'
                matches = re.findall(pattern, xml_data, re.DOTALL)
                
                for start_str, stop_str, channel_id, title in matches:
                    start_ts = parse_xmltv_timestamp(start_str)
                    stop_ts = parse_xmltv_timestamp(stop_str)
                    
                    if start_ts and stop_ts and (start_ts <= now_ts < stop_ts):
                        clean_title = title.strip()
                        start_time = time.strftime("%H:%M", time.localtime(start_ts))
                        end_time = time.strftime("%H:%M", time.localtime(stop_ts))
                        # Ukladáme ID kanála malými písmenami pre presnú zhodu
                        current_epg[channel_id.lower().strip()] = f"({start_time} - {end_time}) {clean_title}"
        except Exception:
            pass

    # Kontrola na pozadí: Ak je súbor starší ako 2 hodiny, stiahne nový pre ďalšie spustenie
    if os.path.exists(LOCAL_XML_PATH):
        file_age = time.time() - os.path.getmtime(LOCAL_XML_PATH)
        if file_age > 7200:
            download_and_save_xml()

    return current_epg

def add_directory_item(label, action, icon=None, is_folder=True, video_url=None, tvg_id="", epg_dict=None):
    query = {'action': action}
    if video_url:
        query['url'] = video_url
        query['title'] = label
        
    url = f"{BASE_URL}?{urllib.parse.urlencode(query)}"
    display_label = label
    plot_info = f"Živé vysielanie stanice {label}."
    
    if not is_folder:
        current_program = None
        # Zistíme, aké ID má kanál priradené v našej mape pre XML
        if epg_dict and tvg_id in MAP_EPG:
            target_xml_id = MAP_EPG[tvg_id].lower()
            if target_xml_id in epg_dict:
                current_program = epg_dict[target_xml_id]
        
        if current_program:
            display_label = f"{label}  |  {current_program}"
            plot_info = f"Práve beží:\n{current_program}"
        else:
            display_label = f"{label}  |  Živé vysielanie"

    list_item = xbmcgui.ListItem(label=display_label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': display_label, 'plot': plot_info})
        list_item.setProperty('tvg-id', tvg_id)
        list_item.setProperty('tvg-logo', icon)

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

# --- DATA STATIONS ---
CHANNELS_SK = [
    ("TV JOJ", "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj", "JOJ.sk", "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"),
    ("JOJ Plus", "https://i.ibb.co/21Xx2nnd/joj-plus.png", "JOJPlus.sk", "https://live.cdn.joj.sk/live/andromeda/plus-1080.m3u8"),
    ("JOJ KRIMI", "https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png", "JofKrimi.sk", "https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8"),
    ("JOJ 24", "https://img.joj.sk/38a52c95-84ce-4c04-b70a-2289a9fd1541", "JOJ24.sk", "https://live.cdn.joj.sk/live/andromeda/joj_news-1080.m3u8"),
    ("JOJ Šport", "https://img.joj.sk/rx660n/662097da-11c1-434a-a923-3e00cdcb81e7", "JOJSport.sk", "https://live.cdn.joj.sk/live/andromeda/joj_sport-1080.m3u8"),
    ("JOJ Šport 2", "https://static.hnonline.sk/images/slike/2025/12/04/o_4878486_1024.png", "JOJSport2.sk", "https://live.cdn.joj.sk/live/andromeda/joj_sport2-1080.m3u8"),
    ("Jojko", "https://i.ibb.co/TxFWhc1J/jojko.png", "Jojko.sk", "https://live.cdn.joj.sk/live/andromeda/jojko-1080.m3u8"),
    ("JOJ Family", "https://i.ibb.co/hJgjKqpF/joj-family.png", "JOJFamily.sk", "https://live.cdn.joj.sk/live/andromeda/family-1080.m3u8"),
    ("JOJ Cinema", "http://www.mediaguru.cz/wp-content/uploads/2016/06/Joj-Cinema_akt.png", "JOJSinema.sk", "https://live.cdn.joj.sk/live/andromeda/cinema-1080.m3u8"),
    ("Prima SK", "https://www.jojgroup.sk/wp-content/uploads/Prima_Plus_Logo_2021.svg.png", "PrimaPlus.cz", "http://88.212.15.19/live/prima_avc_25p/playlist.m3u8"),
    ("CS History", "https://img.joj.sk/418430b1-b598-40d1-8552-39b473c73836", "CSHistory.cz", "https://live.cdn.joj.sk/live/andromeda/cs_history-1080.m3u8"),
    ("CS Film", "https://staticeu.sweet.tv/images/cache/channel_icons/BCTQOIAK/935-cs-film-hd.png", "CSFilm.cz", "https://live.cdn.joj.sk/live/andromeda/cs_film-1080.m3u8"),
    ("CS Mystery", "https://www.jojgroup.sk/wp-content/uploads/CS-mistery.png", "CSMystery.cz", "https://live.cdn.joj.sk/live/andromeda/cs_mystery-1080.m3u8"),
    ("Prima Love", "https://www.recenzer.cz/wp-content/uploads/2023/10/prima-love-logo.jpg", "PrimaLove.cz", "http://88.212.15.19/live/prima_love_avc_25p/playlist.m3u8"),
    ("TV LUX", "https://213.sk/wp-content/uploads/2020/11/tvlux.jpg", "TVLux.sk", "https://stream.tvlux.sk/luxtv/luxtv-livestream/playlist.m3u8"),
    ("TV Liptov", "https://yt3.googleusercontent.com/JJ6maA0dhvLU3z45Jhbgcc1brVZQswuPfYS6Da-Gli4MxXEPlhz5yuLkJlp7VL7mG7eSIxBORA=s900-c-k-c0x00ffffff-no-rj", "TVLiptov.sk", "http://95.105.255.137:1935/tvturiec/tvliptov.stream/playlist.m3u8"),
    ("TV Nitrička", "https://www.satelitnatv.sk/wp-content/uploads/2013/04/nitricka.jpg", "TVNitrička.sk", "https://dash4.antik.sk/live/test_nitricka/playlist.m3u8"),
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
    m3u_path = os.path.join(ADDON_DATA_PATH, "playlist.m3u")
    try:
        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            all_channels = CHANNELS_SK + CHANNELS_CZ
            for name, logo, tid, url in all_channels:
                f.write(f'#EXTINF:-1 tvg-id="{tid}" tvg-name="{name}" tvg-logo="{logo}",{name}\n{url}\n')
        xbmcgui.Dialog().ok("PVR Playlist", f"M3U Playlist úspešne vytvorený!\nCesta: {m3u_path}")
    except Exception as e:
        xbmcgui.Dialog().error("Chyba", f"Zlyhalo generovanie playlistu: {str(e)}")

def show_main_menu():
    add_directory_item("Slovenské TV", "list_sk", is_folder=True)
    add_directory_item("České TV", "list_cz", is_folder=True)
    add_directory_item("Vygenerovať M3U Playlist pre IPTV Simple", "set_pvr_playlist", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_channels():
    xbmcplugin.setContent(HANDLE, 'files')
    epg_dict = get_current_epg_dict()
    for name, logo, tid, url in CHANNELS_SK:
        add_directory_item(name, "play", icon=logo, is_folder=False, video_url=url, tvg_id=tid, epg_dict=epg_dict)
    xbmcplugin.endOfDirectory(HANDLE)

def list_czech_channels():
    xbmcplugin.setContent(HANDLE, 'files')
    epg_dict = get_current_epg_dict()
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
    
    if action == 'list_sk':
        list_slovak_channels()
    elif action == 'list_cz':
        list_czech_channels()
    elif action == 'play':
        play_video(params.get('url'), params.get('title'))
    elif action == 'set_pvr_playlist':
        generate_pvr_playlist()
    else:
        show_main_menu()

