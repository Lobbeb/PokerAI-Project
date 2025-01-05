import math
from collections import Counter


'''Works by tracking the cards that has been removed from the deck and by evaluating the players hand, with this it can track the probability 
    of an opponent having a better hand than the user. The class does it accuratly except for highcard and if the opponent would have a straight_flush as it is calculated within the straight probability and flush probability'''
class prob_calculator:
    def __init__(self):
        self.RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        self.card_in_deck = 52
        self.removed_cards = set()
        self.rank_set = {'A':4, '2':4, '3':4, '4':4, '5':4, '6':4, '7':4, '8':4, '9':4, 'T':4, 'J':4, 'Q':4, 'K':4}
        self.suit_set = {'s': 13,'h':13,'c':13,'d':13}
    
    def update(self,cards =None):
        if cards:
            self.update_removed_cards(cards)
        #print(f'removed_cards {self.removed_cards}')
        self.reset()
        self.update_deck(self.removed_cards)
        self.update_rank_set(self.removed_cards)
        self.update_suit_set(self.removed_cards)

        
    def reset(self):
        self.reset_deck()
        self.reset_rank_set()
        self.reset_suit_set()

    def update_deck(self,cards):
        self.card_in_deck -= len(cards) 
        #print(f'cards_in_deck {self.card_in_deck}')
    
    def reset_deck(self):
        self.card_in_deck = 52

    def update_removed_cards(self,cards):
        '''Appends all specified cards to a set'''
        for c in cards:
            self.removed_cards.add(c)
        

    def reset_removed_cards(self):
        '''clears the removed cards'''
        self.removed_cards.clear()

    def update_suit_set(self, cards):
        '''Removes one instace of suit given cards'''
        for card in cards:
            self.suit_set[card[-1]] = self.suit_set[card[-1]] -1
        #print(f'siut_set {self.suit_set}')
    
    def reset_suit_set(self):
        '''sets the numbers of cards in each suit to its default value'''
        self.suit_set = {'s': 13,'h':13,'c':13,'d':13}



    def update_rank_set(self, cards):
        '''Removes one instace of each rank in cards'''
        for card in cards:
            self.rank_set[card[:-1]] = self.rank_set[card[:-1]] -1
        #print(f'rank_set {self.rank_set}')
    
    def reset_rank_set(self):
        '''sets the numbers of cards in each rank to its default value'''
        self.rank_set = {'A':4, '2':4, '3':4, '4':4, '5':4, '6':4, '7':4, '8':4, '9':4, 'T':4, 'J':4, 'Q':4, 'K':4}

    def print_rank_set(self):
        print(self.rank_set)

    def evaluate_hand(self,hand):
        '''calculates what type of hand and gives it a value, returns the type of hand ("Straight Flush", "Four of a Kind", ... "Pair") 
           and the value of the hand. the better hand the higher the value'''
        # Parse the hand into rank and suit
        ranks = [card[:-1] for card in hand]
        suits = [card[-1] for card in hand]
        value = -1

        # Count the occurrences of each rank and suit
        rank_counts = Counter(ranks)
        #print(rank_counts)
        suit_counts = Counter(suits)

        is_flush = len(suit_counts) == 1  # All cards are of the same suit
        is_straight = False

        # Check if the hand is a straight
        sorted_ranks = sorted([self.RANKS.index(r) for r in ranks])
        if len(set(sorted_ranks)) == 5 and sorted_ranks[-1] - sorted_ranks[0] == 4:
            is_straight = True
        elif set(ranks) == {'A', '2', '3', '4', '5'}:  # Special case for Ace low straight (A-2-3-4-5)
            is_straight = True
            sorted_ranks = [0, 1, 2, 3, 12]  # Representing Ace as 0 in a low straight

        # Determine hand type
        if is_flush and is_straight:
            value = 0
            #print(f' Straight_Flush {value}')
            return "Straight_Flush" , value
        
        # Four of a Kind
        if 4 in rank_counts.values():
            key = [key for key in rank_counts if rank_counts[key] == 4]
            value = self.RANKS.index(key[0]) +2
            #print(f' Four_of_a_Kind {value}')
            return "Four_of_a_Kind" ,value
        
        # Full House
        if sorted(rank_counts.values()) == [2, 3]:
            key = [key for key in rank_counts if rank_counts[key] == 3]
            key2 = [key for key in rank_counts if rank_counts[key] == 2]
            value = self.RANKS.index(key[0]) + self.RANKS.index(key2[0]) +2
            #print(f' Full_House {value}')
            return "Full_House", value
        
        # Flush
        if is_flush:
            value = 2
            #print(f' Flush {value}')
            return "Flush", value
        
        # Straight
        if is_straight:
            value = 0
            for c in hand:
                if self.RANKS.index(c[:-1])+2 > value:
                    value = self.RANKS.index(c[:-1])+2
            if value == 14:
                v2 = 0
                for c in hand:
                    if self.RANKS.index(c[:-1])+2 > v2 and self.RANKS.index(c[:-1])+2 != 14:
                        value = self.RANKS.index(c[:-1])+2
                if v2 ==5:
                    value = 5
            #print(f' Straight {value}')
            return "Straight", value
        
        # Three of a Kind
        if 3 in rank_counts.values():
            key = [key for key in rank_counts if rank_counts[key] == 3]
            value = self.RANKS.index(key[0]) +2 
            #print(f' Three_of_a_Kind {value}')
            return "Three_of_a_Kind", value
        
        # Two Pair
        if sorted(rank_counts.values()) == [1, 2, 2]:
            key = [key for key in rank_counts if rank_counts[key] == 2]
            value = self.RANKS.index(key[0]) + self.RANKS.index(key[1]) +2 
            #print(f' Two_Pair {value}')
            return "Two_Pair" , value
        
        # One Pair
        if 2 in rank_counts.values():
            key = [key for key in rank_counts if rank_counts[key] == 2]
            value = self.RANKS.index(key[0])+2
            #print(f' One_Pair {value}')
            return "One_Pair", value
        
        # High Card
        for c in hand:
            if self.RANKS.index(c[:-1])+2 > value:
                value = self.RANKS.index(c[:-1])+2
        #print(f' High_Card {value}')

        return "High_Card", value


    def probability_oponent_has_better_hand(self,agent_hand_type,agent_value):
        '''Calculates the probability of opponenet having a better hand given the current cards in the deck, does not include high_card probability '''
        p = 0
        if agent_hand_type == "High_Card":
            p += self.p_one_pairs(0)
            p += self.p_two_pairs(0)
            p += self.p_three_pairs(0)
            p += self.p_straights(0)
            p += self.p_flush(0)
            p += self.p_full_house(0)
            p += self.p_four_of_kind(0)
            pass

        if agent_hand_type == "One_Pair":
            p += self.p_one_pairs(agent_value)
            #print(f'p {p}')
            p += self.p_two_pairs(0)
            #print(f'p {p}')
            p += self.p_three_pairs(0)
            #print(f'p {p}')
            p += self.p_straights(0)
            #print(f'p {p}')
            p += self.p_flush(0)
            #print(f'p {p}')
            p += self.p_full_house(0)
            #print(f'p {p}')
            p += self.p_four_of_kind(0)
            #print(f'p {p}')
            pass

        elif agent_hand_type == "Two_Pair":

            p += self.p_two_pairs(agent_value)
            p += self.p_three_pairs(0)
            p += self.p_straights(0)
            p += self.p_flush(0)
            p += self.p_full_house(0)
            p += self.p_four_of_kind(0)
            pass

        elif agent_hand_type == "Three_of_a_Kind":

            p += self.p_three_pairs(agent_value)
            #print(f'three of a kind {self.p_three_pairs(agent_value)} agent value {agent_value}')
            p += self.p_straights(0)
            #print(f'straight {self.p_straights(0)}') 
             
            p += self.p_flush(0)
            #print(f'flush {self.p_flush(0)}')
            p += self.p_full_house(0)
            #print(f'full house {self.p_full_house(0)}')
            p+= self.p_four_of_kind(0)
            #print (f'four_of_kind {self.p_four_of_kind(0)}')
            pass

        elif agent_hand_type == "Straight":
            p += self.p_straights(agent_value)
            p += self.p_flush(0)
            p += self.p_full_house(0)
            p += self.p_four_of_kind(0)
            pass

        elif agent_hand_type == "Flush":
            p += self.p_flush(agent_value)
            p += self.p_full_house(0)
            p += self.p_four_of_kind(0)
            pass

        elif agent_hand_type == "Full_House":
            p += self.p_full_house(agent_value)
            p += self.p_four_of_kind(0)
            pass
    
        elif agent_hand_type == "Four_of_a_Kind":  
            p += self.p_four_of_kind(agent_value)
            pass

        elif agent_hand_type == "Straight_Flush":
            pass
        #print(f'p {p/math.comb(self.card_in_deck,5)}')
        return p/math.comb(self.card_in_deck,5)
            
    
    def p_one_pairs(self,agent_value):
        '''Calculates the probability of opponent having a better hand of pair given the removed cards in the deck'''
        prob_pair = 0

        # calculates how many cards are left of each rank 
        lefts = {1:0,2:0,3:0,4:0}
        for c in self.rank_set:

            lefts[self.rank_set[c]]+=1

        # for each rank, checks if there is enough card to form a pair and if the current rank is higher than the players hand,
        # If so, add each combination of getting a pair of that rank and adds it to the probability.
        for c in self.rank_set:
            if self.rank_set[c] > 1 and self.RANKS.index(c)+2 >=agent_value:
                
                lefts[self.rank_set[c]]-=1 #Removes the current rank from the deck, done to not intclude it in the calculation of combination of the three uniqe cards combined with the pair 
                prob_pair += math.comb(self.rank_set[c],2)*math.comb(12,3)*(math.pow(math.comb(4,1)*lefts[4]/12 +math.comb(3,1)*lefts[3]/12 +math.comb(2,1)*lefts[2]/12+math.comb(1,1)*lefts[1]/12,3))
                lefts[self.rank_set[c]]+=1 # reinserts the current rank to the deck

        return prob_pair # probability
        #print(f'p_one_pairs {prob_pair/math.comb(self.card_in_deck,5)}')


    def p_two_pairs(self,agent_value):
        '''Calculates the probability of opponent having a better hand of two pairs given the removed cards in the deck'''

        prob_pair = 0

        # calculates how many cards are left of each rank
        lefts = {1:0,2:0,3:0,4:0} 
        for c in self.rank_set:
            lefts[self.rank_set[c]]+=1

        # iterates over each combination of two pairs, For each combination it checks if one of the ranks are higher than the players hand. 
        # If so, adds each combination of getting that two pair
        for i in range(len(self.RANKS)): # for each rank 
            c = self.RANKS[i] 
            for j in range(i+1,len(self.RANKS)): # for each rank that is not the same or previous 
                s = self.RANKS[j] 
                # checks that it possible to get a two pair and that it is higher than the players.
                if self.rank_set[c] > 1 and self.rank_set[s] > 1 and self.RANKS.index(c)+2 >=agent_value or self.RANKS.index(s)+2 >=agent_value:
                    lefts[self.rank_set[c]] -= 1#Removes the current rank from the deck, done to not intclude it in the calculation of combination of the uniqe cards combined with the two pair 
                    lefts[self.rank_set[s]] -= 1
                    prob_pair += math.comb(self.rank_set[c],2)*math.comb(self.rank_set[s],2) *math.comb(11,1)*(math.comb(4,1)*lefts[4]/11 +math.comb(3,1)*lefts[3]/11 +math.comb(2,1)*lefts[2]/11+math.comb(1,1)*lefts[1]/11)
                    lefts[self.rank_set[c]] += 1 # reinserts the current rank to the deck
                    lefts[self.rank_set[s]] += 1
        return prob_pair
        #print(f'p_two_pairs {prob_pair/math.comb(self.card_in_deck,5)}')


    def p_three_pairs(self,agent_value):
        '''Calculates the probability of opponent having a better hand of three of a kind given the removed cards in the deck'''
        
        prob_pair = 0
        # calculates how many cards are left of each rank
        lefts = {1:0,2:0,3:0,4:0}
        for c in self.rank_set:
            lefts[self.rank_set[c]]+=1

        # iterates over each combination of three of a kind, For each combination it checks if one of the ranks are higher than the players hand and that the rank is possible. 
        # If so, adds each combination of getting that two pair
        for c in self.rank_set:
            if self.rank_set[c] > 2 and self.RANKS.index(c)+2 >=agent_value:
                lefts[self.rank_set[c]]-=1 #Removes the current rank from the deck, done to not intclude it in the calculation of combination of the uniqe cards combined with the two pair 
                prob_pair += math.comb(self.rank_set[c],3)*math.comb(12,2)*(math.pow(math.comb(4,1)*lefts[4]/12 +math.comb(3,1)*lefts[3]/12 +math.comb(2,1)*lefts[2]/12+math.comb(1,1)*lefts[1]/12,2))
                lefts[self.rank_set[c]]+=1 # reinserts the current rank to the deck
        #print(f'p_one_pairs {prob_pair/math.comb(self.card_in_deck,5)}')
        return prob_pair

    def p_straights(self,agent_value):
        '''Calculates the probability of opponent having a better hand of straights given the removed cards in the deck
        
        Issues: Currently only calculates the probability of opponent having a straight given the removed cards.
        '''
        prob = 0
        # iterates over each combination of straight, For each combination it checks that the rank is possible. 
        # If so, adds each combination of getting that two pair
        for i in range(len(self.RANKS)-4):
            
            c0 = self.RANKS[i]
            c1 = self.RANKS[i+1]
            c2 = self.RANKS[i+2]
            c3 = self.RANKS[i+3]
            c4 = self.RANKS[i+4]
            if self.rank_set[c0] > 0 and self.rank_set[c1] > 0 and self.rank_set[c2] > 0 and self.rank_set[c3] > 0 and self.rank_set[c4] > 0  and self.RANKS.index(c4)+2 >=agent_value:
                prob += math.comb(self.rank_set[c0],1)*math.comb(self.rank_set[c1],1)*math.comb(self.rank_set[c2],1)*math.comb(self.rank_set[c3],1)*math.comb(self.rank_set[c4],1)
        if self.rank_set['A'] > 0 and self.rank_set['2'] > 0 and self.rank_set['3'] > 0 and self.rank_set['4'] > 0 and self.rank_set['5'] > 0:        
            prob += math.comb(self.rank_set['A'],1)*math.comb(self.rank_set['2'],1)*math.comb(self.rank_set['3'],1)*math.comb(self.rank_set['4'],1)*math.comb(self.rank_set['5'],1)
        
        #print(f'p_straights {prob/math.comb(self.card_in_deck,5)}')
        return prob
    

    def p_flush(self,agent_value):
        '''Calculates the probability of opponent having a better hand of flush given the removed cards in the deck'''

        # check which suits has been removed
        #suits = {'s':13,'h':13,'c':13,'d':13}
        #for c in hand:
        #    suits[c[-1]] -=1

        prob = 0
        # for each suits calculates the probability of having given the removed cards
        for s in self.suit_set:
            prob += math.comb(self.suit_set[s],5)    
        #print(f'p_flush {prob/math.comb(self.card_in_deck,5)}')
        return prob



    def p_full_house(self,agent_value):
        '''Calculates the probability of opponent having a better hand of full house given the removed cards in the deck'''

        prob_pair = 0
        lefts = {1:0,2:0,3:0,4:0}
        for c in self.rank_set:
            lefts[self.rank_set[c]]+=1
        for i in range(len(self.RANKS)): # for each rank 
            c = self.RANKS[i] 
            # loogs the amount of cards of that rank
            for j in range(i+1,len(self.RANKS)): # for each rank that is not the same or previous 
                s = self.RANKS[j] 
                if self.rank_set[c] > 2 and self.rank_set[s] > 1:
                    lefts[self.rank_set[c]] -= 1
                    lefts[self.rank_set[s]] -= 1
                    prob_pair += math.comb(self.rank_set[c],3)*math.comb(self.rank_set[s],2)
                    lefts[self.rank_set[c]] += 1
                    lefts[self.rank_set[s]] += 1
                if self.rank_set[c] > 1 and self.rank_set[s] > 2:
                    lefts[self.rank_set[c]] -= 1
                    lefts[self.rank_set[s]] -= 1
                    prob_pair += math.comb(self.rank_set[c],2)*math.comb(self.rank_set[s],3) 
                    lefts[self.rank_set[c]] += 1
                    lefts[self.rank_set[s]] += 1
        #print(f'p_two_pairs {prob_pair/math.comb(self.card_in_deck,5)}')
        return prob_pair
        
    def p_four_of_kind(self,agent_value):

        prob_pair = 0
        lefts = {1:0,2:0,3:0,4:0}
        for c in self.rank_set:
            lefts[self.rank_set[c]]+=1

        for c in self.rank_set:
            if self.rank_set[c] > 3 and self.RANKS.index(c)+2 >=agent_value:
                lefts[self.rank_set[c]]-=1
                prob_pair += math.comb(self.rank_set[c],4)*math.comb(12,1)*(math.comb(4,1)*lefts[4]/12 +math.comb(3,1)*lefts[3]/12 +math.comb(2,1)*lefts[2]/12+math.comb(1,1)*lefts[1]/12)
                lefts[self.rank_set[c]]+=1
        #print(f'p_four_of_kind {prob_pair/math.comb(self.card_in_deck,5)}')
        return prob_pair

        


#exempel
#hand = ['2s', 'Ad', '3c', '4h', '5s']  # start hand
#d = ['4s', '5d','6s','2h'] # kort som swappas
#p = prob_calculator()
#p.update(hand) # updates the deck acording to the card in our hand
#p.update(d) # updates the deck acording to the cards that has been drawn when swaping
#hand_t, hand_val = p.evaluate_hand(hand) # evaluates the hand
#p.probability_oponent_has_better_hand(hand_t,hand_val) # prints the probability
