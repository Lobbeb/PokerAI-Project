import ChangeHand as ch
from opponent_better_hand_calculator import prob_calculator
import math
from collections import Counter

'''This class is used to track an opponents moves and through it estimate if the opponent has a good hand or bad hand and also view if the opponent has a deviating 
    winrate, and if so if it is probable that the opponent is bluffing.'''
class opponent:
    def __init__(self,name,chips):
        self.RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        self.HAND_RANK = ["NAN","High_Card","One_Pair","Two_Pair","Three_of_a_Kind","Straight","Flush","Full_House","Four_of_a_Kind","Straight_Flush"]
        self.name = name #--

        self.pre_draw = 0#-----------------------------------fix vet inte vad för värden och data typ ännnnnnnnn
        self.post_draw = 0 #--------------------------------fix
        self.bluff = 0 # -----------------------------------fix


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
        self.hand_type_log = {}
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
        self.log_chip = {}
        self.log_pre_draw = {}
        self.log_post_draw = {}

        #self.possible_hand_before_draw = "NAN"

    def update_chips(self,chips):
        self.chips = int(chips)
    
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
        """
        Calculates a probability distribution over possible hands the opponent
        could have, combining two factors:
        1) Baseline (based on how many cards they discarded).
        2) Adjustments (based on how aggressively they played this round).
        Stores both:
        - self.possible_hand_dist: the final distribution (dict).
        - self.possible_hand: the single most likely category in that distribution.
        """

        # --------------------- 1) BASELINE DISTRIBUTION ---------------------
        # We define a baseline distribution using #cards_thrown.
        if self.cards_thrown_away == 0:
            # Usually a "pat" hand or big bluff
            base_dist = {
                "High_Card":       0.05,
                "One_Pair":        0.10,
                "Two_Pair":        0.25,
                "Three_of_a_Kind": 0.15,
                "Straight":        0.15,
                "Flush":           0.15,
                "Full_House":      0.10,
                "Four_of_a_Kind":  0.04,
                "Straight_Flush":  0.01
            }
        elif self.cards_thrown_away == 1:
            # Possibly two pair → full house; or 4-to-flush/straight
            base_dist = {
                "Two_Pair":        0.35,
                "Three_of_a_Kind": 0.20,
                "One_Pair":        0.15,
                "Straight":        0.15,
                "Flush":           0.10,
                "Full_House":      0.05,
                "Four_of_a_Kind":  0.00  # extremely rare, but let's keep for completeness
            }
        elif self.cards_thrown_away == 2:
            # Often 3-of-a-kind trying for full house, or 1 pair
            base_dist = {
                "Three_of_a_Kind": 0.40,
                "Two_Pair":        0.20,
                "One_Pair":        0.15,
                "Straight":        0.10,
                "Flush":           0.10,
                "Full_House":      0.05
            }
        elif self.cards_thrown_away == 3:
            # Commonly a single pair kept, or a potential “keep one high card” type
            base_dist = {
                "One_Pair":        0.60,
                "High_Card":       0.20,
                "Three_of_a_Kind": 0.10,
                "Two_Pair":        0.10
            }
        else:  # 4 or 5
            # Usually a desperate draw, or absolutely nothing
            base_dist = {
                "High_Card":       0.80,
                "One_Pair":        0.10,
                "Two_Pair":        0.10
            }

        # Normalize the baseline distribution
        base_total = sum(base_dist.values())
        if base_total > 0:
            for hand_type in base_dist:
                base_dist[hand_type] = base_dist[hand_type] / base_total
        else:
            # If something goes wrong, fallback
            base_dist = {"High_Card": 1.0}

        # --------------------- 2) ADJUSTMENTS BY BETTING LOGS ---------------------
        # Here, we look at how they've played *this round*. 
        # For example: 
        #   self.round_total_raise (total chips they've raised this round)
        #   self.round_times_rasied (how many times they raised)
        #   self.open_bfd / self.open_afd (open bets before/after draw)
        # Or the global stats in logs, if you want to factor *historical* aggression.

        # Let's define some heuristics:
        #   - If they've raised a lot (round_total_raise is large relative to a typical “big bet”),
        #     shift distribution slightly more toward stronger hands.
        #   - If they haven't raised at all (and haven't folded), maybe they're more on a middle-range hand.
        #   - If they folded frequently in the past but are STILL in, they might have a stronger hand than usual.

        # Example "aggression factor" for the current round:
        #   The bigger round_total_raise, the bigger this factor > 1.0
        #   You can fine-tune the scale or threshold:
        if self.round_total_raise > 50:  # example threshold for "big raise"
            aggression_factor = 1.3
        elif self.round_total_raise > 20:
            aggression_factor = 1.1
        else:
            aggression_factor = 1.0

        # We'll also define a "caution factor" if they often fold or are very passive in earlier rounds.
        # E.g., if they've folded a lot in the past, but this round they're not folding, 
        # maybe they do indeed have something decent:
        fold_count = sum(self.log_folds.values())
        # Suppose if they fold a lot historically, but now they're raising or staying in,
        # we interpret that as them having stronger hands.
        if fold_count > (self.rounds * 0.5):  # folded > 50% of total rounds
            caution_factor = 1.15
        else:
            caution_factor = 1.0

        # Combine these factors to get an overall "strength shift"
        # (AG * CF) might be a bit too simplistic, but let's keep it easy:
        overall_strength_shift = aggression_factor * caution_factor

        # We apply the shift to the categories we consider "strong" hands more strongly
        # (e.g., Full_House, Four_of_a_Kind, Straight_Flush, etc.)
        # You can refine which categories get boosted or penalized:
        strength_categories = {"Three_of_a_Kind", "Straight", "Flush", "Full_House", "Four_of_a_Kind", "Straight_Flush", "Two_Pair"}
        # We'll also define "weaker" categories to get a slight penalty if there's big aggression
        #  - Or at least not get boosted as much
        # For example, One_Pair or High_Card might remain or get slightly decreased if aggression is high

        # Let's create a new distribution dict so we don't mutate base_dist in place:
        adjusted_dist = {}

        for hand_type, base_prob in base_dist.items():
            if hand_type in strength_categories:
                # If they're raising a lot, increase probability for strong hands
                adjusted_dist[hand_type] = base_prob * overall_strength_shift
            else:
                # If they're raising a lot, maybe it's less likely they're on a weak holding
                # but sometimes it might be a bluff. Let's allow partial effect, e.g. sqrt(shift).
                # If there's minimal aggression, the distribution remains mostly the same.
                if overall_strength_shift > 1.0:
                    # slight decrease for weaker categories
                    adjusted_dist[hand_type] = base_prob * (1.0 + (overall_strength_shift - 1.0) * 0.2)
                else:
                    # normal or no aggression => distribution remains
                    adjusted_dist[hand_type] = base_prob

        # Now re-normalize again:
        total_adj = sum(adjusted_dist.values())
        if total_adj > 0:
            for hand_type in adjusted_dist:
                adjusted_dist[hand_type] = adjusted_dist[hand_type] / total_adj
        else:
            # if everything got messed up, revert to baseline
            adjusted_dist = base_dist

        # 3) Store the final distribution and pick the single most-likely hand
        self.possible_hand_dist = adjusted_dist
        self.possible_hand = max(adjusted_dist, key=adjusted_dist.get)
    
    
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
        self.log_chip[self.rounds] = self.chips

        if self.rounds not in self.total_raise_logs_before_draw:
            self.total_raise_logs_before_draw[self.rounds] = 0
        if self.rounds not in self.times_raise_logs_before_draw:
            self.times_raise_logs_before_draw[self.rounds] = 0

        
        if self.in_round:
            self.log_folds[self.rounds] = 0
        if self.rounds not in self.log_fold_bd:
            self.log_fold_bd[self.rounds] = 1
        
        if not self.hand_round:
            self.hand_type_log[self.rounds] =  "NAN"
        else:
            self.hand_type_log[self.rounds] = self.evaluate_hand(self.hand_round)

        self.deduce_opponent()
        self.log_pre_draw[self.rounds] =self.pre_draw
        self.log_post_draw[self.rounds] = self.post_draw 

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

    def evaluate_hand(self,hand): 
        '''calculates what type of hand and gives it a value, returns the type of hand ("Straight Flush", "Four of a Kind", ... "Pair")'''
        
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

    def print_result(self):
        '''prints the opponents results of each round and the predicted result'''
        print(f'                                OPPONENT: {self.name}')
        print(f'        |CHIPS: {self.log_chip}')
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
        #print('         |playstyle:')
        #print(f'            |{self.log_play_style}')
        print('         |pre draw p-a:')
        print(f'            |{self.log_pre_draw}')
        print('         |post draw p-a:')
        print(f'            |{self.log_post_draw}')


        print('         |DATA EACH ROUND:')
        for i in range(1,self.rounds):
            print(f'        _____________________________________|ROUND: {i}_____________________________________________')
            print(f'        |CHIPS: {self.log_chip[i]}')
            print(f'         |WIN:{self.log_wins[i]}')
            print(f'        |WIN UNDISPUTED:{self.log_wins_undisputed[i]} |WIN BEFORE DRAW:{self.log_wins_before_draw[i]}')
            print(f'        |FOLD :{self.log_folds[i]}')
            print(f'        |OPENINGS : |BFD :{self.log_open_bfd[i]} |AFD:{self.log_open_afd[i]}')
            print(f'        |RAISES')
            print(f'             |RAISE BD: |RAISE:{self.total_raise_logs_before_draw[i]} |TIMES R:{self.times_raise_logs_before_draw[i]}')
            print(f'             |RAISE AD: |RAISE:{self.total_raise_logs[i]} |TIMES R:{self.times_raise_logs[i]}')
            print(f'             |HAND: {self.hands_log[i]} GUESS: {self.possible_hand_guess_log[i]} CARDS THROWN: {self.cards_thrown_away_log[i]} PLAYSTYLE: pre-D {self.log_pre_draw[i]}, post_D {self.log_post_draw[i]}')
    
    def deduce_opponent(self):
        rounds_played = self.rounds-1
        pre_draw_agresssion = 0
        pre_draw_passiveness = 0
        
        post_draw_agresssion = 0
        post_draw_passiveness = 0
        if rounds_played > 2:
            time_open_NW_BD = 0
            time_raise_NW_BD = 0
            time_open_W_BD = 0
            time_raise_W_BD = 0
            time_open_and_raise_wbd = 0
            times_fold_BD = 0
            ave_raise_per_round_nwbd= {}
            open_per_round_nwbd = {}
            ave_raise_per_round_wbd= {}
            open_per_round_wbd = {}
            folds_bd = {}

            # takes each round where it found an opening or raise and adds it to the ave_raise_per_round and open_per_round
            for i in range(1,rounds_played): 
                if self.log_wins_before_draw[i] == 0: #if not won before draw
                    if self.log_open_bfd[i] > 0:# Opponent opened 
                        time_open_NW_BD += 1
                        open_per_round_nwbd[i] = self.log_open_bfd[i] # log opening
                    if self.times_raise_logs_before_draw[i] > 0: # Opponent raised
                        time_raise_NW_BD += 1
                        ave_raise_per_round_nwbd[i] = self.total_raise_logs_before_draw[i]/self.times_raise_logs_before_draw[i] #log raise
                
                if self.log_wins_before_draw[i] == 1: #if won before draw
                    if self.log_open_bfd[i] > 0:# Opponent opened 
                        time_open_W_BD += 1
                        open_per_round_wbd[i] = self.log_open_bfd[i] # log opening
                    if self.times_raise_logs_before_draw[i] > 0: # Opponent raised
                        time_raise_W_BD += 1
                        ave_raise_per_round_wbd[i] = self.total_raise_logs_before_draw[i]/self.times_raise_logs_before_draw[i] #log raise
                    if self.log_open_bfd[i] > 0 and self.times_raise_logs_before_draw[i] > 0:
                        time_open_and_raise_wbd +=1

                if self.log_fold_bd[i] == 1: # Opponent folded before the drawstep
                    folds_bd[i] = 1    
                    times_fold_BD +=1
                
            for key in folds_bd:
                if key not in open_per_round_nwbd or key not in ave_raise_per_round_nwbd:
                    pre_draw_passiveness +=1

            # 0.6 set as a probability that it was a bad start hand. 0.6 is a guess and should be chanced to a more accurate number 
            pre_draw_agresssion += (time_open_W_BD + time_raise_W_BD + time_open_and_raise_wbd)*0.65
            
            for key in open_per_round_nwbd: # check each round that had a opening
                # check if hand was shown
                hand_type = "NAN"
                if self.hands_log[key]:
                    hand_type = self.evaluate_hand(self.hands_log[key])   
                else: # hand was not shown, go by hand guess
                    hand_type = self.possible_hand_guess_log[key]
                # if shown/guessed hand_type was low or folded

                if (self.hands_log[key] and (hand_type == "High_Card" or self.possible_hand_guess_log[key] == "High_Card")) or  (hand_type == "One_Pair" and self.log_open_bfd[key]/(self.log_open_bfd[key]+self.log_chip[key]) >0.3) or self.log_fold_bd[key] == 1:
                        pre_draw_agresssion +=1
            
            for key in ave_raise_per_round_nwbd:
                hand_type = "NAN"
                if self.hands_log[key]:
                    hand_type = self.evaluate_hand(self.hands_log[key])   
                else: # hand was not shown, go by hand guess
                    hand_type = self.possible_hand_guess_log[key]
                # if shown/guessed hand_type was low or folded
                if (self.hands_log[key] and (hand_type == "High_Card" or self.possible_hand_guess_log[key] == "High_Card")) or (hand_type == "One_Pair" and ave_raise_per_round_nwbd[key]/(ave_raise_per_round_nwbd[key]+self.log_chip[key]) >0.3) or self.log_fold_bd[key] == 1:
                        pre_draw_agresssion +=1

        

            # not win 
            time_open_NW_AD = 0
            time_raise_NW_AD = 0
            ave_raise_per_round_nwad= {}
            open_per_round_nwad = {}
            # undisputed win
            time_open_UW_AD = 0
            time_raise_UW_AD = 0
            ave_raise_per_round_wuad= {}
            open_per_round_wuad = {}
            folds_ad = {}

            # win disputed
            time_open_W_AD = 0
            time_raise_W_AD = 0
            ave_raise_per_round_wad= {}
            open_per_round_wad = {}


            time_open_and_raise_wad = 0
            times_fold_AD = 0
            
            open_per_round_ad = {}
            
            # POST
            for i in range(1,rounds_played): 
                if self.log_wins_undisputed[i] == 1 and self.log_wins_before_draw[i] == 0: # if opponent won undisputed 
                    if self.log_open_afd[i] > 0:    # if it opened after the draw
                        time_open_UW_AD += 1
                        open_per_round_wuad[i] = self.log_open_afd[i] 
                    if self.times_raise_logs[i] -self.times_raise_logs_before_draw[i] >0: # if it raised/betted after draw
                        time_raise_UW_AD += 1
                        ave_raise_per_round_wuad[i] =self.total_raise_logs[i] -self.total_raise_logs_before_draw[i]

                if self.log_wins[i] == 0:  # if it did not win the round
                    if self.log_open_afd[i] > 0: # if it opened after draw
                        time_open_NW_AD += 1
                        open_per_round_nwad[i] = self.log_open_afd[i]
                    if self.times_raise_logs[i] -self.times_raise_logs_before_draw[i] >0: # if it raised/betted after draw
                        time_raise_NW_AD += 1
                        ave_raise_per_round_nwad[i] = self.total_raise_logs[i] - self.total_raise_logs_before_draw[i]
                    if self.log_folds[i] == 1 and self.log_fold_bd[i] == 0: # if it folded after draw
                        folds_ad[i] = 1
                
                if self.log_wins[i] == 1  and self.log_wins_before_draw[i] == 0 and self.log_wins_undisputed[i] == 0: # win with showdown
                    if self.log_open_afd[i] > 0: # if it opened after draw
                        time_open_W_AD += 1
                        open_per_round_wad[i] = self.log_open_afd[i]
                    if self.times_raise_logs[i] -self.times_raise_logs_before_draw[i] >0: # if it raised/betted after draw
                        time_raise_W_AD += 1
                        ave_raise_per_round_wad[i] = self.total_raise_logs[i] - self.total_raise_logs_before_draw[i]
            
            for key in folds_ad:
                if key not in open_per_round_nwad or key not in ave_raise_per_round_nwad:
                    post_draw_passiveness +=1 
            
            for key in open_per_round_wuad: # for each undisputed win after card draw
                # check if it also betted/ opened before the post draw, can tell if it already had a good hand
                if key in ave_raise_per_round_nwbd or key in open_per_round_nwbd:
                    # check if hand guess was a bad hand
                    if self.HAND_RANK.index(self.possible_hand_guess_log[key]) < 3:  
                        # opponent had one_pair or less (guess)
                        post_draw_agresssion += 0.6
                    else:
                        post_draw_agresssion += 0.3
                else:
                    post_draw_agresssion += 0.1

            for key in ave_raise_per_round_wuad: # for each undisputed win after card draw
                # check if it also betted/ opened before the post draw, can tell if it already had a good hand
                if key in ave_raise_per_round_nwbd or key in open_per_round_nwbd:
                    # check if hand guess was a bad hand
                    if self.HAND_RANK.index(self.possible_hand_guess_log[key]) < 3: 
                        # opponent had one_pair or less (guess)
                        post_draw_agresssion += 0.6
                    else:
                        post_draw_agresssion += 0.3
                else:
                    post_draw_agresssion += 0.1

            for key in open_per_round_nwad: # for each non win after card draw
                # check if it also betted/ opened before the post draw, can tell if it already had a good hand
                if key in ave_raise_per_round_nwbd or key in open_per_round_nwbd:
                    if self.hands_log[key]: #if hand was shown
                        hand_type = self.evaluate_hand(self.hands_log[key])
                        if self.HAND_RANK.index(hand_type) < 3:
                            post_draw_agresssion += 1.4 # bad hand and cards was shown
                     
                    elif self.HAND_RANK.index(self.possible_hand_guess_log[key]) < 3:
                        post_draw_agresssion += 0.4
                    else:
                        post_draw_agresssion += 0.1

                else:
                    if self.hands_log[key]: #if hand was shown
                        hand_type = self.evaluate_hand(self.hands_log[key])
                        if self.HAND_RANK.index(hand_type) < 3:
                            post_draw_agresssion += 1 # bad hand and cards was shown
                    else: 
                        if self.HAND_RANK.index(self.possible_hand_guess_log[key]) < 3:
                            post_draw_agresssion += 0.2

            for key in ave_raise_per_round_nwad: # for each non win after card draw
                # check if it also betted/ opened before the post draw, can tell if it already had a good hand
                if key in ave_raise_per_round_nwbd or key in open_per_round_nwbd:
                    if self.hands_log[key]: #if hand was shown
                        hand_type = self.evaluate_hand(self.hands_log[key])
                        if self.HAND_RANK.index(hand_type) < 3:
                            post_draw_agresssion += 1.4 # bad hand and cards was shown
                     
                    elif self.HAND_RANK.index(self.possible_hand_guess_log[key]) < 3:
                        post_draw_agresssion += 0.4
                    else:
                        post_draw_agresssion += 0.1

                else:
                    if self.hands_log[key]: #if hand was shown
                        hand_type = self.evaluate_hand(self.hands_log[key])
                        if self.HAND_RANK.index(hand_type) < 3:
                            post_draw_agresssion += 1 # bad hand and cards was shown
                    else: 
                        if self.HAND_RANK.index(self.possible_hand_guess_log[key]) < 3:
                            post_draw_agresssion += 0.2
            
            for key in open_per_round_wad: # for each win with cards shown
                if key in ave_raise_per_round_nwbd or key in open_per_round_nwbd:
                    hand_type = self.evaluate_hand(self.hands_log[key])
                    if self.HAND_RANK.index(hand_type) < 3:
                        post_draw_agresssion += 0.5 # bad hand and cards was shown
            
            for key in ave_raise_per_round_wad: # for each win with cards shown
                if key in ave_raise_per_round_nwbd or key in open_per_round_nwbd:
                    hand_type = self.evaluate_hand(self.hands_log[key])
                    if self.HAND_RANK.index(hand_type) < 3:
                        post_draw_agresssion += 0.5 # bad hand and cards was shown 


        self.pre_draw = round(pre_draw_agresssion - pre_draw_passiveness, 2)
        self.post_draw = round(post_draw_agresssion -pre_draw_passiveness,2)
        return self.pre_draw, self.post_draw
    

        



                    






                

                






class Poker_Agent:
    def __init__(self,name):
        self.RANKS = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        self.HAND_RANK = ["NAN","High_Card","One_Pair","Two_Pair","Three_of_a_Kind","Straight","Flush","Full_House","Four_of_a_Kind","Straight_Flush"]
        self.agent_name = name
        self.p = prob_calculator()
        self.hand =[]
        self.opponents = {}
        self.rounds = 1
        self.has_drawn = False
        self.bluff_oppurtunity = False
    
    def set_hand(self,hand):
        self.hand = hand
        
    def get_hand_strength_and_prob(self):
        self.p.update(self.hand)
        hand_t, hand_val =self.p.evaluate_hand(self.hand)
        prob = self.p.probability_oponent_has_better_hand(hand_t, hand_val)
        return hand_t, hand_val, prob

    def cards_to_throw(self):
        self.has_drawn = True
        cards_to_throw, blufflag = ch.queryCardsToThrow(self.hand)
        self.bluff_oppurtunity = True if blufflag == 1 else False
        ct = cards_to_throw.split()
        s= ''
        for c in ct:
            s += str(c) +' '
        return s
    
    def new_round(self):

        self.p.reset()
        self.p.reset_removed_cards()
        self.has_drawn = False
        self.bluff_oppurtunity = False
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
                    self.opponents[key].wsin_undisputed(0)
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

    def get_table_playstyle(self):
        '''Returns the playstyle of each opponent'''
        pre_draw = 0
        post_draw = 0
        for opp in self.opponents:
            pre_draw += opp.pre_draw
            post_draw += opp.post_draw
        return pre_draw, post_draw
    
    def get_best_opponent_hand(self):
        '''Returns the best hand of the opponents'''
        best_hand = "NAN"
        for opp in self.opponents:
            if self.HAND_RANK.index(opp.possible_hand) > self.HAND_RANK.index(best_hand):
                best_hand = opp.possible_hand
        return best_hand
    #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Handle Opponent^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
