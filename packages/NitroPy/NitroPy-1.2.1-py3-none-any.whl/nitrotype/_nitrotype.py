import cloudscraper
from bs4 import BeautifulSoup
import json
import re

__all__ = [
    "NitrotypeRacer"
]


class NitrotypeRacer:
    def __init__(self, username):
        self.username = username
        self._scraper = cloudscraper.create_scraper()
        self._racer_info = self._get_user_info()
        self._initialize_attributes()

    def _get_user_info(self):
        response = self._scraper.get(f'https://www.nitrotype.com/racer/{self.username}').text
        soup = BeautifulSoup(response, 'html.parser')

        racer_info = {}
        for script in soup.find_all('script'):
            if 'RACER_INFO' in str(script):
                racer_info = json.loads(re.findall('{".+}', str(script))[0])
                return racer_info

        return None
        

    def _initialize_attributes(self):
        # Initialize attributes
        racer_info = self._racer_info
        self.userID = racer_info['userID']
        self.username = racer_info['username']
        self.membership = racer_info['membership']
        self.displayName = racer_info['displayName']
        self.title = racer_info['title']
        self.experience = racer_info['experience']
        self.level = racer_info['level']
        self.teamID = racer_info['teamID']
        self.lookingForTeam = racer_info['lookingForTeam']
        self.carID = racer_info['carID']
        self.carHueAngle = racer_info['carHueAngle']
        self.totalCars = len(racer_info['garage'])
        self.nitros = racer_info['nitros']
        self.nitrosUsed = racer_info['nitrosUsed']
        self.racesPlayed = racer_info['racesPlayed']
        self.longestSession = racer_info['longestSession']
        self.avgSpeed = racer_info['avgSpeed']
        self.highestSpeed = racer_info['highestSpeed']
        self.allowFriendRequests = racer_info['allowFriendRequests']
        self.profileViews = racer_info['profileViews']
        self.createdStamp = racer_info['createdStamp']
        self.tag = racer_info['tag']
        self.tagColor = racer_info['tagColor']



    def __getattr__(self, attr):
        if attr in self._racer_info:
            return self._racer_info[attr]
        raise AttributeError(f"'NitrotypeRacer' object has no attribute '{attr}'")