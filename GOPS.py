from pulp import *
from itertools import combinations

#number of cards used i.e. 1, 2, 3, ..., n
n = 5

#cards available in the game
cards = list(range(1, n+1, 1))

#dictionary for (player1_deck, player2_deck, deck) : {"value"}
matrix_game = {}

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

def avg(lst):
    return sum(lst)/len(lst)

#creates decks for subgames
#m number of cards used in which subgame
def subgames(m):
    subdecks = [list(c) for c in combinations(cards, m)]
    #every possible subgame of size m for deck of n cards
    subgames = [(v, y, p)
                 for v in subdecks for y in subdecks for p in subdecks]
    return subgames

#values for subgames of size 1
def value_of_1():
    decks = subgames(1)
    #for subgames of size 1 we know the value of the game
    #it's just vale of the card in the middle * sing(player1_card-player2_card)
    for p1, p2, deck in decks:
        matrix_game[tuple(p1 + p2 + deck)] = deck[0] * sign(p1[0]-p2[0])


def solve_payoff_matrix(payoff_matrix, return_strategy = False):
    prob = LpProblem("Payoff_Matrix", LpMaximize)

    n = len(payoff_matrix)

    p = [LpVariable(f"p{i}", lowBound=0) for i in range(n)]
    v = LpVariable("v")

    prob += v
    prob += lpSum(p) == 1

    for i in range(n):
        prob += lpSum(payoff_matrix[j][i]*p[j] for j in range(n)) >= v

    prob.solve(PULP_CBC_CMD(msg=False))

    game_value = value(v)

    if return_strategy:
            probabilities = [value(p[i]) for i in range(n)]
            return probabilities, game_value

    return game_value    

#size_V is current size of subdeck it might be he number from 2 to n
def function(size_V):
    decks = subgames(size_V)

    for V_deck, Y_deck, P_deck in decks:
        #list for values for each card in middle deck
        value_list = []
        strategy_list = []
        #for each card in middle deck we create matrix with elements such that
        # X_(i, j) = P_k*sign(V_i - V_j) + f(V\V_i, Y\Y_j, P\P_k), where f(...) is already know from previous step
        #then we use linear programming to find the value of the game which is f(V, Y, P)

        V_deck = tuple(V_deck)
        Y_deck = tuple(Y_deck)
        P_deck = tuple(P_deck)

        for k, P_k in enumerate(P_deck):
            
            payoff_matrix = [[0]*size_V for i in range(size_V)]

            for i, V_i in enumerate(V_deck):
                for j, Y_j in enumerate(Y_deck):

                    subV = V_deck[:i] + V_deck[i+1:]
                    subY = Y_deck[:j] + Y_deck[j+1:]
                    subP = P_deck[:k] + P_deck[k+1:]

                    key = subV + subY + subP
                    #here we have the final form of our payoff matrix
                    payoff_matrix[i][j] = P_k * sign(V_i - Y_j) + matrix_game[key]
            
            if size_V == n:
                probabilities, value = solve_payoff_matrix(payoff_matrix, True)
                strategy_list.append(probabilities)
            else:
                value = solve_payoff_matrix(payoff_matrix)

            value_list.append(value)

        if size_V == n:
            matrix_game[tuple(V_deck + Y_deck + P_deck)] = {"value": avg(value_list), 
                                                            "strategy": strategy_list
                                                            }
        else:
            matrix_game[tuple(V_deck + Y_deck + P_deck)] = avg(value_list)

def result():
    value_of_1()
    for size in range(2, n+1):
        function(size)
    
    V_deck = tuple(cards)
    Y_deck = tuple(cards)
    P_deck = tuple(cards)

    key = V_deck + Y_deck + P_deck
    final_game = matrix_game[key]

    print("\nPlayer 1 strategy (rows = player cards, columns = middle deck cards):\n")

    print("     ", end="")
    for card in P_deck:
        print(f"{card:>8}", end="")
    print()

    for i, row_card in enumerate(V_deck):
        print(f"{row_card:>3} | ", end="")
        for j in range(len(P_deck)):
            prob = final_game["strategy"][j][i]
            print(f"{prob:8.4f}", end="")
        print()

result()