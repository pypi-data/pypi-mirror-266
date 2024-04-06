import cloudscraper

class NitrotypeNews:
    def __init__(self):
        self._scraper = cloudscraper.create_scraper()
        self._news_data = self._get_news_data()
        self._initialize_attributes()

    def _get_news_data(self):
        data = self._scraper.get("https://www.nitrotype.com/api/v2/news").json()
        latest_news = data['results'][0] if 'results' in data else {}
        return latest_news

    def _initialize_attributes(self):
        news_data = self._news_data
        self.news_blog_id = news_data.get('blogID')
        self.news_slug = news_data.get('slug')
        self.news_title = news_data.get('title')
        self.news_created_stamp = news_data.get('createdStamp')
        self.news_last_modified = news_data.get('lastModified')
        self.news_written_by = news_data.get('writtenBy')
        self.news_short_body = news_data.get('shortBody')