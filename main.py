import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Nastavenia doplnku
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def create_item(label, action, icon=None, is_folder=True):
    """Vytvorí položku v menu."""
    url = f"{BASE_URL}?action={action}"
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def add_video_item(label, stream_url, icon=None):
    """Vytvorí video kanál, ktorý povie Kodi, ako ho prehrať."""
    # Kódovanie odkazu pre router
    url = f"{BASE_URL}?action=play&url={urllib.parse.quote_plus(stream_url)}"
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    list_item.setInfo('video', {'title': label})
    list_item.setProperty('IsPlayable', 'true')
    
    # Toto povie Kodi: "Použi InputStream Adaptive pre tento m3u8"
    list_item.setProperty('inputstream', 'inputstream.adaptive')
    list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=False)

def main_menu():
    create_item("Slovenské TV", "list_sk", is_folder=True)
    create_item("České TV", "list_cz", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    # Hlavičky pre server JOJ
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Safari/537.36"
    headers = f"|User-Agent={ua}&Referer=https://www.joj.sk/&Origin=https://www.joj.sk"

    # 1. TV JOJ
    joj_url = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8" + headers
    joj_logo = "https://upload.wikimedia.org/wikipedia/commons/e/ee/Logo_TV_JOJ_-_2020.svg"
    add_video_item("TV JOJ", joj_url, joj_logo)

    # 2. JOJ KRIMI
    krimi_url = "https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8" + headers
    krimi_logo = "https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png"
    add_video_item("JOJ Krimi", krimi_url, krimi_logo)

    xbmcplugin.endOfDirectory(HANDLE)

def play_stream(url):
    """Funkcia, ktorá fyzicky spustí prehrávanie v Kodi."""
    list_item = xbmcgui.ListItem(path=url)
    list_item.setProperty('inputstream', 'inputstream.adaptive')
    list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    # Toto potvrdí Kodi, že odkaz je pripravený na štart
    xbmcplugin.setResolvedUrl(HANDLE, True, list_item)

def show_cz_msg():
    xbmcgui.Dialog().ok("TV Free", "Pripravujeme čoskoro!")

# --- ROUTER ---
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    show_cz_msg()
elif action == 'play':
    play_stream(params.get('url'))
else:
    main_menu()
    
