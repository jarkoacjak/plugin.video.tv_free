import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Globálne premenné pre Kodi
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def create_item(label, url, is_folder=False, icon=None, is_playable=False):
    """Pomocná funkcia na vytvorenie položky v zozname."""
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if is_playable:
        list_item.setProperty('IsPlayable', 'true')
        # Informácie pre prehrávač
        list_item.setInfo('video', {'title': label, 'mediatype': 'video'})
        
        # HLAVNÁ OPRAVA: Vynútenie InputStream Adaptive pre m3u8
        list_item.setProperty('inputstream', 'inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setProperty('inputstream.adaptive.m3u8_max_bw', '20000000')

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    """Hlavné menu doplnku."""
    create_item("Slovenské TV", f"{BASE_URL}?action=list_sk", is_folder=True)
    create_item("České TV", f"{BASE_URL}?action=list_cz", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    """Zoznam slovenských staníc."""
    # TV JOJ Stream
    joj_url = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"
    
    # Pridanie hlavičiek (User-Agent a Referer sú pre JOJ kľúčové)
    headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36&Referer=https://www.joj.sk/"
    full_url = joj_url + headers
    
    # Logo z YouTube (priamy odkaz)
    joj_logo = "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj"
    
    create_item("TV JOJ", full_url, is_folder=False, icon=joj_logo, is_playable=True)
    xbmcplugin.endOfDirectory(HANDLE)

def show_cz_announcement():
    """Upozornenie pre České TV - Opravené zobrazenie."""
    dialog = xbmcgui.Dialog()
    # Použijeme okno OK, ktoré sa musí potvrdiť, aby si ho videl
    dialog.ok("TV Free", "Pripravujeme čoskoro!")
    # Po potvrdení obnovíme hlavné menu
    main_menu()

# --- ROUTER (SMEROVANIE) ---
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    show_cz_announcement()
else:
    main_menu()
    
