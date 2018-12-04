# -*- coding:utf-8 -*-

from classes.GameState import GameState
from classes.Message import Message
from ai import alphabeta

"""
Here is a solver for making the message replying to response.
"""
def solve(response):
    # static values
    solve.pid = vars(solve).setdefault('pid',-1)
    solve.eid = vars(solve).setdefault('eid',-1)
    solve.state = vars(solve).setdefault('state', None)
    #solve.confprm_once = vars(solve).setdefault('confprm_once', True)
    #solve.logger = vars(solve).setdefault('logger', Logger())

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
        #solve.logger.output_score(scores)