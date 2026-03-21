import sys
import xbmcgui
import xbmcplugin
import urllib.parse

# Premenné pre Kodi
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def main_menu():
    # Slovenské TV
    sk_item = xbmcgui.ListItem(label="Slovenské TV")
    sk_url = BASE_URL + "?action=list_sk"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=sk_url, listitem=sk_item, isFolder=True)
    
    # České TV
    cz_item = xbmcgui.ListItem(label="České TV")
    cz_url = BASE_URL + "?action=list_cz"
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=cz_url, listitem=cz_item, isFolder=False)
    
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    # Tvoj funkčný M3U8 odkaz na JOJ
    joj_m3u8 = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"
    
    # Pridanie hlavičiek, ktoré server JOJ nutne vyžaduje (inak sa nespustí)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    referer = "https://www.joj.sk/"
    full_url = joj_m3u8 + "|User-Agent=" + user_agent + "&Referer=" + referer
    
    # Vytvorenie položky TV JOJ
    joj_item = xbmcgui.ListItem(label="TV JOJ")
    
    # Logo z tvojho odkazu
    joj_logo = "https://upload.wikimedia.org/wikipedia/commons/e/ee/Logo_TV_JOJ_-_2020.svg"
    joj_item.setArt({'icon': joj_logo, 'thumb': joj_logo})
    
    # Nastavenie vlastností pre prehrávač
    joj_item.setInfo('video', {'title': 'TV JOJ'})
    joj_item.setProperty('IsPlayable', 'true')
    
    # Vynútenie InputStream Adaptive (pre stabilný m3u8)
    joj_item.setProperty('inputstream', 'inputstream.adaptive')
    joj_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
    
    xbmcplugin.addDirectoryItem(handle=HANDLE, url=full_url, listitem=joj_item, isFolder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def show_cz_msg():
    # Okno, ktoré sa zobrazí po kliknutí na České TV
    dialog = xbmcgui.Dialog()
    dialog.ok("TV Free", "Pripravujeme čoskoro!")

# --- ROUTER (Logika prepínania) ---
query = sys.argv[2][1:]
params = dict(urllib.parse.parse_qsl(query))
action = params.get('action')

if action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    show_cz_msg()
else:
    main_menu()
    
