import cloudscraper
import datetime

# Define a function to format racer attributes consistently
def format_value(value):
    return '{:,}'.format(value)

class NitrotypeTeam:
    def __init__(self, team_tag):
        self._scraper = cloudscraper.create_scraper()
        self._team_data = self._get_team_data(team_tag)
        self._initialize_attributes()

    def _get_team_data(self, team_tag):
        team_upper = team_tag.upper()
        url = f"https://www.nitrotype.com/api/v2/teams/{team_upper}"

        try:
            response = self._scraper.get(url)
            data = response.json()
            team_data = data.get('results', {}).get('info', {})
            return team_data
        except Exception as e:
            print(f"Failed to fetch data for team {team_tag}: {e}")
            return {}

    def _initialize_attributes(self):
        team_data = self._team_data
        self.team_id = team_data.get('teamID')
        self.user_id = team_data.get('userID')
        self.name = team_data.get('name')
        self.min_level = team_data.get('minLevel')
        self.min_races = team_data.get('minRaces')
        self.min_speed = team_data.get('minSpeed')
        self.other_requirements = team_data.get('otherRequirements')
        self.members = team_data.get('members')
        self.captain_username = team_data.get('username')
        self.enrollment = team_data.get('enrollment')
        self.profile_views = team_data.get('profileViews')
        self.last_modified = team_data.get('lastModified')
        self.created_stamp = team_data.get('createdStamp')
        self.username = team_data.get('username')
        self.display_name = team_data.get('displayName')

        self.formatted_views = format_value(self.profile_views)

        self.last_modified_convert = datetime.datetime.fromtimestamp(self.last_modified).strftime('%Y-%m-%d %H:%M:%S')
        self.created_stamp_convert = datetime.datetime.fromtimestamp(self.created_stamp).strftime('%Y-%m-%d %H:%M:%S')

        # Extracting officer information excluding the captain
        officers_data = [member for member in self._team_data.get('members', []) if member.get('role') == 'officer' and member.get('username') != self.captain_username]
        self.officers_usernames = [officer.get('username') for officer in officers_data]
        self.officers_display_names = [f"[{officer.get('displayName')}]({'https://www.nitrotype.com/racer/' + officer.get('username')})" for officer in officers_data]

# Example usage:
# team_data = NitrotypeTeam("team_tag_here")
# print(team_data.profile_views)
