from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import leaguegamefinder
import pandas as pd
import numpy as np
from twilio.rest import Client
import logging
import requests
import os


def get_team_list():
    team_list = []
    f = open('team_short_names', 'r')
    for line in f:
        team_list.append(line.strip('\n'))
    return team_list

def get_user_favorite_team(team_list):
    fav_short_team = input('Please input you favorite team short-name (Boston'
                            'Celtics = Bos; Los Angeles Lakers = LAL): ')
    fav_short_team = fav_short_team.upper()
    valid_input = False
    while not valid_input:
        if fav_short_team not in team_list:
            fav_short_team = input('Error! please enter a valid NBA team '
                                    'short-name: ')
        else:
            valid_input = True
    return fav_short_team

def get_team_json(team_input):
    """team_input: short string associated with team name (Boston Celtics ==
    BOS)"""
    # API
    url_base = 'https://api-nba-v1.p.rapidapi.com/teams/shortName/{}'
    url = url_base.format(team_input)
    headers = {
        'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
        'x-rapidapi-key': "acca717e1fmshd937604fdb1e291p148866jsn0e6ec8ccd90e"
        }
    # API Call
    response = requests.request('GET', url, headers=headers)
    # API Response as JSON
    team_json = response.json()
    return team_json

def get_team_data(team_json):
    # Find Stats
    team_name = team_json['api']['teams'][0]['fullName']
    nba_teams = teams.find_teams_by_full_name(team_name)
    team_id = nba_teams[0]['id']
    game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    data = game_finder.get_data_frames()[0]
    return data

def get_team_season(year_str, data):
    # Narrow down list of stats and to latest season
    games = data[data.SEASON_ID.str[-4:] == year_str]
    cols = ['TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'WL',
            'MIN', 'PTS', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT',
            'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK',
            'TOV', 'PF', 'PLUS_MINUS']
    return games[cols]

def get_team_stats(games):
    return games.mean()

def get_team_name(games):
    return games['TEAM_NAME'].to_list()[0]

def get_twilio_client(sid, token):
    # Twilio access tokens used to send SMS
    # ADD AUTHENTICATION
    # *******************************************
    return Client(sid, token)

def send_message(client, team_stats, team_name):
    # SMS message
    message_base = []
    with open('message_base.txt', 'r') as file:
        message_base = file.read().replace('\n', '')

    Message = message_base.format(
        team_name,
        round(team_stats['MIN'], 2),
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

    registered_number = input('Enter your registered phone number (all digits '
                                'no spaces): ')
    client.messages.create(to=registered_number,
                                     from_='8622256658',
                                     body=Message)
    print('New message sent to %s.' % registered_number)

if __name__ == '__main__':
    team_li = get_team_list()
    team_input = get_user_favorite_team(team_li)
    team_json = get_team_json(team_input)
    team_data = get_team_data(team_json)
    games = get_team_season('2018', team_data)
    team_stats = get_team_stats(games)
    team_name = get_team_name(games)
    client = get_twilio_client(os.environ['ACC_SID'], os.environ['AUTH_TOKEN'])
    send_message(client, team_stats, team_name)
