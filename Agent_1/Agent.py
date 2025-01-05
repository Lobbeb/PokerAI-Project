from Agent_1 import ChangeHand as ch
from Agent_1.opponent_better_hand_calculator import prob_calculator
import math
from collections import Counter

'''This class is used to track an opponents moves and through it estimate if the opponent has a good hand or bad hand and also view if the opponent has a deviating 
    winrate, and if so if it is probable that the opponent is bluffing.'''
class opponent:
    def __init__(self,name,chips):
        self.RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        self.HAND_RANK = ["NAN","High_Card","One_Pair","Two_Pair","Three_of_a_Kind","Straight","Flush","Full_House","Four_of_a_Kind","Straight_Flush"]
        self.name = name #--
        self.chips = chips #--
        self.in_game = True
        self.rounds = 1     #---
        self.agent_wins = 0     #--
        self.total_raise = 0

        # variables during each round-------- 
        self.in_round = True
        self.open_bfd = 0
        self.open_afd = 0
        self.hand_round = []
        self.cards_thrown_away = 0
        self.possible_hand = "NAN"
        self.round_total_raise = 0
        self.round_times_rasied = 0
        #Logs, used at the end of the game to view each opponents moves and compare it with predictions

        self.hands_log = {}     #--
        self.cards_thrown_away_log = {} #--
        self.possible_hand_guess_log = {} #--
        self.log_wins = {}  #--
        self.log_wins_undisputed = {} #--
        self.log_wins_before_draw = {}
        self.total_raise_logs = {} #--
        self.times_raise_logs = {} #--
        self.total_raise_logs_before_draw = {} #--
        self.times_raise_logs_before_draw = {} #--
        self.log_folds = {}
        self.log_fold_bd = {}
        self.log_open_bfd = {}
        self.log_open_afd = {}

        #self.possible_hand_before_draw = "NAN"

    def update_chips(self,chips):
        self.chips = chips
    
    def opponent_open_before_draw(self,amount):
        self.open_bfd = amount
    
    def opponent_open_after_draw(self,amount):
        self.open_afd = amount
    
    def opponent_fold(self):
        self.in_round = False
        self.log_folds[self.rounds] = 1
    
    
    
    def not_yet_folded(self):
        return self.in_round
    
    def increment_win(self,win):
        if win==1:
            self.agent_wins +=1
        self.log_wins[self.rounds] = win
    
    def win_undisputed(self,win_undisp):
        self.log_wins_undisputed[self.rounds] = win_undisp
    
    def win_before_draw(self,t_f):
        self.log_wins_before_draw[self.rounds] = t_f


    def log_hand(self,hand):
        self.hand_round = hand

    def opponent_raised(self,amount):
        '''Tracks how much the opponent has raised this round and how many times, also tracks the total amount over the game'''
        self.round_total_raise += amount
        self.total_raise += amount
        self.round_times_rasied += 1

    def log_raise_before_draw(self):
        '''Logs how much the opponent has raised before the drawstep at the current round'''
        self.total_raise_logs_before_draw[self.rounds] = self.round_total_raise
        self.times_raise_logs_before_draw[self.rounds] = self.round_times_rasied
    
    def cards_thrown(self,x):
        '''track how many cards thatwere thrown'''
        self.cards_thrown_away = int(x)
        self.calc_possible_hand_by_card_thrown()
        self.log_raise_before_draw()
        if self.in_round:
            self.log_fold_bd[self.rounds] = 0
        
    
    
    def calc_possible_hand_by_card_thrown(self):
        '''Calculates what possible hands the opponent could have given how many cards it threw away'''
        if self.cards_thrown_away == 3:
            self.possible_hand = "One_Pair"
        elif self.cards_thrown_away == 2:
            self.possible_hand ="Three_of_a_Kind"
        elif self.cards_thrown_away == 1:
            self.possible_hand = "Two_Pair"
        else:
            self.possible_hand = "High_Card"

    
    def new_round(self):
        '''Logs,resets and updates variables to fit the new round'''
        
        #LOGS
        self.log_open_bfd[self.rounds] = self.open_bfd
        self.log_open_afd[self.rounds] = self.open_afd
        self.times_raise_logs[self.rounds] = self.round_times_rasied
        self.total_raise_logs[self.rounds] = self.round_total_raise
        self.hands_log[self.rounds] = self.hand_round[:]
        self.possible_hand_guess_log[self.rounds] = self.possible_hand
        self.cards_thrown_away_log[self.rounds] = self.cards_thrown_away

        if self.rounds not in self.total_raise_logs_before_draw:
            self.total_raise_logs_before_draw[self.rounds] = 0
        if self.rounds not in self.times_raise_logs_before_draw:
            self.times_raise_logs_before_draw[self.rounds] = 0

        
        if self.in_round:
            self.log_folds[self.rounds] = 0
        if self.rounds not in self.log_fold_bd:
            self.log_fold_bd[self.rounds] = 1

            
        #UPDATES
        self.rounds +=1
        self.in_round = True

        #RESETS
        self.round_times_rasied = 0
        self.round_total_raise = 0  
        self.possible_hand = "NAN"
        self.cards_thrown_away = 0
        self.hand_round = []
        self.open_afd= 0
        self.open_bfd= 0
        

    def print_result(self):
        '''prints the opponents results of each round and the predicted result'''
        print(f'                                OPPONENT: {self.name}')
        print('         |chips:'  )
        print(f'            |{self.chips}')
        print('         |')
        print(f'        |wins :')
        print(f'            |{self.agent_wins}')
        print('         |')
        print('         |wins log:')
        print(f'            |{self.log_wins}')
        print('         |')
        print('         |wins undiputed log:')
        print(f'            |{self.log_wins_undisputed}')
        print(f'        |')
        print('         |FOLDS')
        print(f'         |{self.log_folds}')
        print('         |OPENINGS')
        print('             |BFD:')
        print(f'             |{self.log_open_bfd}')
        print('             |AFD:')
        print(f'             |{self.log_open_afd}')
        print('         |RAISE')
        print('             |BFD:')
        print(f'             |{self.total_raise_logs_before_draw}')
        print('             |AFD:')
        print(f'             |{self.total_raise_logs}')
        print('         |FOLDS')
        print('             |BFD:')
        print(f'             |{self.log_fold_bd}')
        print('             |AFD:')
        print(f'             |{self.log_folds}')
        print('         |DATA EACH ROUND:')
        for i in range(1,self.rounds):
            print(f'        _____________________________________|ROUND: {i}_____________________________________________')
            print(f'         |WIN:{self.log_wins[i]}')
            print(f'        |WIN UNDISPUTED:{self.log_wins_undisputed[i]} |WIN BEFORE DRAW:{self.log_wins_before_draw[i]}')
            print(f'        |FOLD :{self.log_folds[i]}')
            print('         |OPENINGS')
            print(f'            |BFD :{self.log_open_bfd[i]} |AFD:{self.log_open_afd[i]}')
            print(f'        |RAISES')
            print('             |RAISE BD:')
            print(f'                |RAISE:{self.total_raise_logs_before_draw[i]} |TIMES R:{self.times_raise_logs_before_draw[i]}')
            print('             |RAISE AD:')
            print(f'                |RAISE:{self.total_raise_logs[i]} |TIMES R:{self.times_raise_logs[i]}')
            print(f'            |HAND: {self.hands_log[i]} GUESS: {self.possible_hand_guess_log[i]} CARDS THROWN: {self.cards_thrown_away_log[i]}')



    def check_agressiveness(self):
        average_raises_per_round = sum(self.times_raise_logs.values()) / len(self.times_raise_logs)
        

        average_opening_per_round = sum(self.log_open_afd.values())/len(self.log_open_afd)
        total_folds = sum(self.log_folds.values())


        # ____________________________________________PRE DRAW PHASE________________________________________________________
        # Check how agressive the player is before the draws step, check the rounds that 
        # got to the drawstep and see if they threw cards that matches a good hand, if hand was shown compare those rounds too.
        # determine if they have a high chance of bluffing early or if they only raise when they start with a good hand.
        pre_draw_agressiveness = 0

        average_raises_per_round_BD = sum(self.times_raise_logs_before_draw.values()) / len(self.times_raise_logs_before_draw)
        average_opening_per_round_BD = sum(self.log_open_bfd.values())/len(self.log_open_bfd)

        #_____________________________________________POST DRAW PHASE________________________________________________________
        #Check how aggressive the player is after the draw phase, check how the player changed its cards and how it raised/opened accordingly, 
        # also check if the they raised before the draw and if they changed cards acording to a good hand.
        #if cards where shown then check how good they were with how much they raised. 
        # determine if they have high chance of bluffing, if they fold under pressure. 
        post_draw_aggressiveness = 0 




        
























class Poker_Agent:
    def __init__(self,name):
        self.RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        self.HAND_RANK = ["NAN","High_Card","One_Pair","Two_Pair","Three_of_a_Kind","Straight","Flush","Full_House","Four_of_a_Kind","Straight_Flush"]
        self.agent_name = name
        self.p = prob_calculator()
        self.hand =[]
        self.opponents = {}
        self.p = prob_calculator()
        self.rounds = 0
        self.has_drawn = False
    
    def set_hand(self,hand):
        self.hand = hand
    def get_hand(self):
        return self.hand
        
    def decide_init_bet(self):
        self.p.update(self.hand)
        hand_t, hand_val =self.p.evaluate_hand(self.hand)
        prob = self.p.probability_oponent_has_better_hand(hand_t, hand_val)
        if prob < 0.05:
            return 'bet_rank_1', prob
        if prob < 0.1:
            return 'bet_rank_2',prob
        if prob < 0.3:
            return 'bet_rank_3',prob
        if prob < 0.45:
            return 'bet_rank_4', prob
        return 'check', prob


    def decide_raise_call(self):
        self.p.update(self.hand)
        hand_t, hand_val =self.p.evaluate_hand(self.hand)
        prob = self.p.probability_oponent_has_better_hand(hand_t, hand_val)
        #opponents_hand_strenth = []
        #for key in self.opponents:
        #    print(f'Opponent {self.opponents[key].name}')
        #    if self.opponents[key].not_yet_folded():
        #        opponents_hand_strenth.append(self.opponents[key].get_opponent_hand_strength(self.has_drawn))
        #hand = self.evaluate_hand(self.hand)
        #print(f' hand strenth: === {hand} ====')
        #for h in opponents_hand_strenth:
        #    print(f' OPPONENT hand strenth: === {h} ====')
        #    if self.HAND_RANK.index(h) > self.HAND_RANK.index(hand):
        #        return 'fold', prob
            
        if prob < 0.05:
            return 'bet_rank_1', prob
        if prob < 0.1:
            return 'bet_rank_2',prob
        if prob < 0.3:
            return 'bet_rank_3',prob
        if prob < 0.45:
            return 'bet_rank_4', prob
        return 'check', prob
    

    def cards_to_throw(self):
        self.has_drawn = True
        cards_to_throw = ch.queryCardsToThrow(self.hand)
        ct = cards_to_throw.split()
        s= ''
        for c in ct:
            s += str(c) +' '
        return s
    
    def new_round(self):
        self.p.reset()
        self.p.reset_removed_cards()
        self.has_drawn = False

    def increment_rounds(self):
        self.rounds += 1

    # _______________________________________________________ handle opponent__________________________________________________
    '''These functions calls on the opponent class and is used to track the opponents moves and results that are available'''

    def add_opponent(self, name, chips):
        '''Checks if opponent is being tracked, if not adds it to the diconary by its name'''
        if name not in self.opponents:
            if name != self.agent_name:
                self.opponents[name] = opponent(name, chips)
                print(f"Opponent '{name}' added.")
        
    def update_opponent_chips(self,name,chips):
        '''updates the opponents number of chips '''
        if name != self.agent_name:
            if name in self.opponents:
                self.opponents[name].update_chips(chips)
    
    def opponent_open(self,name, openBet):
        if name != self.agent_name:
            if name in self.opponents:
                if not self.has_drawn:
                    self.opponents[name].opponent_open_before_draw(int(openBet))
                else:
                    self.opponents[name].opponent_open_after_draw(int(openBet))

        
    def opponent_fold(self,name):
        '''Tracks if an opponent has folded'''
        if name != self.agent_name:
            if name in self.opponents:
                self.opponents[name].opponent_fold()
        

    def opponent_raised(self,name,amount):
        '''tracks each opponent that has raised and how much they have raised'''
        if name != self.agent_name:
            if name in self.opponents:
                self.opponents[name].opponent_raised(amount)

    def oponent_cards_thrown(self,name,x):
        self.has_drawn = True
        '''Tracks how many cards an opponent has thrown away'''
        if name != self.agent_name:
            if name in self.opponents:
                self.opponents[name].cards_thrown(x)

                    
    def opponent_hand(self,name,hand):
        '''Logs the opponents hand'''
        if name != self.agent_name:
            if name in self.opponents:
                self.opponents[name].log_hand(hand)

    def opponent_win(self,name,undisp):
        '''Tracks how many wins a opponent has''' 
        for key in self.opponents:
            if name == key:
                self.opponents[name].increment_win(1)
            else:
                self.opponents[key].increment_win(0)
        self.opponent_win_undisputed(name,undisp)
        
    
    def opponent_win_undisputed(self,name,undisp):
        '''Tracks how many undisputed wins a opponent has'''
        if not self.has_drawn:
            for key in self.opponents:
                if name == key:
                    self.opponents[name].win_before_draw(1)
                else:
                    self.opponents[key].win_before_draw(0)
        else:
            for key in self.opponents:    
                self.opponents[key].win_before_draw(0)        
        if undisp:
            for key in self.opponents:
                if name == key:
                    self.opponents[name].win_undisputed(1)
                else:
                    self.opponents[key].win_undisputed(0)
        else:
            for key in self.opponents:    
                self.opponents[key].win_undisputed(0)
            

    def opponent_new_round(self):
        '''Updeates each oppnents variables for the new round'''
        for key in self.opponents:
            self.opponents[key].new_round()
    
    def print_oppnent_results(self):
        '''prints the end game results of each opponent'''
        for key in self.opponents:
            self.opponents[key].print_result()
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Handle Opponent^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    






'''
def get_opponent_hand_strength(self,has_drawn):

        #implement so that it also takes ino acount the chance that the opponent is bluffing.
        if has_drawn:
            if self.rounds >= 3:
                self.possible_hand = self.raises_after_draw()
                return self.possible_hand
        else: 
            if self.rounds >= 3:
                self.possible_hand_before_draw = self.raises_before_draw()
                if self.possible_hand_before_draw == "NAN": # no data to determine
                    pass
                    #check winrate, to determine if high chance of bluffing       
            return self.possible_hand_before_draw 
        return "NAN"


    def raises_before_draw(self):
        avg_rbd = []
        for i in range(1,self.rounds-1):
            rbd = self.raise_logs_before_draw[i]
            trbd = self.times_raise_logs_before_draw[i]
            if trbd != 0:
                avg_rbd.append(rbd/trbd)
            else:
                avg_rbd.append(0)

        print(f'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx {self.rounds} xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        ms_r = -1 # most similiar raise (acording to the avg_rbd)
        ms_r_i = -1
        for v in range(len(avg_rbd)): # finds the most similar rasie from previous values
            if self.times_raise_logs_before_draw[self.rounds-1] != 0:
                if abs(avg_rbd[v]-self.raise_logs_before_draw[self.rounds-1]/self.times_raise_logs_before_draw[self.rounds-1]) < ms_r- self.raise_logs_before_draw[self.rounds-1]/self.times_raise_logs_before_draw[self.rounds-1] or ms_r == -1:
                    ms_r = avg_rbd[v] 
                    ms_r_i = v+1
        
        if ms_r_i != -1:       
            card_thrown_at_ms = self.cards_thrown_away_log[ms_r_i]
            if card_thrown_at_ms == self.cards_thrown_away: # cards thrown away this round matches the amount of cards thrown away at the most similar raise round
                hand_at_ms = self.hands_log[ms_r_i]
                if hand_at_ms:
                    self.possible_hand = self.evaluate_hand(hand_at_ms) # assume similar hand and se how good it was
                    
                    # Set the possible hand,determined by fixed assumtions. 
                    if self.possible_hand == "High_Card": 
                            return "High_Card"#assumes it is the same case
                    if self.possible_hand == "One_Pair": 
                        if card_thrown_at_ms <= 3: # if they most likley had pair before
                            return "One_Pair"#assumes it is the same case
                        self.possible_hand == "High_Card"
                        return "High_Card"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Two_Pair":
                        if card_thrown_at_ms == 1:
                            return "Two_Pair"#assumes it is the same case
                        self.possible_hand == "One_Pair"
                        return "One_Pair"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Three_of_a_Kind":
                        if card_thrown_at_ms <= 2:
                            return "Three_of_a_Kind" #assumes it is the same case
                        self.possible_hand == "One_Pair"
                        return "One_Pair"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Straight":
                        if card_thrown_at_ms == 0:
                            return "Straight"
                        self.possible_hand == "High_Card"
                        return "High_Card"#----------------------------------------------------------------------------
                    elif self.possible_hand == "Flush":
                        if card_thrown_at_ms == 0:
                            return "Flush"
                        self.possible_hand == "High_Card"
                        return "High_Card"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Full_House":
                        if card_thrown_at_ms == 0:
                            return "Full_House"
                        self.possible_hand == "Two_Pair"
                        return "Two_Pair"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Four_of_a_Kind":
                        if card_thrown_at_ms <= 1:
                            return "Four_of_a_Kind"
                        self.possible_hand == "Three_of_a_Kind"
                        return "Three_of_a_Kind"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Straight_Flush":
                        if card_thrown_at_ms == 0:
                            return "Straight_Flush"
                        self.possible_hand == "High_Card"
                        return "High_Card"
                        #----------------------------------------------------------------------------
                else: 
                    #self.clac_possible_hand_by_card_thrown() 
                    #guess = self.possible_hand
                    return "NAN"
                    
            elif self.log_wins[ms_r_i]: #check if the opponent won that match undisputed
                #---------------------------------------------------------IMPROVMENT ------------------------------------------------------
                #self.clac_possible_hand_by_card_thrown()  # Here it can be imporved opon by checking how often this ocours, could be a sign of bluffing.
                #guess = self.possible_hand
                return "NAN"
        #self.clac_possible_hand_by_card_thrown()
        #guess = self.possible_hand
        return "NAN"

    def raises_after_draw(self):
        avg_rbd = []
        for i in range(1,self.rounds-1):
            rbd = self.raise_logs[i]
            trbd = self.times_raise_logs[i]
            if trbd != 0:
                avg_rbd.append(rbd/trbd)
            else:
                avg_rbd.append(0)
        
        ms_r = -1 # most similiar raise (acording to the avg_rbd)
        ms_r_i = -1 # most similar raise index
        for v in range(len(avg_rbd)): # finds the most similar rasie from previous values
            if self.times_raise_logs[self.rounds-1] != 0:
                if abs(avg_rbd[v]-self.raise_logs[self.rounds-1]/self.times_raise_logs[self.rounds-1]) < ms_r- self.raise_logs[self.rounds-1]/self.times_raise_logs[self.rounds-1] or ms_r == -1:
                    ms_r = avg_rbd[v] 
                    ms_r_i = v+1
        if ms_r_i != -1:
            card_thrown_at_ms = self.cards_thrown_away_log[ms_r_i]
            if card_thrown_at_ms == self.cards_thrown_away: # cards thrown away this round matches the amount of cards thrown away at the most similar raise round
                hand_at_ms = self.hands_log[ms_r_i]
                if hand_at_ms:
                    self.possible_hand = self.evaluate_hand(hand_at_ms) # assume similar hand and se how good it was
                    
                    # Set the possible hand,determined by fixed assumtions. 
                    if self.possible_hand == "High_Card": 
                            return "High_Card"#assumes it is the same case
                    if self.possible_hand == "One_Pair": 
                        if card_thrown_at_ms <= 3: # if they most likley had pair before
                            return "One_Pair"#assumes it is the same case
                        self.possible_hand == "High_Card"
                        return "High_Card"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Two_Pair":
                        if card_thrown_at_ms == 1:
                            return "Two_Pair"#assumes it is the same case
                        self.possible_hand == "One_Pair"
                        return "One_Pair"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Three_of_a_Kind":
                        if card_thrown_at_ms <= 2:
                            return "Three_of_a_Kind" #assumes it is the same case
                        self.possible_hand == "One_Pair"
                        return "One_Pair"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Straight":
                        if card_thrown_at_ms == 0:
                            return "Straight"
                        self.possible_hand == "High_Card"
                        return "High_Card"#----------------------------------------------------------------------------
                    elif self.possible_hand == "Flush":
                        if card_thrown_at_ms == 0:
                            return "Flush"
                        self.possible_hand == "High_Card"
                        return "High_Card"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Full_House":
                        if card_thrown_at_ms == 0:
                            return "Full_House"
                        self.possible_hand == "Two_Pair"
                        return "Two_Pair"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Four_of_a_Kind":
                        if card_thrown_at_ms <= 1:
                            return "Four_of_a_Kind"
                        self.possible_hand == "Three_of_a_Kind"
                        return "Three_of_a_Kind"
                        #----------------------------------------------------------------------------
                    elif self.possible_hand == "Straight_Flush":
                        if card_thrown_at_ms == 0:
                            return "Straight_Flush"
                        self.possible_hand == "High_Card"
                        return "High_Card"
                        #----------------------------------------------------------------------------
                else: 
                    self.clac_possible_hand_by_card_thrown()
                    guess = self.possible_hand
                    return guess
                    
            elif self.log_wins[ms_r_i]: #check if the opponent won that match undisputed
                #---------------------------------------------------------IMPROVMENT ------------------------------------------------------
                self.clac_possible_hand_by_card_thrown()  # Here it can be imporved opon by checking how often this ocours, could be a sign of bluffing.
                guess = self.possible_hand
                return guess
            
        self.clac_possible_hand_by_card_thrown()
        guess = self.possible_hand
        return guess



    def evaluate_hand(self,hand): 
        calculates what type of hand and gives it a value, returns the type of hand ("Straight Flush", "Four of a Kind", ... "Pair") 
        
        # Parse the hand into rank and suit
        ranks = [card[:-1] for card in hand]
        suits = [card[-1] for card in hand]
        rank_counts = Counter(ranks)
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
            return "Straight_Flush"
        # Four of a Kind
        if 4 in rank_counts.values():
            return "Four_of_a_Kind"
        # Full House
        if sorted(rank_counts.values()) == [2, 3]:
            return "Full_House"
        # Flush
        if is_flush:
            return "Flush"
        # Straight
        if is_straight:
            return "Straight"
        # Three of a Kind
        if 3 in rank_counts.values():
            return "Three_of_a_Kind"
        # Two Pair
        if sorted(rank_counts.values()) == [1, 2, 2]:
            return "Two_Pair" 
        # One Pair
        if 2 in rank_counts.values():
            return "One_Pair"
        return "High_Card"

'''