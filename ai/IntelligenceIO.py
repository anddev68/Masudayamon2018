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
import queue

from game.core import extend
from gui.TreeViewer import TreeViewer

ALPHABETA_DEPTH = 1

"""
盤面評価関数
"""
def _eval(state):
    #pid = state.myid
    eid = getEnemyId(pid)
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
    state.children = extend(state)
    # There are no children.
    if not state.children:
        #print("Cannot extend")
        return _eval(state)    
    if state.current_player_id == state.myid:
        # It's my turn
        for i, child in enumerate(state.children):
            if depth == ALPHABETA_DEPTH:
                print("Progress", i+1, len(state.children))
            score = alphabeta(child, depth-1, alpha, beta)
            if alpha < score: # replace big value and select child node
                alpha = score
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
            score = alphabeta(child, depth-1, alpha, beta)
            if score < beta: # replace smaller value and select child node
                beta = score
                state.assumption = child
                #state.last_action = child.action

            if alpha >= beta:
                break #alpha cut
        return beta


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
        #print(str(state))
        #score = _alphabeta(state, ALPHABETA_DEPTH, float('-inf'), float('inf'))
        #print("\n=============================")
        #print_assumption(solve.state)
        #print("===============================")
        #action = state.assumption.last_action


        children = extend(state)
        for i, child in enumerate(children):
            print(str(child))

        #print(str(state))
        #TreeViewer().show()
        sleep(5)

        print("thinking was finished.")
        print("Warning: Default Action was used.")
        self.nextAction = Action(self.playerid, "1-1", "S")
        pass
    
    """
    getNextAction使って次打つべき手を返してあげてね
    """
    def getNextAction(self):
        return self.nextAction

    @staticmethod
    def create():
        return IntelligenceIO()