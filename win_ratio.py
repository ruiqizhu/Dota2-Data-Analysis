# Author: Rich Zhu
# Python script of analying user's dota game data, finds inactive periods
# over the user's game history and measure the correlation between the length
# of the inactive period and the win ratio before inactivity begins

# import revelant libraries
import sys
import numpy as np
from numpy import genfromtxt
from math import log
import copy
import json
from datetime import datetime
import os


start_year = 2010
end_year = 2019
months = 12

def date_out_of_range(year, month):
    if (year < start_year or year >= end_year or month < 1 or month > 12):
        return True
    else:
        return False

# Create a dict over the years with 12 months in each year
def init_dates(start_year, end_year):
    game_dates = dict()
    for year in range(start_year, end_year):
        game_dates[year] = init_months()
    return game_dates

# Create a duct with 12 months
def init_months():
    result = dict()
    for i in range(1, months+1):
        result[i] = 0
    return result

# Aggregate the number of games played each month in each year
def add_games_each_month(game_dates, play_data):
    for i in range(0, len(play_data)):
        play_date = play_data[i][0]
        year, month = play_date.split('-')
        year, month = int(year), int(month)
        # print(game_dates)
        # print("year is " + str(year))
        # print("month is " + str(month))
        if (date_out_of_range(year, month)): continue
        game_dates[year][month] += 1

# Find out the month and year when the user starts playing and stops playing
# Return (0, 0) if player has never played game
def find_real_start_time(game_dates):
    for year in range(start_year, end_year):
        for month in range(1, months + 1):
            if game_dates[year][month] != 0:
                return (year, month)
    return (0, 0)

def find_real_end_time(game_dates):
    for year in range(end_year-1, start_year-1, -1):
        for month in range(months, 0, -1):
            if game_dates[year][month] != 0:
                return (year, month)
    # print("Never played the game!")


# inactive period: number of months consecutively where players play less than 5 games in each month 
# find the start month of the inactive period, its duration, and the win ratio 
# find the 10 games before the start of the inactive period
def find_inactive_period(start_year, start_month, end_year, end_month, game_dates, result_dict, play_data):
    game_bar = 2 # threshold for the minimum number of games each month to be considered active
    first_inactive = False
    inactive_start = False
    inactive_period = 0
    inactive_month = None
    inactive_year = None
    for year in range(start_year, end_year + 1):
        begin_month = 1
        over_month = 12
        if (year == start_year): begin_month = start_month
        if (year == end_year): over_month = end_month
        for month in range(begin_month, over_month + 1):
            num_games = game_dates[year][month]
            # print("Year is " + str(year))
            # print("Month is " + str(month))
            # print("Number of games is " + str(num_games))
            if (num_games < game_bar): # this month is inactive
                if (inactive_start == True):
                    inactive_period += 1
                    # print("Continue adding inactive period")
                    # if it is the last month and year
                    if (year == end_year and month == end_month):
                        # print("Adding the inactive period!!!")
                        update_result(result_dict, inactive_year, inactive_month, inactive_period, start_year, start_month, play_data)
                else: # inactive period has not yet started
                    if (first_inactive == False): 
                        first_inactive = True
                        inactive_month = month
                        inactive_year = year
                        # print("First inactive period")
                    else:
                        inactive_start = True
                        inactive_period += 2
                        # print("Start inactive period")
                        if (year == end_year and month == end_month):
                            # print("Adding the inactive period!!!")
                            update_result(result_dict, inactive_year, inactive_month, inactive_period, start_year, start_month, play_data)
            else: # this month is active
                if (inactive_start == True or first_inactive == True): # terminate this inactive period
                    if (inactive_start == True):
                        # print("Adding the inactive period!!!")
                        update_result(result_dict, inactive_year, inactive_month, 
                                      inactive_period, start_year, start_month, play_data)
                    first_inactive = False
                    inactive_start = False
                    # print("Ending the inactive period")
                    inactive_period = 0
            # print()


def update_result(result_dict, inactive_year, inactive_month, inactive_period, start_year, start_month, play_data):
    win_ratio = find_win_ratio(play_data, inactive_year, inactive_month, start_year, start_month)
    # print("win ratio is ", win_ratio)
    if win_ratio == None: return # No data available
    if inactive_period in result_dict:
        data_list = result_dict[inactive_period]
        data_list.append(win_ratio)
    else:
        result_dict[inactive_period] = [win_ratio]

# bug!!!!
def find_win_ratio(play_data, inactive_year, inactive_month, start_year, start_month):
    wins = 0
    backtrace = 5 # backtrace 5 games
    num_data = 0
    for year in range(inactive_year, start_year - 1, -1):
        month1 = 12
        month2 = 0
        if (year == inactive_year): month1 = inactive_month
        if (year == start_year): month2 = start_month
        for month in range(month1, month2, -1):
            if (year, month) in play_data:
                data_list = play_data[(year, month)]
                for i in range(len(data_list)-1, -1, -1):
                    if (num_data == backtrace): 
                        return float(wins)/backtrace
                    else:
                        num_data += 1
                        if data_list[i] == True:
                            wins += 1     
    if num_data != 0: return float(wins) / num_data
    else: return None   



def process_play_data(play_data):
    processed_data = dict()
    for data in play_data:
        game_result = data[1]
        year, month = (data[0]).split('-')
        year, month = int(year), int(month)
        if (year, month) in processed_data:
            data_list = processed_data[(year, month)]
            data_list.append(game_result)
        else:
            processed_data[(year, month)] = [game_result]
    return processed_data

def find_average(data_list):
    result = np.array(data_list)
    return result.mean()

def average_result(result):
    for key in result:
        data_list = result[key]
        result[key] = find_average(data_list)


# Time interval of the data
# %Y-%m-%d %H:%M:%S  data formatting
# Assumption: Data starts from Jan 2012 to Dec 2018, 7 years in total


# a dictionary where the key is the length of the inactive period and the value
# is the array of winning ratio values
inactive_and_win = dict()
path = '../Player_Analysis/split_player_11/'
# browse through all files in the directory
for root, dirs, files in os.walk(path):
    for name in files:
        print(name)
        with open(path + name) as json_data:
            play_data = json.load(json_data)
            for i in range(0, len(play_data)):
                win_lose = play_data[i]['radiant_win']
                start_time = int(play_data[i]['start_time'])
                start_time = datetime.utcfromtimestamp(start_time).strftime('%Y-%m')
                play_data[i] = (start_time, win_lose)
            play_data.reverse() # orders info in chronological order
            
            game_dates = init_dates(start_year, end_year)
            # find the number of games played in each month
            add_games_each_month(game_dates, play_data)
            # ignore the months in the beginning and end where no games are played
            real_start_year, real_start_month = find_real_start_time(game_dates)
            if (real_start_year != 0): # player has played game
                real_end_year, real_end_month = find_real_end_time(game_dates)
                # modify play data to and put it in a dict form (year, month): list of games played with winning results
                play_data = process_play_data(play_data)
                # find inactive period, calculate the win ratio, and put it into result
                find_inactive_period(real_start_year, real_start_month, real_end_year, real_end_month, game_dates, inactive_and_win, play_data)
            
            # print(play_data)
            # print(inactive_and_win)
            # print((start_year, start_month), (end_year, end_month))
            # print(play_data)
average_result(inactive_and_win)
print(inactive_and_win)







