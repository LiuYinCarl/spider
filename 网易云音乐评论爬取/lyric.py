from Crypto.Cipher import AES
import base64
import requests
import json
import time


class GetComments(object):
    def __init__(self):
        # 构造请求头
        self.headers = {
            'Referer': 'http://music.163.com/',
            'Host': 'music.163.com',
            'Accept-Language': "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            'Accept-Encoding':"gzip, deflate",
            'Content-Type': "application/x-www-form-urlencoded",
            'Origin': 'https://music.163.com',
            'Connection': "keep-alive",
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        # 构造会话
        self.session = requests.session()
        # 设置代理
        self.proxies = {
            # 'http': 'http://183.62.22.220:3128',
            # 'http': 'http://118.190.95.35:9001',
            # 'http': 'http://61.135.217.7:80',
            # 'http': 'http://106.75.9.39:8080',
            # 'http': 'http://118.190.95.43:9001',
            # 'http': 'http://121.31.157.94:8123',
            # 'http': 'http://115.46.67.248:8123',
            # 'http': 'http://182.88.14.243:8123'
        }

    # 获取请求参数 params
    def get_params(self, page):
        # 参数1 R_SO_4_加上歌曲的id(rid, 可不写) 确定偏移量(offset) 获取评论的种类(total) 每次获取评论数目(limit)
        # 参数2 还不知道干嘛的
        second_param = "010001"
        # 参数3
        third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876" \
                      "aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05" \
                      "c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289d" \
                      "c6935b3ece0462db0a22b8e7"
        # 参数4
        forth_param = "0CoJUm6Qyw8W8jud"
        # 密钥偏移量
        iv = "0102030405060708"

        first_key = forth_param
        second_key = 16 * 'F'
        if page == 1:
            first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        else:
            first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' % (str((page - 1) * 20), 'false')
        # 一次加密
        h_encText = self.aes_encrypt(first_param, first_key, iv)
        # 二次加密
        h_encText = self.aes_encrypt(h_encText, second_key, iv)
        return h_encText

    # 获取请求参数 encSecKey
    def get_encSecKey(self):
        encSecKey = 'bfe760d35bd3b347f31f32b0df73185278d0d9fa3319a743686ebb47f30dd1cc87ad093bcbdfd021d540db18f7614b587' \
                    '9d8c17ce2835bad300ceb6b4945020513d237a32e105e1c67fe0cafcef66820196bb6acb86a239c454fe53ca089fc5f67' \
                    'fcf262094970f07894b0734bdf32d945c42af40d9e01adf46b54693515017b'
        return encSecKey

    # AES 加密
    def aes_encrypt(self, text, key, iv):
        """
        :param text: 要加密的数据
        :param key: 加密的key
        :param iv: 密钥偏移量
        :return: 加密后的数据
        """
        pad = 16 - len(text) % 16

        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        encrypt_text = str(encrypt_text, encoding="utf-8")
        return encrypt_text

    # 请求json数据
    def get_json(self, url, params, encSecKey):
        """
        :param url: 请求链接
        :param params: 请求参数 params
        :param encSecKey: 请求参数 encSecKey
        :return: 返回的数据
        """
        data = {
            "params": params,
            "encSecKey": encSecKey
        }
        response = self.session.post(url, headers=self.headers, data=data)
        return response

    # 得到全部评论
    def get_all_comments(self, url):
        """
        :param url: 请求链接
        """
        params = self.get_params(1)
        encSecKey = self.get_encSecKey()
        print(params)
        print(encSecKey)
        json_text = self.get_json(url, params, encSecKey)
        print(json_text)
        json_dict = json.loads(json_text.content)
        comments_num = int(json_dict['total'])  # 获取评论总数目
        if not comments_num % 20:
            page = comments_num / 20
        else:
            page = int(comments_num / 20) + 1
        print("共有%d页评论!" % page)

        for i in range(page):  # 逐页抓取
            comments_list = []
            params = self.get_params(i + 1)
            encSecKey = self.get_encSecKey()
            json_text = self.get_json(url, params, encSecKey)
            json_dict = json.loads(json_text)

            for item in json_dict['comments']:
                comment = item['content']  # 评论内容
                liked_count = item['likedCount']  # 点赞总数
                comment_info = liked_count + " " + comment + "\n"
                comments_list.append(comment_info)
            self.save_to_file(comments_list)
            print("第%d页抓取完毕!" % (i + 1))

    # 将数据保存到文件
    def save_to_file(self, comments_list):
        with open('comments.txt', 'a') as f:
            f.write(comments_list)


if __name__ == '__main__':
    spider = GetComments()
    url = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_1296558163?csrf_token="
    spider.get_all_comments(url)
