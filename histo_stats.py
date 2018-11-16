# Author: Rich Zhu
# Python script of analyzing user's dota game data
# Creates a histogram that shows the overall win rate, leaver ratio, and hero diversity

# import revelant libraries
import sys
import numpy as np
import json
from datetime import datetime
import os
import matplotlib.pyplot as plt

start_year = 2010
end_year = 2019
months = 12

# Create a dict over the years with 12 months in each year
def init_dates(start_year, end_year, months):
    games_each_month = dict()
    for year in range(start_year, end_year):
        for month in range(1, months + 1):
            games_each_month[(year, month)] = 0
    return games_each_month




class Player(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.win_rate = 0
        self.hero_diversity = 0
        self.leaver_rate = 0
        self.num_matches = 0
        self.games_each_month = init_dates(start_year, end_year, months)
        self.real_start_year = 0
        self.real_start_month = 0
        self.real_end_year = 0
        self.real_end_month = 0
        self.hero_set = set()




def date_out_of_range(year, month):
    if (year < start_year or year >= end_year or month < 1 or month > 12):
        return True
    else:
        return False



# Find out the month and year when the user starts playing and stops playing
def find_real_start_time(game_dates):
    for year in range(start_year, end_year):
        for month in range(1, months + 1):
            if game_dates[(year, month)] != 0:
                return (year, month)

def find_real_end_time(game_dates):
    for year in range(end_year-1, start_year-1, -1):
        for month in range(months, 0, -1):
            if game_dates[(year, month)] != 0:
                return (year, month)


def get_time(start_time):
    start_time = datetime.utcfromtimestamp(start_time).strftime('%Y-%m')
    year, month = start_time.split('-')
    year, month = int(year), int(month)
    return (year, month)

def update_user_data(user, play_data):
    num_matches = len(play_data)
    user.num_matches = num_matches
    wins = 0
    leaves = 0

    for i in range(0, num_matches):
        win = play_data[i]['radiant_win']
        if win == True: wins += 1
        leave = play_data[i]['leaver_status']
        if leave != 0: leaves += 1
        hero_id = play_data[i]['hero_id']
        if hero_id not in user.hero_set: user.hero_set.add(hero_id)
        start_time = int(play_data[i]['start_time'])
        (year, month) = get_time(start_time)
        if (date_out_of_range(year, month)): continue
        user.games_each_month[(year, month)] += 1

    user.win_rate = float(wins) / num_matches
    user.leaver_rate = float(leaves) / num_matches
    user.hero_diversity = float(len(user.hero_set)) / num_matches
    user.real_start_year, user.real_start_month = find_real_start_time(user.games_each_month)
    user.real_end_year, user.real_end_month = find_real_end_time(user.games_each_month)



win_rate_list = list()
hero_diversity_list = list()
leaver_rate_list = list()
total_matches_list = list()
user_id_list = list()
id_to_user = dict() # A dictionary that uses user id to map directly to user object
path = '../Player_Analysis/split_player_11/'
# browse through all files in the directory
for root, dirs, files in os.walk(path):
    for name in files:
        print(name)
        with open(path + name) as json_data:
            play_data = json.load(json_data)
            if len(play_data) < 50: continue # ignore players with less than 50 games
            user_id = name.split("_")[0]
            user = Player(user_id)
            id_to_user[user_id] = user
            update_user_data(user, play_data)

            win_rate_list.append(user.win_rate)
            hero_diversity_list.append(user.hero_diversity)
            leaver_rate_list.append(user.leaver_rate)
            total_matches_list.append(user.num_matches)
            user_id_list.append(user.user_id)
            id_to_user[user_id] = user

# win rate data
plt.hist(win_rate_list, bins = 10)
plt.title("Win rate histogram")
plt.show()

# hero diversity data
plt.hist(hero_diversity_list, bins = 10)
plt.title("Hero diversity histogram")
plt.show()

# leaver rate data
plt.hist(leaver_rate_list, bins = 10)
plt.title("Leaver rate histogram")
plt.show()

plt.scatter(hero_diversity_list, win_rate_list)
plt.title("Hero diversity and win rate")
plt.xlabel("Hero diversity")
plt.ylabel("Win rate")
plt.show()

plt.scatter(hero_diversity_list, leaver_rate_list)
plt.title("Hero diversity and leaver rate")
plt.xlabel("Hero diversity")
plt.ylabel("Leaver rate")
plt.show()

plt.scatter(win_rate_list, leaver_rate_list)
plt.title("Win rate and leaver rate")
plt.xlabel("Win rate")
plt.ylabel("Leaver rate")
plt.show()

        








