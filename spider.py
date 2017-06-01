#coding=utf-8
import sys,requests,re,threading,time
import Queue
import multiprocessing
from bs4 import BeautifulSoup
from models import ArtistCategory,Artist,Album,Song,Comment,Session
baseurl = 'http://music.163.com'

lock = threading.Lock()
album_list_queue = Queue.Queue()
song_list_queue = Queue.Queue()

from Crypto.Cipher import AES
import base64
import json

# offset的取值为:(评论页数-1)*20,total第一页为true，其余页为false
# first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}' # 第一个参数
second_param = "010001" # 第二个参数
third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
forth_param = "0CoJUm6Qyw8W8jud"

# 获取参数
def get_params(page):
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    if(page == 1):
        first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        h_encText = AES_encrypt(first_param, first_key, iv)
    else:
        offset = str((page-1)*20)
        first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' %(offset,'false')
        h_encText = AES_encrypt(first_param, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText

# 获取 encSecKey
def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey

# 加密过程
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text

def get_availalbe_proxy():
    while True:
        url = 'http://api.ip.data5u.com/api/get.shtml?order=fdf986b1d0dfcbc98b72155d2d41826a&num=10&area=%E4%B8%AD%E5%9B%BD&carrier=2&protocol=0&an1=1&an2=2&an3=3&sp1=1&sort=1&system=1&distinct=0&rettype=1&seprator=,'
        r = requests.get(url)
        for proxy in r.text.split(','):
            proxies = {"http": proxy, "https": proxy}
            try:
                requests.get('http://music.163.com/', proxies=proxies, timeout=1)
            except requests.Timeout:
                print 'timeout:'+proxy
            except requests.ConnectionError:
                print 'connection:'+proxy
            else:
                print proxies
                return proxies

def get_artist_category_ids():
    url = baseurl + '/discover/artist'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    artist_category_id_list = []
    for item in soup.find_all(class_='cat-flag'):
        href = item['href']
        catname = item.string
        match = re.match('.*id=(\d{4})$',href)
        if match:
            catid = match.group(1)
            print catid,repr(catname)
            artist_category_id_list.append(catid)
            if not session.query(ArtistCategory).get(catid):
                artist_category = ArtistCategory()
                artist_category.id = catid
                artist_category.name = catname.encode('utf-8')
                session.add(artist_category)
                session.commit()
    return artist_category_id_list

def get_artist_by_category_id(artist_category_id_list):
    artist_id_list = []
    for catid in artist_category_id_list:
        for initial in range(ord('A'),ord('Z')+1):
            url = baseurl + '/discover/artist/cat?id=%s&initial=%d' % (catid,initial)
            print url
            r = requests.get(url)
            soup = BeautifulSoup(r.text,'html.parser')
            for item in soup.find_all(class_='sml'):
                #print item.a.string,item.a['href']
                match = re.match('.*id=(\d+)$',item.a['href'])
                if match:
                    artist_id = match.group(1)
                    artist_name = item.a.string
                    artist_id_list.append(artist_id)
                    if not session.query(Artist).get(artist_id):
                        artist = Artist()
                        artist.id = artist_id
                        artist.name = artist_name.encode('utf-8')
                        artist.category_id = catid
                        session.add(artist)
                        session.commit()
    return artist_id_list
def get_album_by_artist(artist_list):
    proxies = None
    album_list = []
    for artist_id in artist_list:
        url = baseurl + '/artist/album?id=%s&limit=200' % artist_id
        print url
        while True:
            try:
                r = requests.get(url,proxies=proxies)
            except requests.exceptions.RequestException:
                proxies = get_availalbe_proxy()
            else:
                if r.status_code != 200:
                    proxies = get_availalbe_proxy()
                else:
                    break
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.find_all(id='m-song-module'):
            for li in item.find_all('li'):
                #print li
                match = re.match('.*id=(\d+)$',li.find('a')['href'])
                if match:
                    id = match.group(1)
                    album_list.append(id)
                    if len(album_list) == 1000:
                        # #开启20个线程
                        thread_list = []
                        for i in range(20):
                            album_list_slice = album_list[50*i:50*(i+1)]
                            t = threading.Thread(target=get_song_by_album, args=(album_list_slice,))
                            thread_list.append(t)
                            t.start()
                        #等待线程结束后，再开启20个线程，目的是为了控制内存消耗
                        for t in thread_list:
                            t.join()
                        album_list = []
    album_count = len(album_list)
    thread_list = []
    for i in range(20):
        begin = album_count/20 * i
        end = album_count/20 * (i+1)
        album_list_slice = album_list[begin:end]
        t = threading.Thread(target=get_song_by_album, args=(album_list_slice,))
        thread_list.append(t)
        t.start()
    # 等待线程结束
    for t in thread_list:
        t.join()

def get_song_by_album(album_list):
    print 'current thread: get_song_by_album %s' % threading.current_thread().getName()
    song_list = []
    proxies = None
    for alb_id in album_list:
        url = baseurl + '/album?id=%s' % alb_id
        print 'active thread:%d %s %s %s' % (threading.active_count(),multiprocessing.current_process().name,threading.current_thread().getName(),url)
        while True:
            try:
                r = requests.get(url,proxies=proxies)
            except requests.exceptions.RequestException:
                proxies = get_availalbe_proxy()
            else:
                if r.status_code != 200:
                    proxies = get_availalbe_proxy()
                else:
                    break
        soup = BeautifulSoup(r.text, 'html.parser')
        for item in soup.find_all('a', href=re.compile('\/song\?id=\d+')):
            song_href = item['href']
            match = re.match('.*id=(\d+)$',song_href)
            if match:
                song_id = match.group(1)
                url = 'http://music.163.com/api/song/detail/?id=%s&ids=[%s]' % (song_id,song_id)
                while True:
                    try:
                        r = requests.get(url, proxies=proxies)
                    except requests.exceptions.RequestException:
                        proxies = get_availalbe_proxy()
                    else:
                        if r.status_code != 200:
                            proxies = get_availalbe_proxy()
                        else:
                            break
                json_result = json.loads(r.content)
                song_list.append(json_result)

    t = threading.Thread(target=analyse_song_page, args=(song_list,))
    t.start()
    t.join()
    print 'thread analyse_song end'

def analyse_song_page(song_list):
    global lock
    proxies = None
    db_song = []
    db_album = []
    db_comment = []
    for song in song_list:
        song_json = song['songs'][0]
        album_json = song_json['album']
        artist_json = song_json['artists'][0]

        song_id = song_json['id']
        song_name = song_json['name']
        song_duration =song_json['duration']
        artist_id = artist_json['id']
        album_id = album_json['id']
        album_name = album_json['name']
        album_size = album_json['size']
        album_cover = album_json['picUrl']
        release_time = album_json['publishTime']
        release_comp = album_json['company']

        comment_thread = song_json['commentThreadId']
        print 'active thread:%d %s %s songid:%s' % (
        threading.active_count(), multiprocessing.current_process().name, threading.current_thread().getName(), song_id)

        url = 'http://music.163.com/weapi/v1/resource/comments/' + comment_thread
        params = get_params(1)
        encSecKey = get_encSecKey()
        data = {
            "params": params,
            "encSecKey": encSecKey
        }
        while True:
            try:
                r = requests.post(url, data=data, proxies=proxies)
            except requests.exceptions.RequestException:
                proxies = get_availalbe_proxy()
            else:
                if r.status_code != 200:
                    proxies = get_availalbe_proxy()
                else:
                    break

        json_dict = json.loads(r.content)
        total = json_dict['total']

        song = Song()
        song.id = song_id
        song.name = song_name
        song.duration = song_duration
        song.album_id = album_id
        song.artist_id = artist_id
        song.comment_count = total
        db_song.append(song)

        album = Album()
        album.id = album_id
        album.alb_name = album_name
        album.alb_size = album_size
        album.alb_cover = album_cover
        album.artist_id = artist_id
        timestamp = str(release_time)
        album.release_time = time.strftime('%Y-%m-%d',time.localtime(float(timestamp[:10]+'.'+timestamp[-3:])))
        album.release_comp = release_comp
        db_album.append(album)

        hot_comments = json_dict['hotComments']
        for item in hot_comments:
            comment = Comment()
            comment.song_id = int(song_id)
            #过滤emoji表情
            try:
                highpoints = re.compile(u'[\U00010000-\U0010ffff]')
            except re.error:
                highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')

            content = highpoints.sub(u'??', item['content'])
            comment.content = content[:300]
            comment.liked_count = int(item['likedCount'])
            timestamp = str(item['time'])
            comment.timestamp = time.strftime('%Y%m%d%H%M%S',time.localtime(float(timestamp[:10]+'.'+timestamp[-3:])))
            comment.user_id = int(item['user']['userId'])
            comment.nickname = item['user']['nickname']
            db_comment.append(comment)

            session = Session()
            print session
            for song in db_song:
                try:
                    session.add(song)
                except:
                    session.rollback()
                    print 'insert song error'

            for comment in db_comment:
                session.add(comment)
            for album in db_album:
                flag = True
                for inner_album in db_album:
                    if inner_album != album and album.id == inner_album.id:
                        flag = False
                        break
                if flag:
                    session.execute(
                        Album.__table__.insert().prefix_with('IGNORE'),
                        {'id': album.id,
                         'alb_name':album.alb_name,
                         'alb_desc':'',
                         'alb_cover':album.alb_cover,
                         'alb_size':album.alb_size,
                         'artist_id':album.artist_id,
                         'release_time':album.release_time,
                         'release_comp':album.release_comp}
                    )
            session.commit()
            Session.remove()

if __name__ == "__main__":
    #artist_category_list = get_artist_category_ids()
    #artist_list = get_artist_by_category_id(artist_category_list)
    artist_list = []
    session = Session()
    for artist in session.query(Artist):
       artist_list.append(artist.id)
    Session.remove()
    album_process_count = 10
    print album_process_count
    album_process_list = []
    artist_count = len(artist_list)
    for i in range(album_process_count):
        begin = artist_count/album_process_count * i
        end = artist_count/album_process_count * (i+1)
        artist_list_slice = artist_list[begin:end]
        p = multiprocessing.Process(target=get_album_by_artist, args=(artist_list_slice,))
        album_process_list.append(p)
        p.start()

    #等待进程结束
    for p in album_process_list:
        p.join()



