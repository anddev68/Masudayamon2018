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
import queue
import copy


#from gui.TreeViewer import TreeViewer

ALPHABETA_DEPTH = 2

# 5-3は無視
ACTION_ID_LIST = [
    "1-1", 
    "2-1", "2-2", "2-3",
    "3-1", "3-2", "3-3",
    "4-1", "4-2", "4-3",
    "5-1", "5-2",
    "6-1", "6-2"
]
SEASON_ID_LIST = ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b"]
KIND_ID_LIST = ["P", "A", "S"]


"""
盤面評価関数
"""
def _eval(state):
    #pid = state.myid
    #eid = getEnemyId(pid)
    # tid = getCurrentTrendId(state.season_id)
    return state.resources["M"][state.myid]


"""
ゲーム木出力メソッド
"""
def _print_assumption(state, depth=1):
    if state.assumption is None:
        return
    print(depth, str(state.assumption.last_action), eval(state))
    #print(str(state.assumption))
    print_assumption(state.assumption, depth+1)

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
            if alpha < score: # replace big value and select child node
                alpha = score
                state.best_child = child
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
                #state.assumption = child
                #state.last_action = child.action
            if alpha >= beta:
                break #alpha cut
        return beta


"""
盤面展開メソッド
"""
def _extend(state):
    # 初手決め打ち
    if state.season_id == "1a":
        if state.current_player_id == 0: # 先行
            if 0 < state.resources["P"][0]: #初手
                action = Action(0, "1-1", kind_id="P")
            else: # 2手目
                action = Action(0, "1-1", kind_id="S")
        else: #後攻
            if 0 < state.resources["P"][1]: #初手
                # 1-1 Sもありっぽい
                action = Action(1, "5-1", kind_id="P")
            else: # 2手目
                action = Action(1, "1-1", kind_id="S")
        state_copy = copy.deepcopy(state)
        if play(state_copy, action):
            return [state_copy]
        print("Select error.")
        exit(-1)

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
                print("★", str(child.last_action), _eval(child))
            else:
                print(" ", str(child.last_action), _eval(child))
        print("=========================")

        # 表示用 3sec待つ
        sleep(3)

        print("thinking was finished.")
        print("Warning: Default Action was used.")
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