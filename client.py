# -*- coding:utf-8 -*-

# The Laboratory AI
# revised for Masudayamon2018
# @Author Hideki Kano

import socket
import copy
import sys
import Queue

# Settings
SERVER_IP = "localhost"
SERVER_PORT = 18420
CLIENT_NAME = "Alice"
ALPHABETA_DEPTH = 8
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



"""
Message consists of code + instructions (ex. 100 HELLO)
There are two ways for making Massage
1. With constructer  
    Message(102, {"NAME", "hogehoge"})
2. With "convertToMessage" method
    convertToMessage("102 NAME hogehoge")
"""
class Message:
    def __init__(self, code, instructions):
        self.code = code
        self.instructions = instructions
    def __str__(self):
        return str(self.code)+" "+' '.join(self.instructions) + "\n"

"""
Worker class
"""
class Worker:
    def __init__(self, player_id, kind_id):
        self.player_id = player_id
        self.kind_id = kind_id

"""
Action class
Examples, Action("2-A", "S")
"""
class Action:
    def __init__(self, player_id, action_id, kind_id, trend_id=None):
        self.action_id = action_id
        self.kind_id = kind_id
        self.player_id = player_id
        self.trend_id = trend_id
    def __str__(self):
        # Return value examples, like S 2-A
        if self.trend_id:
            return "Player"+str(self.player_id) + " "+ self.kind_id + " " +self.action_id + " " + self.trend_id
        return "Player"+str(self.player_id) + " "+ self.kind_id + " " +self.action_id

"""
Logger class
to output Graph
"""
class Logger:
    #LOG_HEADER = ["T1", "T2", "T3", "P", "A", "S", "M", "R", "D"]
    def __init__(self):
        if len(sys.argv) >= 2:
            self.filename = sys.argv[1]
        else:
            self.filename = "player.log"
        
    def output(self, state):
        for i in [0,1]:
            f = open("{0}_{1}".format(i, self.filename), "a")
            f.write("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}".format(
            state.season_id,
            state.scores["T1"][i],
            state.scores["T2"][i],
            state.scores["T3"][i],
            state.resources["P"][i],
            state.resources["A"][i],
            state.resources["S"][i],
            state.resources["M"][i],
            state.resources["R"][i],
            state.resources["D"][i],
            getTotalScore(state, i),
            ))
            f.write("\n")
            f.close()

    def output_score(self, scores):
        for i in [0,1]:
            f = open("{0}_{1}".format(i, self.filename), "a")
            f.write("{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10}".format(
                "fin",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                "N/A",
                scores[i]
            ))
            f.write("\n")
            f.close()



"""
Game State Class
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


# raw message to Message class
def convertToMessage(raw_message):
    vector = raw_message.split()
    code = int(vector[0])
    instructions = vector[1:]
    return Message(code, instructions)


def getEnemyId(pid):
    if pid==0:
        return 1
    return 0

def getCurrentTrendId(season_id):
    if season_id in ["1a", "1b", "4a", "4b"]:
        return "T1"
    elif season_id in ["2a", "2b", "5a", "5b"]:
        return "T2"
    elif season_id in ["3a", "3b", "6a", "6b"]:
        return "T3"
    print("Convert Error, Unexpected season_id.")
    exit(1)

def getNextSeasonId(season_id):
    let = "9z"
    if season_id[1] == 'b':
        return str(int(season_id[0])+1) + 'a'    
    else:
        return season_id[0]+ 'b'

def getTotalScore(state, pid):
    return state.scores["T1"][pid] + state.scores["T2"][pid] + state.scores["T3"][pid] 

def countPeople(state, pid):
    return state.resources["P"][pid] + state.resources["A"][pid] +state.resources["S"][pid] 

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
    score = 0
    score += state.resources["M"][pid] 
    score += state.resources["R"][pid] * 2
    score -= state.resources["R"][eid] * 2
    score -= state.resources["D"][pid] * 5
    if (state.scores[tid][pid] - state.scores[tid][eid]) > 0:
        score += 100

    if state.resources["M"][state.current_player_id] < 1:
        score -= 100

    if state.myid == state.current_player_id:
        #print(-score)
        return -score

    #print(score)
    return score
    """
    

    """
    # Read all trees
    if state.finished:
        score = getTotalScore(state, state.myid) - getTotalScore(state, getEnemyId(state.myid))
        if state.current_player_id == state.myid:
            return score * 1000
        else:
            return (-score) * 1000
    
    pid = state.current_player_id
    eid = getEnemyId(pid)
    score = 0
    #score += (state.resources["M"][pid] - state.resources["M"][eid])
    #score += (state.resources["R"][pid] - state.resources["R"][eid]) * 2
    #score -= state.resources["D"][pid] * 5
    score += getTotalScore(state, pid) * 20
    """
    """
    if 2 < state.resources["M"][pid]:
        score += 20

    # no employ
    if 2 < countPeople(state, pid):
        score -= 100
    """
    



def isFinished(state):
    return False

def hasHoldingWorker(state, pid):
    for kind_id in KIND_ID_LIST: 
        if 0 < state.resources[kind_id][pid]:
            return True
    return False

def doProduction(state):
    # Calculate r_seminar point
    p = 0
    a = 0
    s = 0
    for worker in state.board["1-1"]:
        if worker.kind_id == "P":
            p += 1
        elif worker.kind_id == "A":
            a += 1
        elif worker.kind_id == "S":
            s += 1
    # round
    r_seminar =  int(s/2*(a+p))

    # clear max_worker
    state.resetMaxWorkers()

    # Calcualate production by worker
    for key, value in state.board.items():   
        for worker in value:
            if key == "1-1": # R+(2,3,*) *: (S/2)(A+P)
                if worker.kind_id == "P":
                    state.resources["R"][worker.player_id] += 2
                elif worker.kind_id == "A":
                    state.resources["R"][worker.player_id] += 3
                elif worker.kind_id == "S":
                    state.resources["R"][worker.player_id] += r_seminar
                pass
            elif key == "2-1": # R+3
                state.resources["R"][worker.player_id] += 3
            elif key == "2-2": # R+4
                state.resources["R"][worker.player_id] += 4
            elif key == "2-3": # R+5
                state.resources["R"][worker.player_id] += 5
            elif key == "3-1": # Presentation score+(1,1,2)
                if worker.kind_id == "P":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 1
                elif worker.kind_id == "A":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 1
                elif worker.kind_id == "S":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 2
            elif key == "3-2": # Presentation score+(3,4,4)
                if worker.kind_id == "P":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 3
                elif worker.kind_id == "A":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 4
                elif worker.kind_id == "S":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 4
            elif key == "3-3": # Presentation score+(7,6,5)
                if worker.kind_id == "P":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 7
                elif worker.kind_id == "A":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 6
                elif worker.kind_id == "S":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 5
            elif key == "4-1": # Paper score+(8,7,6)
                if worker.kind_id == "P":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 8
                elif worker.kind_id == "A":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 7
                elif worker.kind_id == "S":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 6
            elif key == "4-2": # Paper score+(7,6,5)
                if worker.kind_id == "P":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 7
                elif worker.kind_id == "A":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 6
                elif worker.kind_id == "S":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 5
            elif key == "4-3": # Paper score+(6,5,4)
                if worker.kind_id == "P":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 6
                elif worker.kind_id == "A":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 5
                elif worker.kind_id == "S":
                    state.scores[getCurrentTrendId(state.season_id)][worker.player_id] += 4                            
            elif key == "5-1": # M+3 and start player
                state.setStartPlayerId(worker.player_id)
                state.resources["M"][worker.player_id] += 3
            elif key == "5-2": # M+5
                state.resources["M"][worker.player_id] += 5
            elif key == "5-3": # M+6 and trand
                state.resources["M"][worker.player_id] += 6
                pass
            elif key == "6-1":
                state.resources["S"][worker.player_id] += 1
            elif key == "6-2":
                state.resources["A"][worker.player_id] += 1
            
            # collect worker
            state.resources[worker.kind_id][worker.player_id] += 1
            state.max_workers[worker.kind_id][worker.player_id] += 1

    # board clear
    state.resetBoard()

def doPayment(state):
    for pid in [0, 1]:
        fee = 0
        fee += state.resources["A"][pid] * 3
        fee += state.resources["S"][pid]
        state.resources["M"][pid] -= fee
        if state.resources["M"][pid] < 0:
            state.resources["D"][pid] -= state.resources["M"][pid] 
            state.resources["M"][pid] = 0

def doAwarding(state):
    current_trend_id = getCurrentTrendId(state.season_id)
    if state.trend_id == current_trend_id:
        p = 8
    else:
        p = 5
    if state.scores[current_trend_id][0] < state.scores[current_trend_id][1]:
        state.resources["M"][1] += p
    elif state.scores[current_trend_id][0] > state.scores[current_trend_id][1]:
        state.resources["M"][0] += p
    else:
        # TODO: if same point, all members get money?
        state.resources["M"][0] += p
        state.resources["M"][1] += p

"""
def goNextSeason(state):

    # if 6b, finish this game.
    if "6b" == state.season_id:
        state.finished = True
        #print("finished")
        return

    # Calculate awrard if need
    # after 1b, 2b, 3b, 4b, 5b, 6b
    if "b" in state.season_id:
        #print("awarded")
        pass



    # Common procedure
    state.setSeasonId(getNextSeasonId(state.season_id))
    state.setCurrentPlayerId(state.start_player_id)
"""

"""
@return True ok
@return False falied
"""
def play(state, action):

    # individual procedure including checking condition
    if action.action_id == "1-1":
        pass
    elif action.action_id in ["2-1", "2-2", "2-3"]:
        # Experiment: -2M
        if state.board[action.action_id] or state.resources["M"][action.player_id] < 2:
            return False
        if action.action_id == "2-2" and not state.board["2-1"]:
            return False
        if action.action_id == "2-3" and not state.board["2-2"]:
            return False
        state.resources["M"][action.player_id] -= 2
    elif action.action_id == "3-1": # Presentation R-2
        if state.board[action.action_id] or state.resources["R"][action.player_id] < 2:
            return False
        state.resources["R"][action.player_id] -= 2
    elif action.action_id == "3-2": # Presentation R-4 M-1
        if state.board[action.action_id] or state.resources["R"][action.player_id] < 4 or state.resources["M"][action.player_id] < 1:
            return False
        state.resources["M"][action.player_id] -= 1
        state.resources["R"][action.player_id] -= 4
    elif action.action_id == "3-3": # Presantation R-8 M-1
        if state.board[action.action_id] or state.resources["R"][action.player_id] < 8 or state.resources["M"][action.player_id] < 1:
            return False
        state.resources["M"][action.player_id] -= 1
        state.resources["R"][action.player_id] -= 8
    elif action.action_id == "4-1": # R-8 M-1
        if state.board[action.action_id] or state.resources["R"][action.player_id] < 8 or state.resources["M"][action.player_id] < 1:
            return False
        state.resources["M"][action.player_id] -= 1
        state.resources["R"][action.player_id] -= 8
    elif action.action_id == "4-2":
        if state.board[action.action_id] or not state.board["4-1"] or state.resources["R"][action.player_id] < 8 or state.resources["M"][action.player_id] < 1: # full itself or 2-1 is empty, then failed
            return False
        state.resources["M"][action.player_id] -= 1
        state.resources["R"][action.player_id] -= 8
    elif action.action_id == "4-3":
        if state.board[action.action_id] or not state.board["4-2"] or state.resources["R"][action.player_id] < 8 or state.resources["M"][action.player_id] < 1: # full itself or 2-1 is empty, then failed
            return False
        state.resources["M"][action.player_id] -= 1
        state.resources["R"][action.player_id] -= 8
    elif action.action_id == "5-1": # nocost
        if state.board[action.action_id] or action.kind_id == "S":
            return False
        pass
    elif action.action_id == "5-2": # R-1
        if state.board[action.action_id] or state.resources["R"][action.player_id] < 1 or action.kind_id == "S":
            return False
        state.resources["R"][action.player_id] -= 1
    elif action.action_id == "5-3": # R-3 trand change
        if state.board[action.action_id] or state.resources["R"][action.player_id] < 3 or action.kind_id == "S":
            return False
        state.resources["R"][action.player_id] -= 3
        state.setTrendId(action.trend_id)
    elif action.action_id == "6-1": # Employ R-3
        if state.board[action.action_id] or state.resources["R"][action.player_id] < 3 or action.kind_id == "S":
            return False
        state.resources["R"][action.player_id] -= 3
    elif action.action_id == "6-2": # Employ score 10+
        if state.board[action.action_id] or getTotalScore(state, action.player_id) < 10 or not action.kind_id == "P":
            return False
        pass

    # common procedure
    state.last_action = action  # Set action
    state.resources[action.kind_id][action.player_id] -=1   # Decrease holding worker 
    state.board[action.action_id].append(Worker(action.player_id, action.kind_id)) #Put to board

    # Check worker
    cpid = action.player_id
    npid = getEnemyId(action.player_id)
    if hasHoldingWorker(state, npid):
        # other player plays.
        state.setCurrentPlayerId(npid)
        state.setPlayerChanged(True)

    elif hasHoldingWorker(state, cpid):
        # sampe player plays again.
        state.setPlayerChanged(False)
        pass
        
    else:
        # next season
        doProduction(state)
        
        if state.season_id == "6b":
            state.postFinished()
        else:
            # if need, get award
            if "b" in state.season_id:
                doAwarding(state)
            
            # if need, pay
            doPayment(state)
            
        state.postSeasonChanged()
        state.setCurrentPlayerId(state.start_player_id)

    return True

    


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

    """
    if state.assumption is None:
        return
    print(depth, state.assumption.actionsToStr(), -eval(state))
    print(str(state.assumption))
    print("")
    print_assumption(state.assumption, depth+1)
    """


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





"""
Here is a solver for making the message replying to response.
"""
def solve(response):
    # static values
    solve.pid = vars(solve).setdefault('pid',-1)
    solve.eid = vars(solve).setdefault('eid',-1)
    solve.state = vars(solve).setdefault('state', None)
    #solve.confprm_once = vars(solve).setdefault('confprm_once', True)
    solve.logger = vars(solve).setdefault('logger', Logger())

    if response.code == 100:
        # 100 HELLO -> 101 NAME [NAME]
        return Message(101, ['NAME', CLIENT_NAME])
    elif response.code == 102:
        # 102 PLAYERID [0|1] -> NULL
        solve.pid = int(response.instructions[1])
        solve.eid = getEnemyId(solve.pid)
        solve.state = GameState(solve.pid)
        print("my_id", solve.pid)
        return None
    elif response.code == 200:
        # 200 OK -> NULL
        return None
    elif response.code == 201:
        # 201 MULTILINE -> NULL
        solve.state.reset()
        return None
    elif response.code == 202:
        # 202 LINENED -> NULL
        solve.state.setCurrentPlayerId(solve.state.myid)
        print(str(solve.state))
        # 204 DOPLAY -> 205 PLAY
        # start to think what should I do.
        # (ex. 205 PLAY 0 S 2-1)
        score = alphabeta(solve.state, ALPHABETA_DEPTH, float('-inf'), float('inf'))
        print("\n=============================")
        print_assumption(solve.state)
        print("===============================")
        action = solve.state.assumption.last_action
        #f = open("log.log", "a")
        #f.write(str(action)+"\n")
        #f.close()
        solve.logger.output(solve.state)
        if action.action_id == "5-3":
            return Message(205, ["PLAY", str(solve.pid), action.kind_id, action.action_id, action.trend_id])
        else:
            return Message(205, ["PLAY", str(solve.pid), action.kind_id, action.action_id])
    elif response.code == 204:
        # 204 DOPLAY -> 210 CONFPRM
        return Message(210, ["CONFPRM"])
    elif response.code == 206:
        # 206 PLAYED [01] [PAS][1-6]-[1-3] -> NULL
        return None
    elif response.code == 207:
        # 207 NEXT SEASON
        return None
    elif response.code == 211:
        # 211 RESOURCES [01] P[01] A[01] S[0-9]+ M[1-9]*[0-9]+ R[1-9]*[0-9]+ D[0-9]+
        id = int(response.instructions[1])
        solve.state.resources["P"][id] = int(response.instructions[2][1:])
        solve.state.max_workers["P"][id] = int(response.instructions[2][1:])
        solve.state.resources["A"][id] = int(response.instructions[3][1:])
        solve.state.max_workers["A"][id] = int(response.instructions[3][1:])
        solve.state.resources["S"][id] = int(response.instructions[4][1:])
        solve.state.max_workers["S"][id] = int(response.instructions[4][1:])
        solve.state.resources["M"][id] = int(response.instructions[5][1:])
        solve.state.resources["R"][id] = int(response.instructions[6][1:])
        solve.state.resources["D"][id] = int(response.instructions[7][1:])
        pass
    elif response.code == 212:
        # 212 BOARD [1-6]-[1-3][PAS][01]
        action_id = response.instructions[1]
        kind_id = response.instructions[2][0]
        pid = int(response.instructions[2][1])
        solve.state.board[action_id].append(Worker(pid, kind_id))
        solve.state.max_workers[kind_id][pid] += 1
        pass
    elif response.code == 213:
        # 213 SEASON [1-6][ab]
        solve.state.setSeasonId(response.instructions[1])
        pass
    elif response.code == 214:
        # 214 TREND T[123]
        solve.state.setTrendId(response.instructions[1])
        pass
    elif response.code == 215:
        # 215 score T[1-3] [0-9]+ [0-9]+
        trend_id = response.instructions[1]
        solve.state.scores[trend_id][0] = int(response.instructions[2])
        solve.state.scores[trend_id][1] = int(response.instructions[3])
    elif response.code == 216:
        # 216 STAETPLAYER [01]
        solve.state.setStartPlayerId(int(response.instructions[1]))
    elif response.code == 503:
        # 503 SCORE 10 20
        scores = [0, 0]
        scores[0] = (int(response.instructions[1]))
        scores[1] = (int(response.instructions[2]))
        solve.logger.output_score(scores)

"""
TEST CODE
"""
"""
pid = 0
state = GameState(pid)
state.current_player_id = pid
score = alphabeta(state, 10, float('-inf'), float('inf'))
print_assumption(state, 1)
exit(1)
"""

"""
*** IMPORTANT ***
System main Loop
Do not revisse here!!!
"""
# argment check
if len(sys.argv) >= 3:
    ip = sys.argv[2]
else:
    ip = SERVER_IP
if len(sys.argv) >= 4:
    port = sys.argv[3]
else:
    port = SERVER_PORT

# Connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port)) 
# main loop
while True:
    response_strings = client.recv(4096)
    # if message includes \n, execute respectly.
    for response_str in response_strings.split('\n'):
        if not response_str:
            continue
        print("recv:", response_str)
        response_message = convertToMessage(response_str)
        reply_message = solve(response_message)
        if reply_message is not None:
            print("send:" ,str(reply_message))
            client.send(str(reply_message))













