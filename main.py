import sys
import xbmcgui
import xbmcplugin
import urllib.parse

# Premenné pre Kodi
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def main_menu():
    """Hlavná ponuka: Slovenské a České TV."""
    # Slovenské TV (Priečinok)
    sk_item = xbmcgui.ListItem(label="Slovenské TV")
    sk_url = f"{BASE_URL}?action=list_sk"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=sk_url, listitem=sk_item, isFolder=True)
    
    # České TV (Zobrazí správu)
    cz_item = xbmcgui.ListItem(label="České TV")
    cz_url = f"{BASE_URL}?action=list_cz"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=cz_url, listitem=cz_item, isFolder=False)
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    """Zoznam slovenských staníc."""
    # TV JOJ - Tvoj M3U8 odkaz
    joj_m3u8 = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"
    
    # Tvoje LOGO z YouTube odkazu (vyčistená adresa pre Kodi)
    joj_logo = "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj"
    
    # DÔLEŽITÉ: Hlavičky pre server JOJ, aby stream nezlyhal
    headers = "|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36&Referer=https://www.joj.sk/"
    full_url = joj_m3u8 + headers
    
    # Vytvorenie položky pre TV JOJ
    joj_item = xbmcgui.ListItem(label="TV JOJ")
    joj_item.setArt({'icon': joj_logo, 'thumb': joj_logo})
    
    # Nastavenie vlastností prehrávania
    joj_item.setInfo('video', {'title': 'TV JOJ'})
    joj_item.setProperty('IsPlayable', 'true')
    
    # Vynútenie InputStream Adaptive (pre HLS streamy)
    joj_item.setProperty('inputstream', 'inputstream.adaptive')
    joj_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=full_url, listitem=joj_item, isFolder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def show_cz_msg():
    """Správa pre České TV."""
    dialog = xbmcgui.Dialog()
    dialog.ok("TV Free", "Pripravujeme čoskoro!")
    # Po odkliknutí sa vrátime do menu
    main_menu()

# --- ROUTER (Logika prepínania akcií) ---
query = sys.argv[2][1:]
params = dict(urllib.parse.parse_qsl(query))
action = params.get('action')

if action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    show_cz_msg()
else:
    main_menu()
    
