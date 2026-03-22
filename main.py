import sys
import urllib.parse
import xbmcgui
import xbmcplugin

# --- Configuration (Kodi Engine) ---
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

def add_directory_item(label, action, icon=None, is_folder=True, video_url=None):
    """Vytvorí položku v menu Kodi. Názvy sú po slovensky."""
    query = {'action': action}
    if video_url:
        query['url'] = video_url
        query['title'] = label
        
    url = f"{BASE_URL}?{urllib.parse.urlencode(query)}"
    list_item = xbmcgui.ListItem(label=label)
    
    if icon:
        list_item.setArt({'icon': icon, 'thumb': icon})
    
    if not is_folder:
        list_item.setProperty('IsPlayable', 'true')
        list_item.setInfo('video', {'title': label})

    xbmcplugin.addDirectoryItem(handle=HANDLE, url=url, listitem=list_item, isFolder=is_folder)

def show_main_menu():
    """Hlavné menu doplnku."""
    add_directory_item("Slovenské TV", "list_sk", is_folder=True)
    add_directory_item("České TV", "list_cz", is_folder=False)
    xbmcplugin.endOfDirectory(HANDLE)

def list_slovak_channels():
    """Zoznam slovenských staníc vrátane Jojko."""
    # TV JOJ
    joj_url = "https://live.cdn.joj.sk/live/andromeda/joj-1080.m3u8"
    joj_logo = "https://yt3.googleusercontent.com/8rPXBoj2l1nhd9C-DCXF-s3tx0i_36GJzJcxeMyYvyPpPNakQsyc5DYc5d_QLDeI74ILkmFSJQ=s900-c-k-c0x00ffffff-no-rj"
    add_directory_item("TV JOJ", "play", icon=joj_logo, is_folder=False, video_url=joj_url)

    # JOJ PLUS
    plus_url = "https://live.cdn.joj.sk/live/andromeda/plus-1080.m3u8"
    plus_logo = "https://i.ibb.co/21Xx2nnd/joj-plus.png"
    add_directory_item("JOJ Plus", "play", icon=plus_logo, is_folder=False, video_url=plus_url)

    # JOJ KRIMI
    krimi_url = "https://live.cdn.joj.sk/live/andromeda/wau-1080.m3u8"
    krimi_logo = "https://img.telkac.zoznam.sk/data/images/channel/2026/03/04/image_new_137.thumb.png"
    add_directory_item("JOJ Krimi", "play", icon=krimi_logo, is_folder=False, video_url=krimi_url)

    # JOJ 24
    joj24_url = "https://live.cdn.joj.sk/live/andromeda/joj_news-1080.m3u8"
    joj24_logo = "https://img.joj.sk/38a52c95-84ce-4c04-b70a-2289a9fd1541"
    add_directory_item("JOJ 24", "play", icon=joj24_logo, is_folder=False, video_url=joj24_url)

    # JOJ ŠPORT
    jojsport_url = "https://live.cdn.joj.sk/live/andromeda/joj_sport-1080.m3u8"
    jojsport_logo = "https://img.joj.sk/rx660n/662097da-11c1-434a-a923-3e00cdcb81e7"
    add_directory_item("JOJ Šport", "play", icon=jojsport_logo, is_folder=False, video_url=jojsport_url)

    # JOJKO - Nová stanica
    jojko_url = "https://live.cdn.joj.sk/live/andromeda/jojko-1080.m3u8"
    jojko_logo = "https://i.ibb.co/TxFWhc1J/jojko.png"
    add_directory_item("Jojko", "play", icon=jojko_logo, is_folder=False, video_url=jojko_url)

    # SENZI TV
    senzi_url = "https://lb.streaming.sk/senzi/stream/playlist.m3u8"
    senzi_logo = "https://static.wikia.nocookie.net/cstv/images/8/85/Senzi.png"
    add_directory_item("Senzi TV", "play", icon=senzi_logo, is_folder=False, video_url=senzi_url)

    xbmcplugin.endOfDirectory(HANDLE)

def play_video(stream_url, title):
    """Spustí video so simuláciou prehliadača Chrome."""
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    referer = "https://www.joj.sk/"
    
    # Formát pre základný prehrávač Kodi
    final_url = f"{stream_url}|User-Agent={urllib.parse.quote(user_agent)}&Referer={urllib.parse.quote(referer)}"
    
    list_item = xbmcgui.ListItem(path=final_url)
    list_item.setInfo('video', {'title': title})
    
    xbmcplugin.setResolvedUrl(HANDLE, True, list_item)

def show_czech_notice():
    """Dialog pre České TV."""
    xbmcgui.Dialog().ok("TV Free", "Pripravujeme Čoskoro")

# --- Router ---
if __name__ == '__main__':
    params = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
    action = params.get('action')

    if action == 'list_sk':
        list_slovak_channels()
    elif action == 'list_cz':
        show_czech_notice()
    elif action == 'play':
        play_video(params.get('url'), params.get('title'))
    else:
        show_main_menu()
        
