import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Základné informácie o doplnku
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def create_item(label, url, is_folder=False, icon=None):
    """Pomocná funkcia na vytvorenie položky v zozname."""
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    """Hlavná ponuka: Slovenské vs České TV."""
    # Vytvoríme odkazy pre podmenu
    sk_url = f"{BASE_URL}?action=list_sk"
    cz_url = f"{BASE_URL}?action=list_cz"
    
    create_item("Slovenské TV", sk_url, is_folder=True)
    create_item("České TV", cz_url, is_folder=True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    """Zoznam slovenských staníc."""
    joj_stream = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"
    joj_logo = "https://upload.wikimedia.org/wikipedia/commons/e/ee/Logo_TV_JOJ_-_2020.svg"
    
    create_item("TV JOJ", joj_stream, is_folder=False, icon=joj_logo)
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_czech_tv():
    """Zoznam českých staníc (zatiaľ prázdny)."""
    # Tu môžeš neskôr pridať české stanice podobne ako JOJ
    xbmcplugin.endOfDirectory(HANDLE)

# Smerovanie (Router)
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if not action:
    main_menu()
elif action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    list_czech_tv()

