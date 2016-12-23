import requests
import string

class APIError(Exception):
    """
    Error class that should simply output errors
    raised by the Warlight API itself
    """
    pass

class ServerGameKeyNotFound(Exception):
    """
    Error class for nonexistent games
    """
    pass

def getAPIToken(email, password):
    """
    Gets API token using email and password
    """
    site = "https://www.warlight.net/API/GetAPIToken"
    data = dict()
    data['Email'] = email
    data['Password'] = password
    r = requests.post(url=site, params=data)
    jsonOutput = r.json()
    if 'error' in jsonOutput:
        raise APIError(jsonOutput['error'])
    return jsonOutput['APIToken']

def makeAPIHandler(email, password):
    token = getAPIToken(email, password)
    return APIHandler(email, token)

class APIHandler(object):

    def __init__(self, email, token):
        self.email = email
        self.token = token

    @classmethod
    def __canBeTeamless(cls, teams, allowTeamless=True):
        """
        Helper function to determine whether a game can be teamless
        """
        return ((allowTeamless is True) and ([team for team in teams 
                if ((isinstance(team, tuple) or isinstance(team, list))
                    and len(team) > 1)] == list()))
        # essentially checks teams for tuples; if no tuples are present,
        # then the game can be played teamlessly

    def __makePlayers(self, teams, allowTeamless=False):
        """
        Given teams, returns a list
        containing player dictionaries

        PARAMETERS:
        teams: list of teams as tuples of player IDs

        OPTIONAL:
        teamless: bool (default False); if set to True,
            a teamless result will be returned if possible
        """
        teamless = self.__canBeTeamless(teams, allowTeamless)
        teamID = 0
        players = list()
        for team in teams:
            if (teamless):
                if (type(team) == tuple):
                    team = team[0]
                player = dict()
                player['token'] = str(team)
                player['team'] = str(None)
                players.append(player)
            elif (type(team) == list) or (type(team) == tuple):
                for member in team:
                    player = dict()
                    player['token'] = str(member)
                    player['team'] = str(teamID)
                    players.append(player)
            else:
                player = dict()
                player['token'] = str(team)
                player['team'] = str(teamID)
                players.append(player)
            teamID += 1
        return players

    @classmethod
    def __overrideBonuses(cls, bonuses):
        """
        Given a list containing tuples
        with bonus name and new values,
        generates new list with said data
        in dictionary form
        """
        overridenBonuses = list()
        for bonus in bonuses:
            bonusData = dict()
            bonusData['bonusName'] = bonus[0]
            bonusData['value'] = bonus[1]
            overridenBonuses.append(bonusData)
        return overridenBonuses

    def queryGame(self, gameID, getHistory=False, 
                  getSettings=False):
        """
        Queries a game given gameID
        using credentials (email+token)
        returns JSON output
        """
        getHistory = str(getHistory).lower()
        getSettings = str(getSettings).lower()
        site = "https://www.warlight.net/API/GameFeed"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = str(self.token)
        data['GameID'] = str(gameID)
        data['GetHistory'] = getHistory
        data['GetSettings'] = getSettings
        r = requests.post(url=site, params=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            if ("ServerGameKeyNotFound" in jsonOutput['error']):
                raise ServerGameKeyNotFound(jsonOutput['error'])
            raise APIError(jsonOutput['error'])
        return jsonOutput

    def createGame(self, settingsDict=dict(), **settings):
        """
        Creates a game given settings
        using credentials (email+token)
        returns game ID
        """
        site = "https://www.warlight.net/API/CreateGame"
        data = dict()
        data['hostEmail'] = self.email
        data['hostAPIToken'] = str(self.token)
        data['templateID'] = settings.get('template')
        data['gameName'] = settings.get('gameName')
        data['personalMessage'] = settings.get('message', "")
        teams = settings.get('teams')
        data['players'] = self.__makePlayers(teams)
        data['settings'] = settingsDict
        if 'overriddenBonuses' in settings:
            data['overridenBonuses'] = \
            self.__overrideBonuses(settings.get('overridenBonuses'))
        r = requests.post(url=site, json=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        return jsonOutput['gameID']

    def deleteGame(self, gameID):
        """
        Deletes a game
        using credentials (email+token)
        does not return anything
        """
        site = "https://www.warlight.net/API/DeleteLobbyGame"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = str(self.token)
        data['gameID'] = int(gameID)
        r = requests.post(url=site, json=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        if 'success' not in jsonOutput:
            raise APIError("Unknown error!")

    def getGameIDs(self, *source):
        """
        Gets a list of games for a ladder/tournament
        using credentials (email+token)
        returns list of games
        """
        site = "https://www.warlight.net/API/GameIDFeed"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = self.token
        try:
            assert(len(source) == 2)
        except:
            raise TypeError("Need both source type and ID!")
        if ("ladder" in source) or ("Ladder" in source):
            data['LadderID'] = int(source[-1])
        elif ("tournament" in source) or ("Tournament" in source):
            data['TournamentID'] = int(source[-1])
        else:
            raise IOError("Source type must be either ladder or tournament!")
        r = requests.post(url=site, params=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        return jsonOutput['gameIDs']

    def validateToken(self, player, *templates):
        """
        Validtes an inviteToken
        using credentials (email+token)
        returns response
        """
        site = "https://www.warlight.net/API/ValidateInviteToken"
        data = dict()
        data['Email'] = self.email
        data['APIToken'] = self.token
        data['Token'] = player
        if templates is not tuple():
            data['TemplateIDs'] = string.join(templates, ",")
        r = requests.post(url=site, params=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])
        return jsonOutput

    def setMapDetails(self, mapID, *commands):
        """
        Sets map details
        using credentials (email+token)
        and command setup (commandtype, dict())
        """
        site = "https://www.warlight.net/API/SetMapDetails"
        data = dict()
        data['email'] = self.email
        data['APIToken'] = self.token
        data['mapID'] = str(mapID)
        commandData = list()
        for command in commands:
            order = dict()
            order['command'] = command[0]
            for item in command[1]:
                order[item] = command[item]
            commandData.append(order)
        data['commands'] = commandData
        r = requests.post(url=site, json=data)
        jsonOutput = r.json()
        if 'error' in jsonOutput:
            raise APIError(jsonOutput['error'])