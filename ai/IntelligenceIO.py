# -*- coding:utf-8 -*-
# InteligenceIO.py

"""
startThiningで思考を開始して，
getNextActionで次の手を出力する．

このAIはゲーム開始時に読み込まれることが想定されています．
毎回使い回す処理やパラメータはinit内に記述推奨
"""

from game.GameState import GameState
from game.Action import Action
from game.core import play
from game.core import getCurrentTrendId
from game.core import getTotalScore
from game.core import countPeople
import queue
import copy


#from gui.TreeViewer import TreeViewer

ALPHABETA_DEPTH = 6

# 4-3, 5-3, 6-1, 6-2は無視
ACTION_ID_LIST_N = [
    "1-1",
    "2-1", "2-2", "2-3",
    "3-1", "3-2", "3-3",
    "4-1", "4-2",
           "5-2"
]
ACTION_ID_LIST_R = [
    "1-1",
    "2-1","2-2","2-3",


    "5-2"
]
ACTION_ID_LIST_PS = [
    "1-1",

    "3-1","3-2"


]
ACTION_ID_LIST_PP = [
    "1-1",

                "3-3",
    "4-1","4-2","4-3"

]


SEASON_ID_LIST = ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b"]
KIND_ID_LIST = ["P", "A", "S"]


"""
盤面評価関数
"""
def _eval(state):
    # 終わってたら読み切る
    if(state.finished):
        return getTotalScore(state, state.myid) - getTotalScore(state, state.eid)

    score = 0

    # MとRを単純に増やすだけだとあまり意味がない？
    # 自分のリソースはプラス
    score += state.resources["M"][state.myid]
    score += state.resources["R"][state.myid] * 2
    # 相手のリソースはマイナス
    score -= state.resources["M"][state.eid]
    score -= state.resources["R"][state.eid] * 2

    # お金2より減らしたらダメ
    if state.resources["M"][state.myid] < 2 :
        score -= 100

    score -= state.resources["D"][state.myid] * 1000

    # 各シーズン，相手よりもスコアが高いこと
    if state.scores["T1"][state.myid] + state.deposit_scores["T1"][state.myid] <= state.scores["T1"][state.eid] + state.deposit_scores["T1"][state.eid]:
        score -= 100
    if state.scores["T2"][state.myid] + state.deposit_scores["T2"][state.myid] <= state.scores["T2"][state.eid] + state.deposit_scores["T2"][state.eid]:
        score -= 100
    if state.scores["T3"][state.myid] + state.deposit_scores["T3"][state.myid] <= state.scores["T3"][state.eid] + state.deposit_scores["T3"][state.eid]:
        score -= 100

    if state.myid == 0:
        score += getTotalScore(state, state.myid) * 3
    else:
        score += getTotalScore(state, state.myid)

    return score


"""
アルファベータほう
"""
def _alphabeta(state, depth, alpha, beta):
    # use depth limit
    if depth==0:
        return _eval(state)
    # Extend children nodes
    children = _extend(state)
    state.children = children
    # There are no children.
    if not children:
        #print("Cannot extend")
        return _eval(state)
    if state.current_player_id == state.myid:
        # It's my turn
        for i, child in enumerate(children):
            if depth == ALPHABETA_DEPTH:
                print("Progress", i+1, len(children))
            score = _alphabeta(child, depth-1, alpha, beta)
            if alpha < score : # replace big value and select child node
                alpha = score
                state.best_child = child
                child.score = alpha
                #state.assumption = child
                #state.setActions(child.getActions())
            if alpha >= beta:
                break # beta cut
        return alpha
    else:
        # It's enemies turn
        for i, child in enumerate(children):
            if depth == ALPHABETA_DEPTH:
                print("Progress", i+1, len(children))
            score = _alphabeta(child, depth-1, alpha, beta)
            if score < beta: # replace smaller value and select child node
                beta = score
                state.best_child = child
                child.score = beta
                #state.assumption = child
                #state.last_action = child.action
            if alpha >= beta:
                break #alpha cut
        return beta


"""
盤面展開メソッド
"""
def _extend(state):

    ACTION_ID_LIST = ACTION_ID_LIST_N
    KIND_ID_LIST = ["P", "A", "S"]

    if state.myid == 0 and state.start_player_id == 0 and state.current_player_id == 0:
        if state.season_id not in ["1b","4b","6a","6b"]:
            ACTION_ID_LIST = ACTION_ID_LIST_R
            #if state.resources['P'][state.current_player_id] > 0:
                #KIND_ID_LIST = ['P']


    if state.myid == 1 and state.current_player_id == 1:
        if 'a' in state.season_id and state.season_id != "6a":
            ACTION_ID_LIST = ACTION_ID_LIST_R
            if state.resources['P'][state.current_player_id] > 0:
                KIND_ID_LIST = ['P']

    if state.season_id in ["6a","6b"]:
        #ACTION_ID_LIST = ["4-1","4-2","3-3","4-3","3-2","3-1","1-1"]
        ACTION_ID_LIST = ACTION_ID_LIST_N

    if state.season_id == "6b" and countPeople(state,state.current_player_id) == 1:

        if state.resources['P'][state.current_player_id] > 0:
            ACTION_ID_LIST = ["4-1","4-2","3-3","4-3","3-2","3-1","1-1"]
            kind_id = "P"
        elif state.resources['S'][state.current_player_id] > 0:
            ACTION_ID_LIST = ["4-1","4-2","3-3","3-2","4-3","3-1","1-1"]
            kind_id = "S"

        for action_id in ACTION_ID_LIST:
            action = Action(state.current_player_id,action_id, kind_id=kind_id)
            state_copy = copy.deepcopy(state)
            if play(state_copy, action):
                return [state_copy]


    children = []
    action_list = []

    # アクションリスト生成
    for kind_id in KIND_ID_LIST:         # Select kind_id
        if state.resources[kind_id][state.current_player_id] <= 0: # No worker
            continue
        for action_id in ACTION_ID_LIST:    # Select action_id
            action = Action(state.current_player_id, action_id, kind_id=kind_id)
            action_list.append(action)

    # アクションを適用した盤面を作る
    for action in action_list:
        state_copy = copy.deepcopy(state)
        if play(state_copy, action):
            # success
            children.append(state_copy)

    if state.myid == 0:
        if len(children) > 1:
            children = [child for child in children if not(child.last_action.action_id == "1-1" and child.last_action.kind_id == "S")]

    return children


# TODO: 強制タイムアウト処理
# 別スレッドで回しといてwhileで待機かなぁ？
from time import sleep

class IntelligenceIO:

    def __init__(self):
        self.playerId = -1
        self.nextAction = None
        print("IntelligenceIO was initialized.")
        pass

    """
    thinkingでstateがもらえるので，状態を判断する
    """
    def startThinking(self, state):
        print("start thinking.")
        self.playerid = state.current_player_id
        _alphabeta(state, ALPHABETA_DEPTH, float('-inf'), float('inf'))

        print("=========================")
        for child in state.children:
            if child is state.best_child:
                #print("★", str(child.last_action), _eval(child))
                print("★", str(child.last_action), child.score)
            else:
                #print(" ", str(child.last_action), _eval(child))
                print(" ", str(child.last_action), child.score)
        print("=========================")

        # 表示用 3sec待つ
        #sleep(3)
        print("thinking was finished.")

        #self.nextAction = Action(self.playerid, "1-1", "S")
        self.nextAction = state.best_child.last_action
        pass


    """
    getNextAction使って次打つべき手を返してあげてね
    """
    def getNextAction(self):
        return self.nextAction

    @staticmethod
    def create():
        return IntelligenceIO()
