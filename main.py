import sys
import xbmcgui
import xbmcplugin
import urllib.parse

# Premenné pre Kodi
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def main_menu():
    """Hlavné menu: Slovenské a České TV."""
    # Slovenské TV
    sk_item = xbmcgui.ListItem(label="Slovenské TV")
    sk_url = f"{BASE_URL}?action=list_sk"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=sk_url, listitem=sk_item, isFolder=True)
    
    # České TV
    cz_item = xbmcgui.ListItem(label="České TV")
    cz_url = f"{BASE_URL}?action=list_cz"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=cz_url, listitem=cz_item, isFolder=False)
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    """Zoznam slovenských staníc."""
    # Spoločné hlavičky (User-Agent je nutnosť pre servery JOJ)
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    headers = f"|User-Agent={ua}&Referer=https://www.joj.sk/"

    # 1. TV JOJ
    joj_url = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8" + headers
    joj_logo = "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj" # Logo z YouTube profilu
    add_stream("TV JOJ", joj_url, joj_logo)

    # 2. JOJ KRIMI
    krimi_url = "https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8" + headers
    krimi_logo = "https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png"
    add_stream("JOJ Krimi", krimi_url, krimi_logo)

    xbmcplugin.endOfDirectory(HANDLE)

def add_stream(name, url, logo):
    """Pomocná funkcia na pridanie streamu do zoznamu."""
    list_item = xbmcgui.ListItem(label=name)
    list_item.setArt({'icon': logo, 'thumb': logo})
    list_item.setInfo('video', {'title': name})
    list_item.setProperty('IsPlayable', 'true')
    
    # Nastavenie pre InputStream Adaptive (nutné pre HLS/m3u8)
    list_item.setProperty('inputstream', 'inputstream.adaptive')
    list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=False)

def show_cz_msg():
    """Zobrazenie oznámenia pre České TV."""
    xbmcgui.Dialog().ok("TV Free", "Pripravujeme čoskoro!")

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
    
