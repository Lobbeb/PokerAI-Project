import socket
import random
import time

import ClientBase  # This is needed for the BettingAnswer constants

# -----------------------------------------------------------------------------
# 1) REFLEX AGENT CLASS
# -----------------------------------------------------------------------------

import random
import ClientBase

class ReflexAgent:
    def __init__(self, name="ReflexAgent"):
        self.name = name

    def queryPlayerName(self, proposed_name):
        """
        Return the agent's name when the server asks: 'Name?'.
        """
        return proposed_name if proposed_name else self.name

    def queryOpenAction(self, minimumPotAfterOpen, playersCurrentBet, playersRemainingChips):
        """
        Called when the server says: 'Open?'
        Decide whether to Open (and how much) or Check.
        """
        print("ReflexAgent: queryOpenAction called.")
        
        # If we do NOT have enough chips to meet min open, just check (or go all-in).
        if playersRemainingChips < minimumPotAfterOpen:
            # Example: just check if that's allowed
            return ClientBase.BettingAnswer.ACTION_CHECK
        
        # Otherwise, we can open somewhere between minimumPotAfterOpen and playersRemainingChips
        open_amount = random.randint(minimumPotAfterOpen, playersRemainingChips)
        return (ClientBase.BettingAnswer.ACTION_OPEN, open_amount)

    def queryCallRaiseAction(self, maximumBet, minimumAmountToRaiseTo,
                             playersCurrentBet, playersRemainingChips):
        """
        Called when the server says: 'Call/Raise?'
        Decide whether to Fold, Call, Raise (and how much), or go All-in.
        
        maximumBet = the highest amount any other player has put in
        minimumAmountToRaiseTo = the minimum total bet we must make to 'raise'
        playersCurrentBet = how much we have already put in
        playersRemainingChips = how many chips we have left
        """
        print("ReflexAgent: queryCallRaiseAction called.")

        # 1) Check if we can CALL:
        #    To call, we need at least (maximumBet - playersCurrentBet) chips.
        needed_to_call = max(0, maximumBet - playersCurrentBet)
        
        # 2) If we do NOT have enough to call, we might fold or go all-in.
        if needed_to_call > playersRemainingChips:
            # Example: fold if we cannot call
            return ClientBase.BettingAnswer.ACTION_FOLD
        
        # 3) If we have exactly enough or slightly more, let's just call
        #    (or we could do all-in if we like).
        if needed_to_call == playersRemainingChips:
            # Example: call (which effectively is all-in)
            return ClientBase.BettingAnswer.ACTION_CALL
        
        # 4) Otherwise, we can at least call. Now check if we can RAISE:
        #    If playersRemainingChips + playersCurrentBet >= minimumAmountToRaiseTo,
        #    we can raise. That means we have (playersRemainingChips >= minRaiseNeeded).
        minRaiseNeeded = minimumAmountToRaiseTo - playersCurrentBet
        
        if playersRemainingChips >= minRaiseNeeded:
            # We can raise. Let’s pick a random raise in [minRaiseTo, playersCurrentBet+playersRemainingChips].
            raise_amount = random.randint(minimumAmountToRaiseTo, 
                                          playersCurrentBet + playersRemainingChips)
            # But also clamp to our actual max (playersCurrentBet+playersRemainingChips):
            # (the randint logic above might already do that, but it's safer to clamp)
            raise_amount = min(raise_amount, playersCurrentBet + playersRemainingChips)
            return (ClientBase.BettingAnswer.ACTION_RAISE, raise_amount)
        
        # 5) If we cannot raise, just call:
        return ClientBase.BettingAnswer.ACTION_CALL

    def queryCardsToThrow(self, hand):
        """
        Called when the server says: 'Draw?'
        Return a list of which cards to discard.
        For example, if hand == ["AH", "7D", "3C", "9S", "KD"], you might discard one card.
        """
        print("ReflexAgent: queryCardsToThrow called.")
        if not hand:
            return []
        # Randomly discard exactly one card as a placeholder strategy
        card_to_throw = random.choice(hand)
        return [card_to_throw]


# (Optional) Helper class if you want to keep these "info" functions:
class GameCommunicationHelper:
    @staticmethod
    def infoNewRound(round_number):
        print(f"Starting Round: {round_number}")

    @staticmethod
    def infoGameOver():
        print("The game is over.")

    @staticmethod
    def infoPlayerChips(player_name, chips):
        print(f"The player {player_name} has {chips} chips.")

    @staticmethod
    def infoAnteChanged(ante):
        print(f"The ante is: {ante}")

    @staticmethod
    def infoForcedBet(player_name, forced_bet):
        print(f"Player {player_name} made a forced bet of {forced_bet} chips.")

    @staticmethod
    def infoPlayerOpen(player_name, open_bet):
        print(f"Player {player_name} opened, has put {open_bet} chips into the pot.")

    @staticmethod
    def infoPlayerCheck(player_name):
        print(f"Player {player_name} checked.")

    @staticmethod
    def infoPlayerRise(player_name, amount_raised_to):
        print(f"Player {player_name} raised to {amount_raised_to} chips.")

    @staticmethod
    def infoPlayerCall(player_name):
        print(f"Player {player_name} called.")

    @staticmethod
    def infoPlayerFold(player_name):
        print(f"Player {player_name} folded.")

    @staticmethod
    def infoPlayerAllIn(player_name, all_in_chip_count):
        print(f"Player {player_name} goes all-in with a pot of {all_in_chip_count} chips.")

    @staticmethod
    def infoPlayerDraw(player_name, card_count):
        print(f"Player {player_name} exchanged {card_count} cards.")

    @staticmethod
    def infoPlayerHand(player_name, hand):
        print(f"Player {player_name} hand: {hand}")

    @staticmethod
    def infoRoundUndisputedWin(player_name, win_amount):
        print(f"Player {player_name} won {win_amount} chips undisputed.")

    @staticmethod
    def infoRoundResult(player_name, win_amount):
        print(f"Player {player_name} won {win_amount} chips.")


# -----------------------------------------------------------------------------
# 2) NETWORKING + "MAIN" LOOP
# -----------------------------------------------------------------------------

# Change these if your server is on a different IP/port:
TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024

# The name that will appear at the poker table:
POKER_CLIENT_NAME = 'ReflexAgent1'

# Create an instance of your ReflexAgent:
reflex_agent = ReflexAgent(name=POKER_CLIENT_NAME)

# Keep track of the current hand in a list of strings, e.g. ["AH", "7D", "3C", ...]
CURRENT_HAND = []

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    print(f"Connected to Poker Server at {TCP_IP}:{TCP_PORT} as '{POKER_CLIENT_NAME}'.")

    game_on = True
    msg_buffer = []

    while game_on:
        try:
            data = s.recv(BUFFER_SIZE)
            if not data:
                break

            # Break the data into tokens
            tokens = data.split()

            # Accumulate tokens into msg_buffer
            for t in tokens:
                msg_buffer.append(t)

            # Process commands in msg_buffer
            while len(msg_buffer) > 0:
                cmd = msg_buffer.pop(0).decode('ascii')

                if cmd == 'Name?':
                    # The server wants the player's name
                    chosen_name = reflex_agent.queryPlayerName(POKER_CLIENT_NAME)
                    s.send((f"Name {chosen_name}\n").encode())

                elif cmd == 'Chips':
                    # e.g. "Chips <name> <amount>"
                    # read the name
                    player_name = msg_buffer.pop(0).decode('ascii')
                    # read the chip count
                    chip_count = msg_buffer.pop(0).decode('ascii')
                    # (Optional) store or print
                    # GameCommunicationHelper.infoPlayerChips(player_name, chip_count)

                elif cmd == 'Ante_Changed':
                    # e.g. "Ante_Changed 10"
                    ante_value = msg_buffer.pop(0).decode('ascii')
                    # (Optional) store or print
                    # GameCommunicationHelper.infoAnteChanged(ante_value)

                elif cmd == 'Forced_Bet':
                    # e.g. "Forced_Bet <name> <betAmount>"
                    name_forced = msg_buffer.pop(0).decode('ascii')
                    bet_amount = msg_buffer.pop(0).decode('ascii')
                    print(f"--- Round Start ---")
                    # (Optional) store or print
                    # GameCommunicationHelper.infoForcedBet(name_forced, bet_amount)

                elif cmd == 'Open?':
                    # e.g. "Open? <minPotAfterOpen> <playersCurrentBet> <playersRemainingChips>"
                    minPotAfterOpen = int(msg_buffer.pop(0).decode('ascii'))
                    currentBet = int(msg_buffer.pop(0).decode('ascii'))
                    remainingChips = int(msg_buffer.pop(0).decode('ascii'))

                    decision = reflex_agent.queryOpenAction(minPotAfterOpen, currentBet, remainingChips)

                    # Send decision back to server
                    if isinstance(decision, str):
                        # e.g. "Check" or "All-in"
                        s.send((decision + "\n").encode())
                    else:
                        # e.g. ("Open", amount)
                        action_str, amount = decision
                        s.send((f"{action_str} {amount}\n").encode())

                elif cmd == 'Call/Raise?':
                    # e.g. "Call/Raise? <maxBet> <minRaiseTo> <playersCurrentBet> <playersRemainingChips>"
                    max_bet = int(msg_buffer.pop(0).decode('ascii'))
                    min_raise_to = int(msg_buffer.pop(0).decode('ascii'))
                    current_bet = int(msg_buffer.pop(0).decode('ascii'))
                    remaining_chips = int(msg_buffer.pop(0).decode('ascii'))

                    decision = reflex_agent.queryCallRaiseAction(max_bet, min_raise_to, current_bet, remaining_chips)

                    if isinstance(decision, str):
                        # e.g. "Fold", "All-in", or "Call"
                        s.send((decision + "\n").encode())
                    else:
                        action_str, amount = decision
                        s.send((f"{action_str} {amount}\n").encode())

                elif cmd == 'Cards':
                    # Server is giving us our 5 cards
                    CURRENT_HAND.clear()  # reset old hand
                    for _ in range(5):
                        card = msg_buffer.pop(0).decode('ascii')
                        CURRENT_HAND.append(card)
                    print(f"Got new hand: {CURRENT_HAND}")

                elif cmd == 'Draw?':
                    # We can discard some cards
                    discard_list = reflex_agent.queryCardsToThrow(CURRENT_HAND)

                    if discard_list:
                        # e.g. if discard_list == ["AH", "7D"], we want: "Throws AH 7D"
                        cards_str = " ".join(discard_list)
                        s.send((f"Throws {cards_str}\n").encode())
                    else:
                        # no cards to throw
                        s.send("Throws\n".encode())

                elif cmd == 'Round':
                    # e.g. "Round 1"
                    round_number = msg_buffer.pop(0).decode('ascii')
                    # (Optional) store or print
                    # GameCommunicationHelper.infoNewRound(round_number)

                elif cmd == 'Game_Over':
                    # The server says the entire game is done
                    # (Optional) store or print
                    # GameCommunicationHelper.infoGameOver()
                    print("Game Over!")
                    game_on = False

                else:
                    # Possibly other commands like "Player_Open", "Player_Check", etc.
                    # Just skip the relevant arguments so we don't leave them behind
                    # or optionally handle them for logging
                    #
                    # Example: "Player_Open <name> <amount>"
                    # We can read however many arguments we expect, or ignore them.
                    #
                    # If you want to do a thorough handling, you'd need if/elif for each
                    # of those commands. But it's not strictly required for the game to run.
                    pass

        except socket.timeout:
            # In case the socket times out
            break

    s.close()
    print("Disconnected from server.")


if __name__ == "__main__":
    main()
