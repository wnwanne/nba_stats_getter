from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
from twilio.rest import Client
import logging
import requests

team_list = []
f = open('team_short_names', 'r')
for line in f:
    team_list.append(line.strip('\n'))

fav_short_team = input('Please input you favorite team short-name (Boston Celtics = Bos '
                       'Los Angeles Lakers = LAL): ').upper()

if fav_short_team not in team_list:
    fav_short_team = input('Error! please enter a valid NBA team short-name: ').upper()

# API
url = "https://api-nba-v1.p.rapidapi.com/teams/shortName/{}".format(fav_short_team)

headers = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': "acca717e1fmshd937604fdb1e291p148866jsn0e6ec8ccd90e"
    }

# API Call
response = requests.request("GET", url, headers=headers)

# API Response as JSON
team_json = response.json()

# Find Stats
team_name = team_json['api']['teams'][0]['fullName']
nba_teams = teams.find_teams_by_full_name(team_name)
team_id = nba_teams[0]['id']
game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
games = game_finder.get_data_frames()[0]

# Narrow down list of stats and to latest season
games_1819 = games[games.SEASON_ID.str[-4:] == '2018']
cols = ['TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL',
        'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
        'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV',
        'PF', 'PLUS_MINUS']
games_1819 = games_1819[cols]
team_stats = games_1819.mean()
team_name = games_1819['TEAM_NAME'].to_list()[0]

# Twilio access tokens used to send SMS
# ADD AUTHENTICATION
# *******************************************
acc_sid = ''
auth_token = ''
client = Client(acc_sid, auth_token)
# *******************************************
# SMS message sent
Message = 'SEASON STATS: Team Name: {}, Minutes Played: {}, PTS: {}, FGM: {}, FGA: {}, ' \
          'FG_PCT {}, FG3M {}, FG3A {}, FG3_PCT {}, FTM {}, FTA {}, FT_PCT {}, OREB {}, DREB {}, REB {}, AST {}, ' \
          'STL {}, BLK {}, TOV {}, PF {}, PLUS_MINUS {}'.format(team_name, round(team_stats['MIN'], 2),
                                                                round(team_stats['PTS'], 2),
                                                                round(team_stats['FGM'], 2),
                                                                round(team_stats['FGA'], 2),
                                                                round(team_stats['FG_PCT'], 2),
                                                                round(team_stats['FG3M'], 2),
                                                                round(team_stats['FG3A'], 2),
                                                                round(team_stats['FG3_PCT'], 2),
                                                                round(team_stats['FTM'], 2),
                                                                round(team_stats['FTA'], 2),
                                                                round(team_stats['FT_PCT'], 2),
                                                                round(team_stats['OREB'], 2),
                                                                round(team_stats['DREB'], 2),
                                                                round(team_stats['REB'], 2),
                                                                round(team_stats['AST'], 2),
                                                                round(team_stats['STL'], 2),
                                                                round(team_stats['BLK'], 2),
                                                                round(team_stats['TOV'], 2),
                                                                round(team_stats['PF'], 2),
                                                                round(team_stats['PLUS_MINUS'], 2))

registered_number = input('Enter your registered phone number (all digits no spaces): ')

message = client.messages.create(to=registered_number,
                                 from_='8622256658',
                                 body=Message)
print('Check you phone!')
