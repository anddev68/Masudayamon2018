# -*- coding:utf-8 -*-


"""
ゲームの情報を保持する変数
"""

class GameState:

    def __init__(self, myid):
        self.myid = myid
        if myid == 0:
            self.eid = 1
        else:
            self.eid = 0
        self.reset()
        self.resetDeposit()
    
    def reset(self):
        self.season_id = "1a"           # as string 1a~6b
        self.trend_id = "T0"            # as string T1, T2, T3
        self.start_player_id = 0        # as int
        self.current_player_id = 0      # 手番プレイヤーのID
        self.last_action = None         # 最後に打たれた手
        #self.level = 0                 # 現在の階層(先読みレベル)，AIでしか使わん
        #self.parent = None # 親ノード，AIでしか使わん
        self.children = []              # 展開後のノード，ここにおくのはメモリ上よくないかも
        self.best_child = None          # AIが選択したノード
        #self.assumption = None
        self.finished = False           # ゲームが終了しているかどうか
        self.score = 0                  # AIで使うスコア
#        self.season_changed = False
#        self.player_changed = True
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
        self.board = {  # 盤面
            "1-1": [],  # Workerクラスのインスタンスが入る
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

    def resetDeposit(self):
        self.deposit_resources = {      # このシーズン終了後に変動予定のリソース数
            "P": [0, 0],
            "A": [0, 0],
            "S": [0, 0],
            "M": [0, 0], 
            "R": [0, 0],
        }
        self.deposit_scores = {       # このシーズン終了時に獲得予定のスコア
            "T1": [0, 0],
            "T2": [0, 0],
            "T3": [0, 0]
        }

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
    

    def setSeasonId(self, season_id):
        self.season_id = season_id

    def setStartPlayerId(self, player_id):
        self.start_player_id = player_id

    def setCurrentPlayerId(self, player_id):
        self.current_player_id = player_id

    def setTrendId(self, trend_id):
        self.trend_id = trend_id
    
#    def postSeasonChanged(self):
#        self.season_changed = True

#    def setPlayerChanged(self, flag):
#        self.player_changed = flag

    def postFinished(self):
        self.finished = True

    def resetMaxWorkers(self):
        for key in self.max_workers.keys():
            self.max_workers[key][0] = 0
            self.max_workers[key][1] = 0