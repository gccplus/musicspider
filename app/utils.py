# coding:utf-8
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
            except requests.RequestException:
                print 'request error:' + proxy
            else:
                print proxies
                return proxies

class TrieNode(object):
    def __init__(self):
        """
        Initialize your data structure here.
        """
        self.data = {}
        self.is_word = False


class Trie(object):
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """
        Inserts a word into the trie.
        :type word: str
        :rtype: void
        """
        node = self.root
        for letter in word:
            child = node.data.get(letter)
            if not child:
                node.data[letter] = TrieNode()
            node = node.data[letter]
        node.is_word = True

    def search(self, word):
        """
        Returns if the word is in the trie.
        :type word: str
        :rtype: bool
        """
        node = self.root
        for letter in word:
            node = node.data.get(letter)
            if not node:
                return False
        return node.is_word  # 判断单词是否是完整的存在在trie树中