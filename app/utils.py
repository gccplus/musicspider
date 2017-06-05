import requests

def get_availalbe_proxy():
    while True:
        url = 'http://api.ip.data5u.com/api/get.shtml?order=fdf986b1d0dfcbc98b72155d2d41826a&num=10&area=%E4%B8%AD%E5%9B%BD&carrier=2&protocol=0&an1=1&an2=2&an3=3&sp1=1&sort=1&system=1&distinct=0&rettype=1&seprator=,'
        r = requests.get(url)
        for proxy in r.text.split(','):
            proxies = {"http": proxy, "https": proxy}
            try:
                requests.get('http://music.163.com/', proxies=proxies, timeout=1)
            except requests.Timeout:
                print 'timeout:' + proxy
            except requests.ConnectionError:
                print 'connection:' + proxy
            else:
                print proxies
                return proxies
