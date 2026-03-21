import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Globálne premenné
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def create_item(label, url, is_folder=False, icon=None, playable=False):
    """Pomocná funkcia na vytvorenie položky v Kodi menu."""
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if playable:
        list_item.setProperty('IsPlayable', 'true')
        # Povieme Kodi, že ide o video stream
        list_item.setInfo('video', {'title': label})
        # Vynútime použitie InputStream Adaptive pre stabilitu m3u8
        list_item.setProperty('inputstream', 'inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    """Hlavné menu: Slovenské a České TV."""
    create_item("Slovenské TV", f"{BASE_URL}?action=list_sk", is_folder=True)
    create_item("České TV", f"{BASE_URL}?action=list_cz", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    """Zoznam slovenských staníc."""
    # TV JOJ - tvoj overený m3u8
    joj_m3u8 = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"
    
    # OPRAVA PREHRÁVANIA: Pridanie User-Agenta a overenia (bez toho server JOJ spojenie ukončí)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    full_url = f"{joj_m3u8}|User-Agent={user_agent}&Referer=https://www.joj.sk/"
    
    # Logo z tvojho odkazu
    joj_logo = "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj"
    
    create_item("TV JOJ", full_url, is_folder=False, icon=joj_logo, playable=True)
    xbmcplugin.endOfDirectory(HANDLE)

def show_cz_announcement():
    """Oprava pre České TV: Zobrazenie oznámenia."""
    dialog = xbmcgui.Dialog()
    dialog.ok("TV Free", "Pripravujeme čoskoro!")
    # Po odkliknutí "OK" vrátime používateľa do hlavného menu
    main_menu()

# --- SMEROVANIE (ROUTER) ---
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    show_cz_announcement()
else:
    main_menu()
    
