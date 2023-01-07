#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/python
# -*- coding: utf-8 -*-
# Calculates OPR/DPR/CCWM
# For implementation details, see
# https://www.chiefdelphi.com/forums/showpost.php?p=484220&postcount=19

# M is n x n where n is # of teams
# s is n x 1 where n is # of teams
# solve [M][x]=[s] for [x]

# x is OPR and should be n x 1

# Match format:
# match_number, red1, red2, red3, blue1, blue2, blue3, redscore, bluescore

## Event code is set in line 112ish

import numpy as np
import requests
import csv
import pandas as pd

baseURL = 'http://www.thebluealliance.com/api/v3/'
#baseURL = 'http://127.0.0.1:8080/'
header = {'X-TBA-Auth-Key':'2dZKrdov7pGW7HW3kA7Ib8MXa6je84N8ecaqhk3dbFK0SACi27TS8XLU4P5U6GPf'} 

ses = requests.Session()

def getTBA(url):
	return ses.get(baseURL + url, headers=header).json()


numTeams = 3

red_index = [1, numTeams+1]
blue_index = [numTeams+1, (numTeams*2)+1]


def build_team_mapping(matches):
    # Build team list

    team_list = set()

    #any team key is added.
    for match in matches:
        for team in match[1:(numTeams*2)+1]:
            team_list.add(team)

    #Converted to list to make it unique keys.
    team_list = list(team_list)
    team_id_map = {}
    for (i, team) in enumerate(team_list):
        team_id_map[team] = i

    return (team_list, team_id_map)


def build_Minv_matrix(matches, team_id_map):
    n = len(team_id_map.keys())
    M = np.zeros([n, n]) #n x n array of teams to solve.
    for match in matches:
        for alliance_color in [red_index, blue_index]:
            alliance_teams = match[alliance_color[0]:alliance_color[1]]
            for team1 in alliance_teams:
                team1_id = team_id_map[team1]
                for team2 in alliance_teams:
                    M[team1_id, team_id_map[team2]] += 1
    return np.linalg.pinv(M)

def build_s_matrix(matches,team_id_map):
    n = len(team_id_map.keys())
    s = np.zeros([n, 1])
    for match in matches:
		#We used to ignore non-qf matches here.
		#instead do it on input to reduce dimensionality or something.
        for alliance_color in [red_index, blue_index]:
            alliance_teams = [team for team in
                              match[alliance_color[0]:alliance_color[1]]]
            stat = _get_stat(match, alliance_color)

            for team in alliance_teams:
                s[team_id_map[team]] = s[team_id_map[team]] + stat
    return s


def calc_stat(matches, team_list, team_id_map, Minv):
    import numpy as np

    s = build_s_matrix(matches, team_id_map) 
    x = np.dot(Minv, s)

    stat_dict = {}
    for (team, stat) in zip(team_list, x):
        stat_dict[team] = stat[0]
    return stat_dict


def _get_stat( match, alliance_color):
    if alliance_color == red_index:
        return match[7]
    if alliance_color == blue_index:
        return match[8]


def calculate_matchstats(matches):
    (team_list, team_id_map) = build_team_mapping(matches)
    Minv = build_Minv_matrix(matches, team_id_map)
    oprs_dict = calc_stat(matches, team_list, team_id_map, Minv)
    return oprs_dict


eventCode = "2022wasno"# Set event code

eventMatches = [x for x in getTBA("event/" + eventCode + "/matches") if x['comp_level'] == "qm" and x['actual_time'] != None]


keysWeCanUse = []
for key in eventMatches[0]['score_breakdown']['red'].keys():
	if type(eventMatches[0]['score_breakdown']['red'][key]) != type(""):
		keysWeCanUse.append(key)

print(keysWeCanUse)
for cOPRKey in keysWeCanUse:
	currentMatchData = []
	for match in eventMatches:
		if 'score_breakdown' in match:
			#print((match['alliances']['red']['team_keys']))
			currentMatchData.append([match['key']] + match['alliances']['red']['team_keys'] + match['alliances']['blue']['team_keys'] + [match['score_breakdown']['red'][cOPRKey]] + [match['score_breakdown']['blue'][cOPRKey]])
			#print(currentMatchData[-1])


	x = calculate_matchstats(currentMatchData)
	x = sorted([[y,x[y]] for y in x], key=lambda opr:opr[1], reverse=True)
	#print(x)
	with open((eventCode + "_" + cOPRKey + ".csv"), 'w') as csvfile:
		sw = csv.writer(csvfile, delimiter=',',
                            quotechar='|')
		for dataItem in x:
			#print(dataItem)
			sw.writerow(dataItem)


# In[4]:


import pandas as pd
import numpy as np
import math
import time
import sys
from IPython.display import display 
import csv
from astropy import units as u
from astropy.coordinates import Angle

#still needs to be cleaned up, but should work
pd.set_option("display.max_rows", None, "display.max_columns", None)


OPRt = pd.read_csv ('2022wasno_matchCargoTotal.csv',index_col=None, header=None ) 

type(OPRt)
OPRt.columns = ['Team', 'Cargo Count OPR']
display(OPRt)
OPR8248wasno = OPRt[OPRt['Team'].str.contains('8248')]
print (OPR8248wasno)

OPRt = pd.read_csv ('2022wabon_matchCargoTotal.csv',index_col=None, header=None ) 

type(OPRt)
OPRt.columns = ['Team', 'Cargo Count OPR']
display(OPRt)
OPR8248wabon = OPRt[OPRt['Team'].str.contains('8248')]
print (OPR8248wabon)

OPRt = pd.read_csv ('2022pncmp_matchCargoTotal.csv',index_col=None, header=None ) 

type(OPRt)
OPRt.columns = ['Team', 'Cargo Count OPR']
display(OPRt)
OPR8248wacmp = OPRt[OPRt['Team'].str.contains('8248')]
print (OPR8248wacmp)


# In[5]:


mainSeason = pd.concat([OPR8248wasno, OPR8248wabon])
fullSeason = pd.concat([mainSeason, OPR8248wacmp])
#print(fullSeason)

df = pd.DataFrame(data=fullSeason)

print(df)

Total = df.at[17, 'Cargo Count OPR']+df.at[7, 'Cargo Count OPR']+df.at[42, 'Cargo Count OPR']
final=(Total/3)/2
print("Total avg cycles by OPR=", final)
print("WASNO avg cycles by OPR=", (df.at[17, 'Cargo Count OPR']/2))
print("WABON avg cycles by OPR=", (df.at[7, 'Cargo Count OPR']/2))
print("PNWCMP avg cycles by OPR=", (df.at[42, 'Cargo Count OPR']/2))


# In[ ]:




