# automated tests for wl_api.py

import sys
# sys.path hack @TODO: get rid of this
sys.path.append('..')

from nose.tools import *
from wl_api import *

def test_apihandler():
    apiHandler = APIHandler(email="iwill@lightthefu.se",
                            token="andillneverlose")
    assert_equal(apiHandler.email,"iwill@lightthefu.se")
    assert_equal(apiHandler.token,"andillneverlose")

def test_canBeTeamless():
    cbt = APIHandler._APIHandler__canBeTeamless
    cbt_forced = lambda x: APIHandler._APIHandler__canBeTeamless(x,
                           allowTeamless=False)
    teamless = [0, 1]
    one_player = [(0,)]
    teamless_tuples = [(0,), (1,), (2,), (3,)]
    teamed = [(0,1), 3]
    teamed_multi = [(0,1), (2,3), (4,5), (6,7)]
    empty = list()
    tricky = [0, 1, 2, (3,), (5,), (84,49)]
    tricky_teamless = [0, 1, 2, (3,), (5,), (84,)]
    # should return True
    assert_true(cbt(teamless))
    assert_true(cbt(one_player))
    assert_true(cbt(teamless_tuples))
    assert_true(cbt(empty))
    assert_true(cbt(tricky_teamless))
    # should return False
    assert_false(cbt_forced(teamless))
    assert_false(cbt(teamed))
    assert_false(cbt_forced(teamed))
    assert_false(cbt(teamed_multi))
    assert_false(cbt_forced(empty))
    assert_false(cbt_forced(tricky))
    assert_false(cbt(tricky))

def retrieve_teams(playerList):
    teamDict = dict()
    for player in playerList:
        team = player['team']
        token = player['token']
        if team not in teamDict:
            teamDict[team] = list()
        teamDict[team].append(token)
    return teamDict

def retrieve_players(playerList):
    playerDict = dict()
    for player in playerList:
        team = player['team']
        token = player['token']
        playerDict[token] = team
    return playerDict

def same_team(playerList, player1, player2):
    playerDict = retrieve_players(playerList)
    return (playerDict[str(player1)] == playerDict[str(player2)])

def opp_team(playerList, player1, player2):
    playerDict = retrieve_players(playerList)
    return (playerDict[str(player1)] != playerDict[str(player2)])

def test_makePlayers():
    apiHandler = APIHandler("email", "token")
    teams_2v2 = [(0,1), (2,3)]
    teams_1v1 = [0, 1]
    teams_2v1 = [[0,1], 2]
    teams_1v1v1 = [(0,), (1,), (2,)]
    teams_1v1v2 = [(0,), 1, [2,3]]
    teams_3v4v5 = [(0,1,2), (3,4,5,6), (7,8,9,10,11)]
    assert_equal(apiHandler._APIHandler__makePlayers(teams_2v2),
                 apiHandler._APIHandler__makePlayers(teams_2v2, True))
    assert_equal(apiHandler._APIHandler__makePlayers(teams_2v1),
                 apiHandler._APIHandler__makePlayers(teams_2v1, True))
    assert_equal(apiHandler._APIHandler__makePlayers(teams_1v1v2),
                 apiHandler._APIHandler__makePlayers(teams_1v1v2, True))
    assert_equal(apiHandler._APIHandler__makePlayers(teams_3v4v5),
                 apiHandler._APIHandler__makePlayers(teams_3v4v5, True))
    players_2v2 = apiHandler._APIHandler__makePlayers(teams_2v2)
    assert same_team(players_2v2, 0, 1)
    assert same_team(players_2v2, 2, 3)
    assert opp_team(players_2v2, 1, 2)
    players_1v1 = apiHandler._APIHandler__makePlayers(teams_1v1)
    assert opp_team(players_1v1, 0, 1)
    players_1v1_t = apiHandler._APIHandler__makePlayers(teams_1v1, True)
    assert players_1v1_t[0]['team'] == 'None'
    assert same_team(players_1v1_t, 0, 1)
    players_2v1 = apiHandler._APIHandler__makePlayers(teams_2v1)
    assert same_team(players_2v2, 0, 1)
    assert opp_team(players_2v2, 0, 2)
    players_1v1v1 = apiHandler._APIHandler__makePlayers(teams_1v1v1)
    assert opp_team(players_1v1v1, 2, 0)
    players_1v1v1_t = apiHandler._APIHandler__makePlayers(teams_1v1v1, True)
    assert same_team(players_1v1v1_t, 1, 2)
    assert players_1v1v1_t[0]['team'] == 'None'
    players_1v1v2 = apiHandler._APIHandler__makePlayers(teams_1v1v2)
    assert same_team(players_1v1v2, 2, 3)
    assert opp_team(players_1v1v2, 0, 1)
    assert opp_team(players_1v1v2, 1, 2)
    players_3v4v5 = apiHandler._APIHandler__makePlayers(teams_3v4v5)
    assert same_team(players_3v4v5, 0, 2)
    assert same_team(players_3v4v5, 3, 5)
    assert same_team(players_3v4v5, 9, 11)
    assert opp_team(players_3v4v5, 0, 6)
    assert opp_team(players_3v4v5, 1, 8)
    assert opp_team(players_3v4v5, 4, 10)
    assert opp_team(players_3v4v5, 6, 2)