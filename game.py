import networkx as nx
#from State import *
from matplotlib import pyplot as plt
import random
global MAX_DEPTH
MAX_DEPTH = 8
global input_file
input_file = "input.txt"
global graph_env
graph_env = None
game_mode = 3
# game_mode = 'adversarial' if game_mode == 1 else 'semi-cooperative' if game_mode == 2 else 'fully-cooperative'



class State:
    def __init__(self, treeDepth:int, agent1Node: int, agent1Score:int, agent2Node:int,agent2Score:int, visitedNodes:list,flag):
        self.treeDepth = treeDepth
        self.agent1Node=agent1Node
        self.agent2Node=agent2Node
        self.agent1Score=agent1Score
        self.agent2Score=agent2Score
        self.visitedNodes = visitedNodes
        self.flag=flag

    def __hash__(self):
        #for dictionary purposes
        return hash((self.agent1Node, self.agent1Score,self.agent2Node, self.agent2Score,str(self.visitedNodes),self.flag))

    def __eq__(self, other):
        #for dictionary purposes
        if other == None:
            return False
        return (self.agent1Node, self.agent1Score,self.agent2Node,self.agent2Score,str(self.visitedNodes.sort()),self.flag) == (other.agent1Node, other.agent1Score,other.agent2Node,other.agent2Score,str(other.visitedNodes.sort()),other.flag)
        
        
    def utility(self,flag):
        if game_mode == 1:
            if flag>0:
                return self.agent1Score-self.agent2Score
            else:
                return self.agent2Score-self.agent1Score
        else:
            if game_mode==2:
                if flag>0:
                    return [self.agent1Score,self.agent2Score]
                else:
                    return [self.agent2Score , self.agent2Score]
            else:
                return (self.agent1Score+self.agent2Score)

                               
    def isGoal(self):
        return self.agent1Score + self.agent2Score == graph_env.graph['total_people']
        
def isTerminal(state,flag):
        if state.treeDepth > MAX_DEPTH:
            return True
        if state.agent1Score + state.agent2Score == graph_env.graph['total_people']:
            return True
        if len(expand(state,flag)) == 1 and len(expand(state,-1*flag)) == 1:
            return True
        if isVisited.get(state) != None:
            return True
        return False



def maxMaxSearchSemi(state,flag,p1_or_p2):
    actions = expand(state, flag)
    # print("ACTIONS: ")
    # for a in actions:
        # print("p1 node: ", a.agent1Node, " p1 score: ", a.agent1Score, " p2 node: ", a.agent2Node, " p2 score: ", a.agent2Score, " visited: ", a.visitedNodes, " utility: ", a.utility(p1_or_p2))
    best_score = -float('inf')
    opponents_best= -float('inf')
    best = [best_score,opponents_best]
    best_action = None
    for a in actions:
        v , opponent = max_value_without_beta_semi(a, (-1)*flag,p1_or_p2)
        print("p1 node: ", a.agent1Node, " p1 score: ", a.agent1Score, " p2 node: ", a.agent2Node, " p2 score: ", a.agent2Score, " visited: ", a.visitedNodes,  " v: ", v)
        # print("HERE MIN IN STATE (", a.agent1Node, ",", a.agent2Node, ") DEPTH ", " IS ", v)
        if v > best[0]:
            best = [v,opponent]
            best_action = a
        if v == best[0]:
            #tie breaker
            if best_action == None or best[1] < opponent:
                print("TIE BROKEN :" , "v: " ,v, " opponent: ",opponent, "best[0]:", best[0],"best[1]:",best[1])
                best = [v,opponent]
                best_action = a
    return best_action

def max_value_without_beta_semi(state,flag,p1_or_p2):
    #Returns list of 2 elements: [my best score, opponent's best score]
    if isTerminal(state,flag):
        return state.utility(p1_or_p2)

    res=[-float('inf'),-float('inf')]
    successors = expand(state,flag)

    for s in successors:
        max_val, max_opponent = max_value_without_beta_semi(s,(flag)*(-1),p1_or_p2)
        if max_val > res[0]:
            res=[max_val , max_opponent]
        if max_val == res[0]:
            #tie breaker
            if res[1] < max_opponent:
                res[1]=max_opponent
    return res



def maxMax_fully_cop(state,flag,p1_or_p2):
    actions = expand(state, flag)
    best_score = -float('inf')
    best_action = None
    for a in actions:
        v = max_value_fully_cop(a,(-1)*flag,p1_or_p2)
        print("p1 node: ", a.agent1Node, " p1 score: ", a.agent1Score, " p2 node: ", a.agent2Node, " p2 score: ", a.agent2Score, " visited: ", a.visitedNodes,  " v: ", v)
        if v > best_score:
            best_score = v
            best_action = a
    
    return best_action

def max_value_fully_cop(state,flag,p1_or_p2):
    if isTerminal(state,flag):
        return state.utility(p1_or_p2)

    v = -float('inf')
    successors = expand(state,flag)

    for s in successors:
        v = max(v, max_value_fully_cop(s,(flag)*(-1),p1_or_p2))
    return v


def alpha_beta_search(state,flag,p1_or_p2):
    actions = expand(state, flag)
    print("ACTIONS: ")
    best_score = -float('inf')
    beta = float('inf')
    best_action = None
    for a in actions:
        v = min_value(a, best_score, beta, (-1)*flag,p1_or_p2)
        print("p1 node: ", a.agent1Node, " p1 score: ", a.agent1Score, " p2 node: ", a.agent2Node, " p2 score: ", a.agent2Score, " visited: ", a.visitedNodes,  " v: ", v)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


def max_value(state, alpha, beta,flag, p1_or_p2):
    if isTerminal(state,flag):
        return state.utility(p1_or_p2)

    v = -float('inf')
    successors = expand(state,flag)

    for s in successors:
        v = max(v, min_value(s, alpha, beta,(flag)*(-1),p1_or_p2))
        if v >= beta:
            return v
        alpha = max(alpha, v)
    return v
       

def min_value(state, alpha, beta,flag,p1_or_p2):
        if isTerminal(state,flag):
            return state.utility(p1_or_p2)

        v = float('inf')
        successors = expand(state,flag)

        for s in successors:
            v = min(v, max_value(s, alpha, beta,(flag)*(-1),p1_or_p2))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v



def expand(state,flag):
    children = []
    noOp=State(state.treeDepth + 1, state.agent1Node, state.agent1Score, state.agent2Node, state.agent2Score, state.visitedNodes, flag)
    children.append(noOp)
    if flag>0:
        currNode = state.agent1Node
    else:
        currNode = state.agent2Node

    for neighbor in graph_env.neighbors(currNode):
        if not graph_env.nodes[neighbor]['breakable'] or neighbor not in state.visitedNodes:
            #making sure the neighbor is not breakable and the other agent is not in the neighbor
            if flag>0:
                if neighbor == state.agent2Node and graph_env.nodes[neighbor]['breakable']:
                    continue
            else:
                if neighbor == state.agent1Node and graph_env.nodes[neighbor]['breakable']:
                    continue

            #if flag>0: means agent 1 is playing, so we need to update agent 1 score and node
            if neighbor not in state.visitedNodes:
                if flag>0:
                    newNode = State(state.treeDepth + 1, neighbor, state.agent1Score + graph_env.nodes[neighbor]['num_of_people'], state.agent2Node, state.agent2Score, state.visitedNodes + [neighbor],flag)
                else:
                    newNode = State(state.treeDepth + 1, state.agent1Node, state.agent1Score, neighbor, state.agent2Score + graph_env.nodes[neighbor]['num_of_people'], state.visitedNodes + [neighbor],flag)
            else:
                #visited already, so we don't need to update the score
                if flag>0:
                    newNode = State(state.treeDepth + 1, neighbor, state.agent1Score, state.agent2Node, state.agent2Score, state.visitedNodes,flag)
                else:
                    newNode = State(state.treeDepth + 1, state.agent1Node, state.agent1Score, neighbor, state.agent2Score, state.visitedNodes,flag)
            children.append(newNode)
    return children


def print_graph(graph: nx.Graph, p1_location: int, p2_location: int):
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, nodelist=[node for node in graph.nodes if graph.nodes[node]['breakable']], node_color='r')
    nx.draw_networkx_nodes(graph, pos, nodelist=[node for node in graph.nodes if not graph.nodes[node]['breakable']], node_color='b')
    nx.draw_networkx_labels(graph, pos, labels={node: f"{node} ({graph.nodes[node]['num_of_people']})" for node in graph.nodes})
    nx.draw_networkx_edges(graph, pos)
    nx.draw_networkx_nodes(graph, pos, nodelist=[p1_location], node_color='g')
    nx.draw_networkx_nodes(graph, pos, nodelist=[p2_location], node_color='y')
    plt.show()


def parse(file:str):
    graph = nx.Graph()
    #open file
    f = open(file, 'r')
    #first line after "#N" is the number of nodes
    num_nodes = int(f.readline().split()[1])
    #next num_nodes lines are the nodes
    for i in range(num_nodes):
        line = f.readline().split()
        breakable = True if 'B'in line else False
        number_of_people = 0
        for cell in line:
            if 'P' in cell:
                number_of_people = int(cell[1:])

        graph.add_node(i+1, breakable=breakable, num_of_people=number_of_people)

    #add to the graph field for total number of people
    graph.graph['total_people'] = sum([graph.nodes[node]['num_of_people'] for node in graph.nodes])
    #read and throw away the next line
    f.readline()

    #rest of the file is the edges
    for line in f:
        line = line.split()
        graph.add_edge(int(line[1]), int(line[2]))

    return graph


def simulate():
    print("Choose game mode:")
    print("1. Adversarial (S = S1 - S2)")
    print("2. semi-cooperative (S = S)")
    print("3. fully cooperative (S = S1 + S2)")
    game_mode = int(input())
    #if game_mode == 1: print("Game mode: Adversarial") if game_mode == 2: print("Game mode: Semi-cooperative") if game_mode == 3: print("Game mode: Fully-cooperative")
    # print("Game mode: Adversarial" if game_mode == 1 else "Game mode: Semi-cooperative" if game_mode == 2 else "Game mode: Fully-cooperative")
    
   
    global graph_env

    print("enter input file name:")
    input_file = input()
    graph_env = parse(input_file)
    

    print("Choose player 1 starting node:")
    player1_start = int(input())
    # player1_start = 1
    print("Choose player 2 starting node:")
    player2_start = int(input())
    # player2_start = 1
    print("Player 1 starting node: ", player1_start)
    print("Player 2 starting node: ", player2_start)

    print_graph(graph_env, player1_start, player2_start)

    if player1_start == player2_start:
        p1score = graph_env.nodes[player1_start]['num_of_people']
        p2score = 0
    else:
        p1score = graph_env.nodes[player1_start]['num_of_people']
        p2score = graph_env.nodes[player2_start]['num_of_people']           

    action = State(0, player1_start,p1score , player2_start, p2score, list(set([player1_start, player2_start])),1)
    flag = 1
    global isVisited
    isVisited={}
    stuckCounter=0
    p1_or_p2 = 1 # 1 for p1, -1 for p2
    turns = 0
    while(True):
        turns+=1
        if game_mode ==1:
            action = alpha_beta_search(action, flag, p1_or_p2)
        elif game_mode==2:
            action = maxMaxSearchSemi(action, flag, p1_or_p2)
        else:
            action = maxMax_fully_cop(action, flag, p1_or_p2)
        #remove duplicate nodes
        action.visitedNodes=list(set(action.visitedNodes))
    
        p1_or_p2 = p1_or_p2 * -1
        flag=flag*-1
        if turns == 3:
            x=3
        if action == None:
            if stuckCounter == 2:
                print("stuck")
                break
            else:
                stuckCounter+=1
                action=prevAction
                continue
        if(isVisited.get(action)==None):
            isVisited[action]=1
        else:
            print("visited before")
            break
        action.treeDepth=0
        print("Best action chosen")
        print("Agent 1 node : ", action.agent1Node, " score : ", action.agent1Score)
        print("Agent 2 node : ", action.agent2Node, " score : ", action.agent2Score)
        print("-------------------------------")
        if action.isGoal():
            print("reached goal")
            break
        prevAction = action
        stuckCounter=0
    print("DONE :)")

def main():
    simulate()

if __name__ == "__main__":
    main()
    
