# -*- coding:utf-8 -*-


"""
ゲームの情報を保持する変数
"""

class GameState:

    def __init__(self, myid):
        self.reset()
        self.myid = myid
    
    def reset(self):
        self.season_id = "1a"  # as string 1a~6b
        self.trend_id = "T0"   # as string T1, T2, T3
        self.start_player_id = 0  # as int
        self.current_player_id = 0
        self.last_action = None
        self.assumption = None
        self.finished = False
        self.season_changed = False
        self.player_changed = True
        self.scores = {
            "T1": [0, 0],
            "T2": [0, 0],
            "T3": [0, 0]
        }
        self.max_workers = {
            "P": [1, 1],
            "A": [0, 0],
            "S": [1, 1],
        }
        self.resources = {
            "P": [1, 1],
            "A": [0, 0],
            "S": [1, 1],
            "M": [5, 5],
            "R": [0, 0],
            "D": [0, 0]
        }
        self.board = {
            "1-1": [],  # worker array
            "2-1": [],
            "2-2": [],
            "2-3": [],
            "3-1": [],
            "3-2": [],
            "3-3": [],
            "4-1": [],
            "4-2": [],
            "4-3": [],
            "5-1": [],
            "5-2": [],
            "5-3": [],
            "6-1": [],
            "6-2": [],
        }

    def resetBoard(self):
        for key in self.board.keys():
            self.board[key] = []

    def toDict(self):
        d = {
            "season_id": self.season_id,
            "trend_id": self.trend_id,
            "start_player_id": self.start_player_id,
            "scores": self.scores,
            "resouces": self.resources,
            "finished": self.finished,
            "season_changed": self.season_changed
        }
        return d
    
    def __str__(self):
        return str(self.toDict().items())

    def setSeasonId(self, season_id):
        self.season_id = season_id

    def setStartPlayerId(self, player_id):
        self.start_player_id = player_id

    def setCurrentPlayerId(self, player_id):
        self.current_player_id = player_id

    def setTrendId(self, trend_id):
        self.trend_id = trend_id
    
    def postSeasonChanged(self):
        self.season_changed = True

    def setPlayerChanged(self, flag):
        self.player_changed = flag

    def postFinished(self):
        self.finished = True

    def resetMaxWorkers(self):
        for key in self.max_workers.keys():
            self.max_workers[key][0] = 0
            self.max_workers[key][1] = 0