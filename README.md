# musicspider
网易云音乐爬虫
基本思路是先爬取所有artist，根据artist爬取album，根据album爬取song_id

根据 http://music.163.com/api/song/detail/?id=186016&ids=[186016] 这个api 获取歌曲以及专辑信息

根据 http://music.163.com/weapi/v1/resource/comments/R_SO_4_186016 获取歌曲评论

后者的参数需要加密，加密算法参考https://www.zhihu.com/question/36081767/answer/140287795 下@平胸小仙女 的回答
