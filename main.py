import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Globálne premenné
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def create_item(label, url, is_folder=False, icon=None, is_playable=False):
    """Vytvorí položku v zozname Kodi s vynúteným prehrávaním pre streamy."""
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if is_playable:
        list_item.setProperty('IsPlayable', 'true')
        # Nastavenie informácií o videu
        list_item.setInfo('video', {'title': label})
        
        # HLAVNÁ OPRAVA: Povieme Kodi, že toto je adaptívny stream (m3u8)
        list_item.setProperty('inputstream', 'inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setProperty('inputstream.adaptive.m3u8_max_bw', '20000000')

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    """Hlavná ponuka: Slovenské a České TV."""
    create_item("Slovenské TV", f"{BASE_URL}?action=list_sk", is_folder=True)
    create_item("České TV", f"{BASE_URL}?action=list_cz", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    """Zoznam slovenských staníc so všetkými logami."""
    # Spoločné hlavičky (User-Agent a Referer sú povinné)
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    headers = f"|User-Agent={ua}&Referer=https://www.joj.sk/"

    # 1. TV JOJ
    joj_url = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8" + headers
    joj_logo = "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj"
    create_item("TV JOJ", joj_url, is_folder=False, icon=joj_logo, is_playable=True)

    # 2. JOJ KRIMI
    krimi_url = "https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8" + headers
    krimi_logo = "https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png"
    create_item("JOJ Krimi", krimi_url, is_folder=False, icon=krimi_logo, is_playable=True)

    xbmcplugin.endOfDirectory(HANDLE)

def show_cz_msg():
    """Oznámenie pre České TV."""
    xbmcgui.Dialog().ok("TV Free", "Pripravujeme čoskoro!")

# --- ROUTER (Spracovanie kliknutia) ---
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    show_cz_msg()
else:
    main_menu()
    
