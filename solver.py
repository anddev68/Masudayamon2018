# -*- coding:utf-8 -*-

CLIENT_NAME = "Alice"

from classes.GameState import GameState
from classes.Message import Message
from ai import alphabeta

"""
204の時だけ，AIの思考に入る
@param state: GameState
@return action: Action どこに何を打つか
"""
def _think(state):
    print(str(state))
    score = alphabeta(state, ALPHABETA_DEPTH, float('-inf'), float('inf'))
    print("\n=============================")
    #print_assumption(solve.state)
    print("===============================")
    action = state.assumption.last_action


"""
サーバからのメッセージに対して適切な応答を返す
自分の番が来たらMULTILINEで情報取得し直しているので，TRENDとかPLAYEDの処理は不要かと
"""
def solve(message):
    # static values
    solve.pid = vars(solve).setdefault('pid',-1)
    solve.eid = vars(solve).setdefault('eid',-1)
    solve.state = vars(solve).setdefault('state', None)
    if message.code == 100:
        # 100 HELLO -> 101 NAME [NAME]
        return Message(101, ['NAME', CLIENT_NAME])
    elif message.code == 102:
        # 102 PLAYERID [0|1] -> NULL
        solve.pid = int(message.instructions[1])
        solve.eid = getEnemyId(solve.pid)
        solve.state = GameState(solve.pid)
        print("my_id", solve.pid)
        return None
    elif message.code == 200:
        # 200 OK -> NULL
        return None
    elif message.code == 201:
        # 201 MULTILINE -> NULL
        solve.state.reset()
        return None
    elif message.code == 202:
        # 202 LINENED -> NULL
        # 204 DOPLAY -> 205 PLAY
        # start to think what should I do.
        # (ex. 205 PLAY 0 S 2-1)
        solve.state.setCurrentPlayerId(solve.state.myid)
        action = _think(solve.state)
        if action.action_id == "5-3":
            return Message(205, ["PLAY", str(solve.pid), action.kind_id, action.action_id, action.trend_id])
        else:
            return Message(205, ["PLAY", str(solve.pid), action.kind_id, action.action_id])
    elif message.code == 203:
        # 203 EXIT -> OK
        return Message(200, ["OK"])
    elif message.code == 204:
        # 204 DOPLAY -> 210 CONFPRM
        return Message(210, ["CONFPRM"])
    elif message.code == 206:
        # 206 PLAYED [01] [PAS][1-6]-[1-3] -> NULL
        return None
    elif message.code == 207:
        # 207 NEXT SEASON
        return None
    elif message.code == 209:
        # 209 TREND T[0-3]
        return None
    elif message.code == 211:
        # 211 RESOURCES [01] P[01] A[01] S[0-9]+ M[1-9]*[0-9]+ R[1-9]*[0-9]+ D[0-9]+
        id = int(message.instructions[1])
        solve.state.resources["P"][id] = int(message.instructions[2][1:])
        solve.state.max_workers["P"][id] = int(message.instructions[2][1:])
        solve.state.resources["A"][id] = int(message.instructions[3][1:])
        solve.state.max_workers["A"][id] = int(message.instructions[3][1:])
        solve.state.resources["S"][id] = int(message.instructions[4][1:])
        solve.state.max_workers["S"][id] = int(message.instructions[4][1:])
        solve.state.resources["M"][id] = int(message.instructions[5][1:])
        solve.state.resources["R"][id] = int(message.instructions[6][1:])
        solve.state.resources["D"][id] = int(message.instructions[7][1:])
        pass
    elif message.code == 212:
        # 212 BOARD [1-6]-[1-3][PAS][01]
        action_id = message.instructions[1]
        kind_id = message.instructions[2][0]
        pid = int(message.instructions[2][1])
        solve.state.board[action_id].append(Worker(pid, kind_id))
        solve.state.max_workers[kind_id][pid] += 1
        pass
    elif message.code == 213:
        # 213 SEASON [1-6][ab]
        solve.state.setSeasonId(message.instructions[1])
        pass
    elif message.code == 214:
        # 214 TREND T[123]
        solve.state.setTrendId(message.instructions[1])
        pass
    elif message.code == 215:
        # 215 score T[1-3] [0-9]+ [0-9]+
        trend_id = message.instructions[1]
        solve.state.scores[trend_id][0] = int(message.instructions[2])
        solve.state.scores[trend_id][1] = int(message.instructions[3])
    elif message.code == 216:
        # 216 STAETPLAYER [01]
        solve.state.setStartPlayerId(int(message.instructions[1]))
    elif message.code == 503:
        # 503 SCORE 10 20
        scores = [0, 0]
        scores[0] = (int(message.instructions[1]))
        scores[1] = (int(message.instructions[2]))
        #solve.logger.output_score(scores)