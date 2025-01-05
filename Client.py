import socket
import random
import ClientBase
from Agent_1.Agent import Poker_Agent

# IP address and port
TCP_IP = '127.0.0.1'
TCP_PORT = 3000
BUFFER_SIZE = 1024


# Agent
POKER_CLIENT_NAME = 'FIIIIIIIIIIITAAAAAAA'
#POKER_CLIENT_NAME = 'FUUUUUUUUUUUUUUUUUUK'

CURRENT_HAND = []


a = Poker_Agent(POKER_CLIENT_NAME)

class pokerGames(object):
    def __init__(self):
        self.PlayerName = POKER_CLIENT_NAME
        self.Chips = 0
        self.CurrentHand = []
        self.Ante = 0
        self.playersCurrentBet = 0
        print('test')

'''
* Gets the name of the player.
* @return  The name of the player as a single word without space. <code>null</code> is not a valid answer.
'''
def queryPlayerName(_name):
    if _name is None:
        _name = POKER_CLIENT_NAME
    return _name

'''
* Modify queryOpenAction() and add your strategy here
* Called during the betting phases of the game when the player needs to decide what open
* action to choose.
* @param minimumPotAfterOpen   the total minimum amount of chips to put into the pot if the answer action is
*                              {@link BettingAnswer#ACTION_OPEN}.
* @param playersCurrentBet     the amount of chips the player has already put into the pot (dure to the forced bet).
* @param playersRemainingChips the number of chips the player has not yet put into the pot.
* @return                      An answer to the open query. The answer action must be one of
*                              {@link BettingAnswer#ACTION_OPEN}, {@link BettingAnswer#ACTION_ALLIN} or
*                              {@link BettingAnswer#ACTION_CHECK }. If the action is open, the answers
*                              amount of chips in the anser must be between <code>minimumPotAfterOpen</code>
*                              and the players total amount of chips (the amount of chips alrady put into
*                              pot plus the remaining amount of chips).
'''
def queryOpenAction(_minimumPotAfterOpen, _playersCurrentBet, _playersRemainingChips):
    print(f'queryOpenAction--------------- {POKER_CLIENT_NAME}')
    print(f'    |minpotafterOpen {_minimumPotAfterOpen} playersCurBet {_playersCurrentBet} remainingchips {_playersRemainingChips}')
    s,prob = a.decide_init_bet()
    if s == 'bet_rank_1':
        print('     |bet_rank_1')
        to_bet =_minimumPotAfterOpen +3 #int(_minimumPotAfterOpen + _playersCurrentBet +3) #+ random.randint(0, 15)
        if to_bet < _playersRemainingChips:
            print('open')
            return    ClientBase.BettingAnswer.ACTION_OPEN, to_bet
    if s == 'bet_rank_2':
        print('     |bet_rank_2')
        to_bet = _minimumPotAfterOpen +2 #int(_minimumPotAfterOpen + _playersCurrentBet +2)
        if to_bet < _playersRemainingChips:
            print('open')
            return    ClientBase.BettingAnswer.ACTION_OPEN, to_bet
    if s == 'bet_rank_3':
        print('     |bet_rank_3')
        to_bet = _minimumPotAfterOpen +1 #int(_minimumPotAfterOpen + _playersCurrentBet + +1)
        if to_bet < _playersRemainingChips:
            print('open')
            return    ClientBase.BettingAnswer.ACTION_OPEN, to_bet
    if s == 'bet_rank_4':
        print('     |bet_rank_4')
        print('open')
        return ClientBase.BettingAnswer.ACTION_OPEN, _minimumPotAfterOpen +1#int(_minimumPotAfterOpen + _playersCurrentBet +1)
    print('     |else check')
    return ClientBase.BettingAnswer.ACTION_CHECK


'''
* Modify queryCallRaiseAction() and add your strategy here
* Called during the betting phases of the game when the player needs to decide what call/raise
* action to choose.
* @param maximumBet                the maximum number of chips one player has already put into the pot.
* @param minimumAmountToRaiseTo    the minimum amount of chips to bet if the returned answer is {@link BettingAnswer#ACTION_RAISE}.
* @param playersCurrentBet         the number of chips the player has already put into the pot.
* @param playersRemainingChips     the number of chips the player has not yet put into the pot.
* @return                          An answer to the call or raise query. The answer action must be one of
*                                  {@link BettingAnswer#ACTION_FOLD}, {@link BettingAnswer#ACTION_CALL},
*                                  {@link BettingAnswer#ACTION_RAISE} or {@link BettingAnswer#ACTION_ALLIN }.
*                                  If the players number of remaining chips is less than the maximum bet and
*                                  the players current bet, the call action is not available. If the players
*                                  number of remaining chips plus the players current bet is less than the minimum
*                                  amount of chips to raise to, the raise action is not available. If the action
*                                  is raise, the answers amount of chips is the total amount of chips the player
*                                  puts into the pot and must be between <code>minimumAmountToRaiseTo</code> and
*                                  <code>playersCurrentBet+playersRemainingChips</code>.
'''
def queryCallRaiseAction(_maximumBet, _minimumAmountToRaiseTo, _playersCurrentBet, _playersRemainingChips):
    print('-------------------------------------------queryCallRaiseAction-----------------')

    print(f'    |{POKER_CLIENT_NAME} _maximumBet {_maximumBet} minAmountToRaise { _minimumAmountToRaiseTo} _playersCurrentBet {_playersCurrentBet}')
    
    s,prob = a.decide_raise_call()
    fold = random.randint(0, 10)
    if fold > 7:
        return    ClientBase.BettingAnswer.ACTION_FOLD
    #if _maximumBet + _playersCurrentBet > 
    if s == 'bet_rank_1':
        to_bet = int(_minimumAmountToRaiseTo + 3)
        print(f'    |bet_rank_1 , to bet {to_bet}')
        if to_bet < _playersRemainingChips and _playersCurrentBet < 70:
            print('     |raise')
            return    ClientBase.BettingAnswer.ACTION_RAISE, to_bet
    elif s == 'bet_rank_2':
        to_bet =int( _minimumAmountToRaiseTo +2)
        print(f'    |bet_rank_2 , to bet {to_bet}')
        if to_bet < _playersRemainingChips and _playersCurrentBet < 30:
            print('     |raise')
            return    ClientBase.BettingAnswer.ACTION_RAISE, to_bet
    elif s == 'bet_rank_3':
        to_bet =int( _minimumAmountToRaiseTo + 1)
        print(f'    |bet_rank_3 , to bet {to_bet}')
        if to_bet < _playersRemainingChips and _playersCurrentBet < 30:
            print('     |raise')
            return    ClientBase.BettingAnswer.ACTION_RAISE, to_bet
    elif s == 'fold':
        print('     |Fold')
        ClientBase.BettingAnswer.ACTION_FOLD
    print('     |else call')
    return ClientBase.BettingAnswer.ACTION_CALL

'''
* Modify queryCardsToThrow() and add your strategy to throw cards
* Called during the draw phase of the game when the player is offered to throw away some
* (possibly all) of the cards on hand in exchange for new.
* @return  An array of the cards on hand that should be thrown away in exchange for new,
*          or <code>null</code> or an empty array to keep all cards.
* @see     #infoCardsInHand(ca.ualberta.cs.poker.Hand)
'''
def queryCardsToThrow(_hand):
    print('-------------------------------------------queryCardsToThrow---------------')
    print(f'    |hand {_hand}')
    return a.cards_to_throw()




# InfoFunction:

'''
* Called when a new round begins.
* @param round the round number (increased for each new round).
'''
def infoNewRound(_round):
    a.opponent_new_round()
    print('Starting Round: ' + _round )

'''
* Called when the poker server informs that the game is completed.
'''
def infoGameOver():
    print('The game is over.')
    a.print_oppnent_results()
    

'''
* Called when the server informs the players how many chips a player has.
* @param playerName    the name of a player.
* @param chips         the amount of chips the player has.
'''
def infoPlayerChips(_playerName, _chips):
    a.add_opponent(_playerName,_chips)
    a.update_opponent_chips(_playerName,_chips)

    print('The player ' + _playerName + ' has ' + _chips + 'chips')

'''
* Called when the ante has changed.
* @param ante  the new value of the ante.
'''
def infoAnteChanged(_ante):
    print('The ante is: ' + _ante)

'''
* Called when a player had to do a forced bet (putting the ante in the pot).
* @param playerName    the name of the player forced to do the bet.
* @param forcedBet     the number of chips forced to bet.
'''
def infoForcedBet(_playerName, _forcedBet):
    #print("Player "+ _playerName +" made a forced bet of "+ _forcedBet + " chips.")
    pass

'''
* Called when a player opens a betting round.
* @param playerName        the name of the player that opens.
* @param openBet           the amount of chips the player has put into the pot.
'''
def infoPlayerOpen(_playerName, _openBet):
    a.opponent_open(_playerName, _openBet)
    #print("Player "+ _playerName + " opened, has put "+ _openBet +" chips into the pot.")
    

'''
* Called when a player checks.
* @param playerName        the name of the player that checks.
'''
def infoPlayerCheck(_playerName):
    if _playerName != POKER_CLIENT_NAME:
        print("     |Player "+ _playerName +" checked.")
    pass

'''
* Called when a player raises.
* @param playerName        the name of the player that raises.
* @param amountRaisedTo    the amount of chips the player raised to.
'''
def infoPlayerRise(_playerName, _amountRaisedTo):
    if _playerName != POKER_CLIENT_NAME:
        a.opponent_raised(_playerName, int(_amountRaisedTo))
        print("     |Player "+_playerName +" raised to "+ _amountRaisedTo+ " chips.")
    pass

'''
* Called when a player calls.
* @param playerName        the name of the player that calls.
'''
def infoPlayerCall(_playerName):
    if _playerName != POKER_CLIENT_NAME:
        print("     |Player "+_playerName +" called.")
    pass

'''
* Called when a player folds.
* @param playerName        the name of the player that folds.
'''
def infoPlayerFold(_playerName):
    if _playerName != POKER_CLIENT_NAME:
        a.opponent_fold(_playerName)
        print("     |Player "+ _playerName +" folded.")

'''
* Called when a player goes all-in.
* @param playerName        the name of the player that goes all-in.
* @param allInChipCount    the amount of chips the player has in the pot and goes all-in with.
'''
def infoPlayerAllIn(_playerName, _allInChipCount):
    #print("Player "+_playerName +" goes all-in with a pot of "+_allInChipCount+" chips.")
    pass

'''
* Called when a player has exchanged (thrown away and drawn new) cards.
* @param playerName        the name of the player that has exchanged cards.
* @param cardCount         the number of cards exchanged.
'''
def infoPlayerDraw(_playerName, _cardCount):
    a.oponent_cards_thrown(_playerName, _cardCount)
    #print("Player "+ _playerName + " exchanged "+ _cardCount +" cards.")

'''
* Called during the showdown when a player shows his hand.
* @param playerName        the name of the player whose hand is shown.
* @param hand              the players hand.
'''
def infoPlayerHand(_playerName, _hand):
    a.opponent_hand(_playerName,_hand)
    print("Player "+ _playerName +" hand " + str(_hand))


def infoCardsInHand(_hand):
    a.set_hand(_hand[:])
    #print('infoCardsInHand')
    #print(f'ch {a.get_hand()}')
    




'''
* Called during the showdown when a players undisputed win is reported.
* @param playerName    the name of the player whose undisputed win is anounced.
* @param winAmount     the amount of chips the player won.
'''
def infoRoundUndisputedWin(_playerName, _winAmount):
    a.opponent_win(_playerName,True)
    #a.opponent_win_undisputed (_playerName)
    print("Player" + _playerName +" won "+ _winAmount +" chips undisputed.")
    a.new_round()

'''
* Called during the showdown when a players win is reported. If a player does not win anything,
* this method is not called.
* @param playerName    the name of the player whose win is anounced.
* @param winAmount     the amount of chips the player won.
'''
def infoRoundResult(_playerName, _winAmount):
    a.opponent_win(_playerName,False)
    print("Player "+ _playerName +" won " + _winAmount + " chips.")
    a.new_round()

