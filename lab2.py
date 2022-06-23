# MIT 6.034 Lab 2: Games
# Written by 6.034 staff

from game_api import *
from boards import *
from toytree import GAME1

INF = float('inf')

# Please see wiki lab page for full description of functions and API.

#### Part 1: Utility Functions #################################################

def is_game_over_connectfour(board):
    """Returns True if game is over, otherwise False."""
    if board.count_pieces(current_player=None) >=42: return True
    currentState = board.get_all_chains(current_player=None)
    if len(currentState)>0:
        for i in range(len(currentState)):
            if len(currentState[i])>= 4:
                return True
    return False



def next_boards_connectfour(board):
    """Returns a list of ConnectFourBoard objects that could result from the
    next move, or an empty list if no moves can be made."""
    if is_game_over_connectfour(board): return []
    legalCols = [x for x in range(7) if not board.is_column_full(x)]
    possibleBoards = []
    for i in legalCols:
        possibleBoards.append(board.add_piece(i)) #this adds a new board to the list of possible boards
    return possibleBoards


def endgame_score_connectfour(board, is_current_player_maximizer):
    """Given an endgame board, returns 1000 if the maximizer has won,
    -1000 if the minimizer has won, or 0 in case of a tie."""
    if is_current_player_maximizer:
        currentState = board.get_all_chains(current_player=False)#false to get chains of maximizer
        if len(currentState)>0:
            for i in range(len(currentState)):
                if len(currentState[i])>= 4:
                    return -1000
            return 0
    else:
        currentState = board.get_all_chains(current_player=False)#false to get chains of maximizer
        if len(currentState)>0:
            for i in range(len(currentState)):
                if len(currentState[i])>= 4:
                    return 1000
            return 0



def endgame_score_connectfour_faster(board, is_current_player_maximizer):
    """Given an endgame board, returns an endgame score with abs(score) >= 1000,
    returning larger absolute scores for winning sooner."""
    if is_current_player_maximizer:
        currentState = board.get_all_chains(current_player=False)#false to get chains of maximizer
        if len(currentState)>0:
            for i in range(len(currentState)):
                if len(currentState[i])>= 4:
                    return -1000 - (43 - board.count_pieces()) #makes reward less negative as each move is made
            return 0
    else:
        currentState = board.get_all_chains(current_player=False)#false to get chains of maximizer
        if len(currentState)>0:
            for i in range(len(currentState)):
                if len(currentState[i])>= 4:
                    return 1000 + (43 - board.count_pieces())#makes reward less positive with each additional piece added to board (every move taken)
            return 0

def heuristic_connectfour(board, is_current_player_maximizer):
    """Given a non-endgame board, returns a heuristic score with
    abs(score) < 1000, where higher numbers indicate that the board is better
    for the maximizer."""

    def findHeur(board, is_current_player_maximizer):
        playerHeur = 0
        currentState = board.get_all_chains(is_current_player_maximizer)
        if len(currentState)>0:
            #points for number of chains (even singletons) is lower than continuous chains
            playerHeur += (len(currentState))
            for i in range(len(currentState)):
                if len(currentState[i]) == 2:
                    #points for number of chains must be lower than 2 singleton chains (so greater than 1+1)
                    playerHeur += 2
                if len(currentState[i]) == 3:
                    #points for number of chains must be lower than 2 singleton chains (so greater than 1+1)
                    # and greater than 1 singleton (+1) and one double(1+2), so must be 5
                    playerHeur += 5
        return playerHeur
    gameHeur = findHeur(board, is_current_player_maximizer) - findHeur(board, not is_current_player_maximizer)
    return gameHeur




# Now we can create AbstractGameState objects for Connect Four, using some of
# the functions you implemented above.  You can use the following examples to
# test your dfs and minimax implementations in Part 2.

# This AbstractGameState represents a new ConnectFourBoard, before the game has started:
state_starting_connectfour = AbstractGameState(snapshot = ConnectFourBoard(),
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "NEARLY_OVER" from boards.py:
state_NEARLY_OVER = AbstractGameState(snapshot = NEARLY_OVER,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)

# This AbstractGameState represents the ConnectFourBoard "BOARD_UHOH" from boards.py:
state_UHOH = AbstractGameState(snapshot = BOARD_UHOH,
                                 is_game_over_fn = is_game_over_connectfour,
                                 generate_next_states_fn = next_boards_connectfour,
                                 endgame_score_fn = endgame_score_connectfour_faster)


#### Part 2: Searching a Game Tree #############################################

# Note: Functions in Part 2 use the AbstractGameState API, not ConnectFourBoard.

def dfs_maximizing(state) :
    """Performs depth-first search to find path with highest endgame score.
    Returns a tuple containing:
     0. the best path (a list of AbstractGameState objects),
     1. the score of the leaf node (a number), and
     2. the number of static evaluations performed (a number)"""


    if state.is_game_over():
        possibleHigh = state.get_endgame_score(is_current_player_maximizer = True)
        currentEval = 1
        return ([state], possibleHigh, currentEval)
    else:
        pathToReturn = []
        evalTotal = 0
        possibleHigh = 0
        highest = -INF
        queue = state.generate_next_states()
        currentPath = [state]
        while len(queue) != 0:
            stateToExpand = queue.pop(0)
            (node, possibleHigh, currentEval) = dfs_maximizing(stateToExpand)
            if possibleHigh > highest:
                pathToReturn = currentPath + node
                highest = possibleHigh

            evalTotal += currentEval

        return (pathToReturn, highest, evalTotal)

# Uncomment the line below to try your dfs_maximizing on an
# AbstractGameState representing the games tree "GAME1" from toytree.py:

# pretty_print_dfs_type(dfs_maximizing(GAME1))


def minimax_endgame_search(state, maximize=True) :
    """Performs minimax search, searching all leaf nodes and statically
    evaluating all endgame scores.  Same return type as dfs_maximizing."""

    evalNum = 0
    leafScore = 0
    pathToReturn = []
    #check for base case
    if state.is_game_over():
        pathToReturn = [state]
        evalNum += 1
        leafScore = state.get_endgame_score(is_current_player_maximizer=True)
        return (pathToReturn, leafScore, evalNum)

    nextStates = state.generate_next_states()
    totalEvals =0

    if maximize == True:
        highScore = -INF
        for next in nextStates:
            (leaf, leafScore, evalNum) = minimax_endgame_search(next, False)
            totalEvals +=evalNum
            if leafScore > highScore:
                pathToReturn = [state] + leaf
                highScore = leafScore
        return (pathToReturn, highScore, totalEvals)
    else:
        lowScore = INF
        for next in nextStates:
            (leaf, leafScore, evalNum) = minimax_endgame_search(next, True)
            totalEvals +=evalNum
            if leafScore < lowScore:
                pathToReturn = [state] + leaf
                lowScore = leafScore
        return (pathToReturn, lowScore, totalEvals)


# Uncomment the line below to try your minimax_endgame_search on an
# AbstractGameState representing the ConnectFourBoard "NEARLY_OVER" from boards.py:

# pretty_print_dfs_type(minimax_endgame_search(state_NEARLY_OVER))


def minimax_search(state, heuristic_fn=always_zero, depth_limit=INF, maximize=True) :
    """Performs standard minimax search. Same return type as dfs_maximizing."""

    #check for base case
    if state.is_game_over():
        #evalNum += 1
        leafScore = state.get_endgame_score(is_current_player_maximizer = maximize)
        return ([state], leafScore, 1)
    #check for depth is at limit
    if depth_limit==0:
        #evalNum += 1
        heurScore = heuristic_connectfour(state.get_snapshot(), maximize)
        return ([state], heurScore, 1)
    nextStates = state.generate_next_states()
    leafScore = 0
    pathToReturn = []
    totalEvals =0
    if maximize == True:
        highScore = -INF
        for l in nextStates:
            (leaf, currentScore, evalNum) = minimax_search(l, heuristic_fn, depth_limit-1, False)
            totalEvals +=evalNum
            if currentScore > highScore:
                pathToReturn = [state] + leaf
                highScore = currentScore
        return (pathToReturn, highScore, totalEvals)
    else:
        lowScore = +INF
        for l in nextStates:
            (leaf, currentScore, evalNum) = minimax_search(l, heuristic_fn, depth_limit-1, True)
            totalEvals +=evalNum
            if currentScore < lowScore:
                pathToReturn = [state] + leaf
                lowScore = currentScore
        return (pathToReturn, lowScore, totalEvals)


# Uncomment the line below to try minimax_search with "BOARD_UHOH" and
# depth_limit=1. Try increasing the value of depth_limit to see what happens:

# pretty_print_dfs_type(minimax_search(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=1))


def minimax_search_alphabeta(state, alpha=-INF, beta=INF, heuristic_fn=always_zero,
                             depth_limit=INF, maximize=True) :
    """"Performs minimax with alpha-beta pruning. Same return type
    as dfs_maximizing."""
    if state.is_game_over():
        leafScore = state.get_endgame_score(is_current_player_maximizer = maximize)
        return ([state], leafScore, 1)
    if not (depth_limit):
        endScore = heuristic_fn(state.get_snapshot(), maximize)
        return ([state], endScore, 1)
    totalEvals =0
    nextStates = state.generate_next_states()
    bestScore = 0
    pathToReturn = []
    current = [state]
    if maximize == True:
        bestScore = -INF
        for i in nextStates:
            (l, currentScore, num) = minimax_search_alphabeta(i, alpha, beta, heuristic_fn, depth_limit - 1, False)
            if currentScore > bestScore:
                bestScore = currentScore
                pathToReturn = current + l
            totalEvals += num
            if bestScore > alpha:
                alpha = bestScore
            if alpha >= beta:
                return (pathToReturn, alpha, totalEvals)
        return (pathToReturn, bestScore, totalEvals)
    else:
        bestScore = +INF
        for i in nextStates:
            (l, currentScore, num) = minimax_search_alphabeta(i, alpha, beta, heuristic_fn, depth_limit - 1, True)
            if currentScore < bestScore:
                pathToReturn = current + l
                bestScore = currentScore
            totalEvals += num
            if bestScore < beta:
                beta = bestScore
            if alpha >= beta:
                return (pathToReturn, beta, totalEvals)
        return (pathToReturn, bestScore, totalEvals)



# Uncomment the line below to try minimax_search_alphabeta with "BOARD_UHOH" and
# depth_limit=4. Compare with the number of evaluations from minimax_search for
# different values of depth_limit.

# pretty_print_dfs_type(minimax_search_alphabeta(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4))


def progressive_deepening(state, heuristic_fn=always_zero, depth_limit=INF,
                          maximize=True) :
    """Runs minimax with alpha-beta pruning. At each level, updates anytime_value
    with the tuple returned from minimax_search_alphabeta. Returns anytime_value."""
    at = AnytimeValue()
    for level in range(1, depth_limit+1):
        endOfGame = minimax_search_alphabeta(state, -INF, INF, heuristic_fn, level, maximize)
        at.set_value(endOfGame)
    return at


# Uncomment the line below to try progressive_deepening with "BOARD_UHOH" and
# depth_limit=4. Compare the total number of evaluations with the number of
# evaluations from minimax_search or minimax_search_alphabeta.

# progressive_deepening(state_UHOH, heuristic_fn=heuristic_connectfour, depth_limit=4).pretty_print()


# Progressive deepening is NOT optional. However, you may find that
#  the tests for progressive deepening take a long time. If you would
#  like to temporarily bypass them, set this variable False. You will,
#  of course, need to set this back to True to pass all of the local
#  and online tests.
TEST_PROGRESSIVE_DEEPENING = True
if not TEST_PROGRESSIVE_DEEPENING:
    def not_implemented(*args): raise NotImplementedError
    progressive_deepening = not_implemented


#### Part 3: Multiple Choice ###################################################

ANSWER_1 = '4'

ANSWER_2 = '1'

ANSWER_3 = '4'

ANSWER_4 = '5'


#### SURVEY ###################################################

NAME = "Skylar Kolisko"
COLLABORATORS = "None"
HOW_MANY_HOURS_THIS_LAB_TOOK = "8"
WHAT_I_FOUND_INTERESTING = "All"
WHAT_I_FOUND_BORING = "None"
SUGGESTIONS = "None"
