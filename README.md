# musicspider
网易云音乐爬虫
基本思路是先爬取所有artist
根据artist爬取album
根据album爬取song_id

最后根据这个api http://music.163.com/api/song/detail/?id=186016&ids=[186016] 获取歌曲、专辑以及评论信息

api的加密算法参考https://www.zhihu.com/question/36081767/answer/140287795 下@平胸小仙女 的回答
