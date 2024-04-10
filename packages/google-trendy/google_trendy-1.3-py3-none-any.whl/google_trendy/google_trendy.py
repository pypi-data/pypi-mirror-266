import json
import requests 
from datetime import datetime
import bs4 as bs

explore_url = "https://trends.google.com/trends/explore?q=/m/02bh_v&date=now+7-d&geo=US"
search_url = "https://trends.google.com/trends/api/realtimetrends?hl=en-US&tz=300&cat=all&fi=0&fs=0&geo=US&ri=10&rs=10&sort=0"
daily_trend_url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"

class RealtimeTrend():
    def __init__(self, id, trend_data):
        self.id = id 
        self.title = trend_data['title']
        self.explore_links = ["https://trends.google.com" + link for link in trend_data['entityExploreLinks']]
        self.entities = trend_data['entityNames']
        self.time_range = trend_data['timeRange']
        self.articles = self.get_articles(trend_data)

        self.timeseries_data = self.get_bar_data(trend_data)

    def start_date(self):
        return datetime.fromtimestamp(self.timeseries_data['start']).strftime("%A, %B %d, %Y %I:%M %p")
    
    def end_date(self):
        return datetime.fromtimestamp(self.timeseries_data['end']).strftime("%A, %B %d, %Y %I:%M %p")
    
    def get_articles(self, data):
        articles = []
        if 'articles' in data['widgets'][0]:
            for article in data['widgets'][0]['articles']:
                articles.append(Article(article))
        
        return articles
    def get_bar_data(self, data):
        num_articles = 0
        start_time = None
        end_time = None
        if 'barData' in data['widgets'][1]:
            bar_data = data['widgets'][1]['barData']
            num_articles = bar_data[-1]['accumulative']
            start_time = bar_data[0]['startTime']
            end_time = bar_data[-1]['startTime']
        return {"article_count": num_articles, "start":start_time, "end":end_time}

    def __str__(self):
        return f"Trend({self.id},[ {self.title} ],{self.time_range},{self.entities},{self.timeseries_data},{self.explore_links},{self.articles})"
    def __repr__(self):
        return f"Trend({self.id},{self.title},{self.time_range},{self.entities},{self.timeseries_data},{self.explore_links},{self.articles})"
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)

class Article():
    def __init__(self, data):
        self.title = data['title']
        self.url = data['url']
        self.source = data['source']

    def __str__(self):
        return f"Article({self.title}, {self.source}, {self.url})"
    def __repr__(self):
        return f"Article({self.title}, {self.source}, {self.url})"
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)
'''
Daily Google Search Trend
'''
class DailyTrend:
    def __init__(self, title, traffic, desc=None, link=None):
        self.title = title
        self.desc = desc
        self.link = link
        self.traffic = int(traffic.strip("+").replace(",",""))
    
    def __str__(self):
        return f"DailyTrend(title={self.title}, traffic={self.traffic:,}, link={self.link})"
    def __repr__(self):
        return f"DailyTrend(title={self.title}, traffic={self.traffic:,}, link={self.link})"

'''
Google Trends class - used to get realtime and daily search trends
'''
class GoogleTrends():
    def __init__(self):
        self.decoder = json.JSONDecoder()
        self.trends = []
        self.trend_ids = []
        self.entities = set([])

    def trend_url(self, id):
        return f"https://trends.google.com/trends/api/stories/{id}?hl=en-US&tz=300"

    def _jsonify(self, data):
        data = data.split('\n')[1]
        json_data = self.decoder.decode(data)
        return json_data

    def _request(self, url, err_msg="ERROR"):
        res = requests.get(url)
        if res.status_code != 200:
            raise(RuntimeError(f"[ {err_msg} ] - Code {res.status_code}"))
        
        data = res.content.decode()
        json_data = self._jsonify(data)
        return json_data

    def get_trends(self, num):
        json_data = self._request(f"https://trends.google.com/trends/api/realtimetrends?hl=en-US&tz=300&cat=all&fi=0&fs=0&geo=US&ri={num}&rs={num}&sort=0", "ERROR initiating trend search")
        self.trends = []
        # This only grabs top stories? Doesn't include the full 'num' requested
        # for trend in json_data['storySummaries']['trendingStories']:
        #     self.trends.append(self.get_trend(trend['id']))
        self.trend_ids = json_data['trendingStoryIds']
        for trend_id in self.trend_ids:
            trend = self.get_trend(trend_id)
            self.trends.append(trend)
            self.entities = self.entities.union(set(trend.entities))
        
        self.trends.sort(key=lambda x: x.timeseries_data['article_count'], reverse=True)
        
    def get_trend(self, id):
        json_data = self._request(self.trend_url(id), f"ERROR getting trend {id}")
        return RealtimeTrend(id, json_data)


    def daily_trends(self):
        res = requests.get(daily_trend_url)
        if (res.status_code != 200):
            raise RuntimeError("ERROR getting daily trends from Google")
        
        soup = bs.BeautifulSoup(res.content, "xml")
        items = soup.find_all('item')
        searches = []
        for item in items:
            searches.append(DailyTrend(item.find('title').text, item.find('ht:approx_traffic').text, link=item.find("link").text))

        searches.sort(key=lambda x: x.traffic, reverse=True)
        return searches
    