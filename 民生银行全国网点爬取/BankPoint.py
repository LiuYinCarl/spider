import requests
import json


class BankPoint(object):
    def __init__(self):
        with open('BankPoint.json', 'r') as f:
            self.conf = json.load(f)

        self.city_json = self.conf['city_json']
        self.area_json = self.conf['area_json']
        self.headers = self.conf['headers']
        self.session = requests.session()

    def get_json(self, cities):
        url = 'http://www.cmbc.com.cn/channelApp/ajax/QueryBranchBank'
        for city in cities:
            for i in range(1, 2):  # some cities have two page bank
                self.city_json['request']['body']['cityno'] = city
                self.city_json['request']['body']['page'] = i
                response = self.session.post(url, headers=self.headers, data=json.dumps(self.city_json))
                try:
                    if response.status_code == 200:
                        json_data = response.json()
                        print("this is json data")
                        print(json_data)
                        return json_data
                except Exception as e:
                    print("get_json error: ", e.args)

    def get_data(self):
        # get all cities of the area
        url = 'http://www.cmbc.com.cn/channelApp/ajax/QueryArea2'
        for area in range(110000, 650000, 10000):
            self.area_json['request']['body']['parNo'] = area
            try:
                response = self.session.post(url, headers=self.headers, data=json.dumps(self.area_json))
                if response.status_code == 200:
                    # print(response.content, 'gb2312')
                    print(str(response.content, 'utf-8'))
                    cities = []
                    jsons = json.loads(response.content)['returnData']
                    for city in jsons:
                        cities.append(city['areano'])
                    self.get_json(cities)
            except Exception as e:
                print("get data error:", e.args)

    def save_data(self):
        pass


if __name__ == '__main__':
    spider = BankPoint()
    spider.get_data()
