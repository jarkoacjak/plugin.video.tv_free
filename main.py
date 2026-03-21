import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Základné nastavenia doplnku
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def create_item(label, url, is_folder=False, icon=None):
    """Pomocná funkcia na vytvorenie položky v zozname Kodi."""
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': label})
        
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def main_menu():
    """Hlavná ponuka s výberom krajiny."""
    sk_url = f"{BASE_URL}?action=list_sk"
    cz_url = f"{BASE_URL}?action=list_cz"
    
    create_item("Slovenské TV", sk_url, is_folder=True)
    create_item("České TV", cz_url, is_folder=True)
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    """Zoznam slovenských staníc - Pridaná TV JOJ."""
    # User-Agent je dôležitý, aby stream v Kodi nabehol
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    joj_stream = f"https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8|User-Agent={user_agent}"
    
    # Tvoje nové logo z odkazu
    joj_logo = "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj"
    
    create_item("TV JOJ", joj_stream, is_folder=False, icon=joj_logo)
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_czech_tv():
    """Funkcia pre České TV s upozornením o príprave."""
    dialog = xbmcgui.Dialog()
    dialog.notification('TV Free', 'Pripravujeme, pribudnú čoskoro!', xbmcgui.NOTIFICATION_INFO, 5000)
    
    # Ukončíme adresár bez pridania položiek
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=False)

# Smerovanie požiadaviek podľa kliknutia používateľa
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if not action:
    main_menu()
elif action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    list_cz_tv() # Volanie funkcie pre české TV s oznamom
