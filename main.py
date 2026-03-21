import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# Nastavenia Kodi
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def create_item(label, url, icon=None, folder=False, playable=False):
    list_item = xbmcgui.ListItem(label=label)
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if playable:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': label})
        # AKTIVÁCIA PREHRÁVAČA (Toto je kľúčové pre m3u8)
        list_item.setProperty('inputstream', 'inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setProperty('inputstream.adaptive.m3u8_max_bw', '20000000')

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=folder)

def main_menu():
    create_item("Slovenské TV", f"{BASE_URL}?action=list_sk", folder=True)
    create_item("České TV", f"{BASE_URL}?action=list_cz", folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_tv():
    # HLAVA: Kompletná sada hlavičiek pre JOJ (bez nich to zlyhá)
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    headers = f"|User-Agent={ua}&Referer=https://www.joj.sk/&Origin=https://www.joj.sk&Connection=keep-alive"

    # TV JOJ
    joj_url = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8" + headers
    joj_logo = "https://upload.wikimedia.org/wikipedia/commons/e/ee/Logo_TV_JOJ_-_2020.svg"
    create_item("TV JOJ", joj_url, icon=joj_logo, playable=True)

    # JOJ KRIMI
    krimi_url = "https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8" + headers
    krimi_logo = "https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png"
    create_item("JOJ Krimi", krimi_url, icon=krimi_logo, playable=True)

    xbmcplugin.endOfDirectory(HANDLE)

def show_cz_msg():
    xbmcgui.Dialog().ok("TV Free", "Pripravujeme čoskoro!")

# ROUTER
params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
action = params.get('action')

if action == 'list_sk':
    list_slovak_tv()
elif action == 'list_cz':
    show_cz_msg()
else:
    main_menu()
    
