from random import shuffle
from random import random
from random import randint
from copy import deepcopy
from functools import reduce


#MATH
def flatten(l):
    return [item for sublist in l for item in sublist]

#PLAYERS
def player(hand, budget):
    return {'hand': hand, 'budget': budget }

def visitors(hand):
    return {'hand': hand, 'claimed_cards':[]}

#PROSPECTS
def boy(rank):
    return {'rank': rank, 'sex': 'm'}

def girl(rank):
    return {'rank': rank, 'sex': 'f'}

def suits(value):
    return [{'rank': value, 'sex': 'm'}, {'rank': value, 'sex': 'f'}] * 2

#CARDS
def card(rank, sex):
    return {'rank': rank, 'sex': sex }

def claimed_visitor_card(owner, p_card, v_card, money): # owner: 0 = visitor, 1 = player1, 2 = player2
    return { 'owner': owner, 'p_card': p_card, 'v_card': v_card, 'money': money}

def get_deck():
    d = flatten([suits(a + 1) for a in range(7)])
    shuffle(d)
    return deepcopy(d)


def deal_from(deck, how_many):
    if len(deck) < how_many:
        return []
    popped = deck[0:how_many]
    del deck[0:how_many]
    return popped


#MONEY
def money(shem, gelt):
    return {"shem": shem, "gelt": gelt}

def is_free(money):
    return money["shem"] == 0 and money["gelt"] == 0

def is_more(m1, m2):
    return True if m1["shem"] + m1["gelt"] > m2["shem"] + m2["gelt"] else False

def flip(money):
    return {"shem": money["gelt"], "gelt": money["shem"]}

def kind(money):
    return "gelt" if (money["shem"] == 0) else "shem"

def add_money(m1, m2):
    return money(m1["shem"] + m2["shem"], m1["gelt"] + m2["gelt"])

def subtract_money(m1, m2):
    return {"shem": m1["shem"] - m2["shem"], "gelt": m1["gelt"] - m2["gelt"]}

def multiply_money(m, factor):
    return {"shem": m["shem"] * factor, "gelt": m["gelt"] * factor}

def combine_resources(money):
    return money['shem'] + money['gelt']


#STEALING

def expected_steal_reward(client, e_item):
    if client['rank'] < e_item['player_card']['rank']:
        return None
    if chance_of_match(client, e_item['vis_card']) is None:
        return None
    reward = e_item['money']
    if(client['rank'] > e_item['vis_card']['rank'] and e_item['money']['gelt'] is 0):
        reward = flip(reward)
    # take into account that a steal costs opponent money
    reward = multiply_money(reward, 2)
    reward = multiply_money(reward, chance_of_match(client, e_item['vis_card']))
    reward = subtract_money(reward, money(2, 0))  # take in account the cost of stealing
    return reward

#BUDGET

def starting_budget():
    return money(2, 2)

def distribute_winnings():
    for c in the_visitors['claimed_cards']:
        c['owner']['budget'] = add_money(c['owner']['budget'], c['money'])
    the_visitors['claimed_cards'] = []
    
def resource_count(budget):
    return budget['shem'] + budget['gelt']

def can_afford(budget, cost):
    return budget['shem'] >= cost['shem'] and budget['gelt'] >= cost['gelt']


#AI


def match_cost(client, visitor):
    if client['sex'] == visitor['sex']:
        return None
    marrying_down = client['rank'] - visitor['rank']
    return {"shem": max(0, marrying_down), "gelt": max(0, -marrying_down)}


def chance_of_match(client, visitor):
    if client['sex'] == visitor['sex']:
        return None
    difference = abs(client["rank"] - visitor["rank"])
    if difference == 0:
        return 1
    return max(0, float(5 - max(2, difference))/4)


def expected_match_reward(client, visitor):
    cost = actual_match_profit(client, visitor)
    if cost is None:
        return None
    return multiply_money(flip(cost), chance_of_match(client, visitor))


def actual_match_profit(client, visitor):
    cost = actual_match_reward(client, visitor)
    if cost is None or is_free(cost):
        return cost
    return max(0, subtract_money(cost, match_cost(client, visitor)))
    

def actual_match_reward(client, visitor):
    cost = match_cost(client, visitor)
    if cost is None:
        return None
    if is_free(cost):
        return {"shem": 0, "gelt": 2.5} 
    cost[kind(cost)] += visitor["rank"]
    return cost


def print_cost_and_reward(client, visitor):
    m = match_cost(client, visitor)
    r = expected_match_reward(client, visitor)
    vals = (client['rank'], visitor['rank'], m, chance_of_match(client, visitor), r)
    print "%s client to marry a %s visitor: cost %s, chance %s, expected rwd %s" % vals

#print_cost_and_reward(boy(4.0), girl(6.0))

    
#ETHAN WORK HERE
### TK for v2: 
###     stealing a match
###     blocking a choice 

def card_match(player_idx, vis_idx, reward):
    return {'player_idx': player_idx, 'vis_idx': vis_idx, 'reward':reward}


def find_best_play(player):
    player_hand = player['hand']
    best_play = None
    ### Check the visitor cards on the table
    for player_idx, player_card in enumerate(player_hand):
        for vis_idx, visitor_card in enumerate(the_visitors['hand']):
            cost = match_cost(player_card, visitor_card)
            if cost is not None and not can_afford(player['budget'], cost):
                continue
            reward = expected_match_reward(player_card, visitor_card)
            if reward != None:
                if best_play == None or is_more(reward, best_play['reward']):
                    best_play = card_match(player_idx, vis_idx, reward)
    ### Check visitor cards claimed by opponent for possible steal 
    print "Add in checking claimed visitor cards for stealing"
    return best_play ### doing this for now, later add back stealing
#    opponents_escrow = []
#    if player_hand is my_hand:
#        opponents_escrow = your_budget['escrow']
#    else:
#        opponents_escrow = my_budget['escrow']
#    for player_idx, player_card in enumerate(player_hand):
#        for escrow_idx, e_item in enumerate(opponents_escrow):
#            reward = expected_steal_reward(player_card, e_item)             
#            if reward is not None:
#                if best_play == None or combine_resources(reward) >= combine_resources(best_play['reward']):
#                    print "Planning to steal card!"
#                    best_play = card_match(player_idx, escrow_idx, reward)  
#    return best_play

def take_turn(player):
    best_play = find_best_play(player)
    if best_play is None:
        return
    hand = player['hand']
    budget = player['budget']
    vis_hand = the_visitors['hand']
    p_card = hand[best_play['player_idx']]
    v_card = vis_hand[best_play['vis_idx']]
    budget = subtract_money(budget, match_cost(p_card,v_card))
    if random() <= chance_of_match(p_card,v_card):
        # (card, owner, player_card, money)
        the_visitors['claimed_cards'].append(claimed_visitor_card(player, p_card, v_card,actual_match_reward(p_card,v_card)))
        del vis_hand[best_play['vis_idx']] 
    del hand[best_play['player_idx']]      

    
def play_round(first_player):    
    print "\n\tTURN START:\n\tMy hand:\t%s \n\tYour hand:\t%s \n\tVisitors:\t%s" % (player1['hand'], player2['hand'], the_visitors['hand'])
    take_turn(first_player)    
    if first_player is player1:
        take_turn(player2) 
    else: 
        take_turn(player1) 
    # print "\n\tTURN END:\n\tMy hand:\t%s \n\tYour hand:\t%s \n\tVisitors:\t%s" % (my_hand, your_hand, visitors)
    if find_best_play(player1) is not None or find_best_play(player2) is not None:
        play_round(first_player)    
   

def end_round_bookkeeping():
    ### deal cards
    global the_visitors
    the_visitors['hand'].extend(deal_from(visitor_cards, num_visitors))
    player1['hand'].extend(deal_from(client_cards, handsize - len(player1['hand'])))
    player2['hand'].extend(deal_from(client_cards, handsize - len(player2['hand'])))
    distribute_winnings()
    print "\n\tBUDGET:\n\tMy budget:\t%s\n\tYour budget:\t%s" % (player1['budget'], player2['budget'])

    
# the winner is whoever has the most total resources (i.e. shem + gelt)
def determine_leader(p1, p2):
    player1_res = resource_count(p1['budget']) 
    player2_res = resource_count(p2['budget']) 
    if player1_res == player2_res:
        return None
    elif player1_res > player2_res:
        return player1
    else:
        return player2
 

def determine_first_player(p1, p2):
    leader = determine_leader(p1, p2)
    if leader is player1:
        return player2
    elif leader == player2:
        return player1
    elif 1 == randint(1,2):
        return player1
    else: 
        return player2
        
    
def play_game():  
    print "STARTING GAME"
    count = 1
    while len(client_cards) > 0 and len(visitor_cards) > 0 and len(player1['hand']) == handsize and len(player2['hand']) == handsize: 
        print "\nRound %s:" % (count)
        print "\t\t%s remain in client cards, %s in visitor_cards" % (len(client_cards), len(visitor_cards))
        play_round(determine_first_player(player1, player2))
        end_round_bookkeeping()
        count += 1   
    print "\nGAME OVER: Player %s won (0 indicates tie)\n" % ("1" if player1 is determine_leader(player1, player2) else "2"  )

def reset_game():
    global client_cards, visitor_cards, the_visitors, player1, player2
    client_cards = get_deck()
    visitor_cards = get_deck()
    player1 = player(deal_from(client_cards, handsize), starting_budget())
    player2 = player(deal_from(client_cards, handsize), starting_budget())
    the_visitors = visitors(deal_from(visitor_cards, num_visitors))
    
def game_result():
    return { 'tie':0,'player1':0,'player2':0 }

def add_game_result(result, leader):
    if leader == None:
        result['tie'] += 1
    elif leader == player1:
        result['player1'] += 1
    else:
        result['player2'] += 1
    return result    

def run_analysis():
    total_results = game_result()
    for x in range(0, 1000):
        play_game()
        add_game_result(total_results, determine_leader(player1, player2))
        reset_game()
    print total_results
    
    
### Globals 
client_cards = get_deck()
visitor_cards = get_deck()

handsize = 4
num_visitors = 2

player1 = player(deal_from(client_cards, handsize), starting_budget())
player2 = player(deal_from(client_cards, handsize), starting_budget()) 

the_visitors = visitors(deal_from(visitor_cards, num_visitors))
        
    
run_analysis()


#BEN WORK HERE







