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


ACTION_ID_LIST = [
    "1-1", 
    "2-1", "2-2", "2-3",
    "3-1", "3-2", "3-3",
    "4-1", "4-2", "4-3",
    "5-1", "5-2", "5-3",
    "6-1", "6-2"
]
SEASON_ID_LIST = ["1a", "1b", "2a", "2b", "3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b"]
KIND_ID_LIST = ["P", "A", "S"]
ALPHABETA_DEPTH = 8


def eval(state):
    pid = state.myid
    eid = getEnemyId(pid)
    tid = getCurrentTrendId(state.season_id)

    # if final node, calculate only score
    if state.finished:
        diff = (getTotalScore(state, pid) - getTotalScore(state, eid))
        return diff

    # normal evaluate
    # We configure, between playing P 2-1 and S 5-1 are same value.
    #   pay $2 (-2point) get R3 (6point) = total 4point
    #   get $3 (3point) 
    score = 0
    score += state.resources["M"][pid]
    score += state.resources["R"][pid] * 3
    score -= state.resources["D"][pid] * 5
    if state.resources["M"][pid] < 1:
        score -= 100
    if (state.scores[tid][pid] - state.scores[tid][eid]) > 0:
        score += 100

    score -= state.resources["M"][eid]
    score -= state.resources["R"][eid] * 3
    score += state.resources["D"][eid] * 5
    if state.resources["M"][eid] < 1:
        score += 100
    if (state.scores[tid][eid] - state.scores[tid][pid]) > 0:
        score -= 100

    #if state.resources["A"][pid] > 0:
    #    score += 50

    #if state.resources["A"][eid] > 0:
    #    score -= 50

    return score












    


"""
This method uses for extending node.
@return children
"""
def extend(state):
    # stop to execute recursively
    if state.season_changed:
        # cannot expand
        #print(eval(s), str(s), s.actionsToStr())
        return None

    children = []

    # make action lists
    # TODO: do outside while loop
    action_list = []
    for kind_id in ["P", "S", "A"]:         # Select kind_id
        if state.resources[kind_id][state.current_player_id] <= 0: # No worker
            continue
        # edagari
        if 0 < state.resources["P"][state.current_player_id] and kind_id == "A": # Put P first
            if 2 < state.resources["M"][state.current_player_id] or 3 < state.resources["R"]: # if enough money or R
                continue

        for action_id in ACTION_ID_LIST:    # Select action_id
            if action_id == "1-1":
                if state.max_workers["S"][state.current_player_id] < 2 and kind_id == "S":
                    # ignore put S to seminar
                    continue
            if action_id == "5-3":
                for tid in ["T1", "T2", "T3"]:
                    action = Action(state.current_player_id, action_id, kind_id=kind_id, trend_id=tid)
                    action_list.append(action)
            else:
                action = Action(state.current_player_id, action_id, kind_id=kind_id)
                action_list.append(action)
    
    # Actions apply 
    for action in action_list:
        state_copy = copy.deepcopy(state)
        if play(state_copy, action):
            # success
            children.append(state_copy)

    # no actions, but workers remain.
    if not action_list or not children:
        print("No action_list was occured. Using 1-1 S.")
        state_copy = copy.deepcopy(state)
        action = Action(state.current_player_id, "1-1", "S")
        if play(state_copy, action):
            children.append(state_copy)

                
    # return children
    return children

def print_assumption(state, depth=1):
    if state.assumption is None:
        return
    print(depth, str(state.assumption.last_action), eval(state))
    #print(str(state.assumption))
    print_assumption(state.assumption, depth+1)


def alphabeta(state, depth, alpha, beta):
    # use depth limit
    if depth==0:
        return eval(state)

    # Extend children nodes
    children = extend(state)

    # There are no children.
    if not children:
        #print("Cannot extend")
        return eval(state)    

    if state.current_player_id == state.myid:
        # It's my turn
        for i, child in enumerate(children):
            if depth == ALPHABETA_DEPTH:
                print("Progress", i+1, len(children))
            score = alphabeta(child, depth-1, alpha, beta)
            if alpha < score: # replace big value and select child node
                alpha = score
                state.assumption = child
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
        #score = alphabeta(state, ALPHABETA_DEPTH, float('-inf'), float('inf'))
        #print("\n=============================")
        #print_assumption(solve.state)
        #print("===============================")
        #action = state.assumption.last_action
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