from collections import Counter
import random

# Poker hand rankings
RANK_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


def validate_hand(hand_):
    """Ensure the hand contains valid cards."""
    valid_suits = {'h', 'd', 's', 'c'}
    valid_ranks = set(RANK_VALUES)
    for card in hand_:
        if len(card) < 2 or card[:-1] not in valid_ranks or card[-1] not in valid_suits:
            raise ValueError(f"Invalid card format: {card}")

def hand_strength(hand_):
    """Evaluate hand strength and categorize it"""
    ranks = [card[:-1] for card in hand_]
    suits = [card[-1] for card in hand_]
    rank_counts = Counter(ranks)
    unique_ranks = len(rank_counts)
    max_count = max(rank_counts.values())
    sorted_ranks = sorted([RANK_VALUES.index(rank) for rank in ranks])

    #Check for flush
    is_flush = len(set(suits)) == 1

    #Check for straight (including special case for A-2-3-4-5)
    is_straight = (
        len(sorted_ranks) == 5 and sorted_ranks[-1] - sorted_ranks[0] == 4
    ) or set(sorted_ranks) == {0, 1, 2, 3, 12}  # A-2-3-4-5

    #Adjust sorted_ranks for A-2-3-4-5 straight (Ace treated as low card)
    if set(sorted_ranks) == {0, 1, 2, 3, 12}:
        sorted_ranks = [0, 1, 2, 3, 4]

    #Categorize the hand
    if is_flush and is_straight:
        return ("straight_flush", sorted_ranks)
    if max_count == 4:
        return ("four_of_a_kind", rank_counts)
    if max_count == 3 and unique_ranks == 2:
        return ("full_house", rank_counts)
    if is_flush:
        return ("flush", sorted_ranks)
    if is_straight:
        return ("straight", sorted_ranks)
    if max_count == 3:
        return ("three_of_a_kind", rank_counts)
    if max_count == 2 and unique_ranks == 3:
        return ("two_pair", rank_counts)
    if max_count == 2:
        return ("one_pair", rank_counts)
    return ("high_card", rank_counts)

def queryCardsToThrow(hand_):
    """
    Decide which cards to throw to maximize the potential of forming a stronger hand.
    Return a string of cards to throw away in the format: 'card1 card2 '.
    """
    #Bluff flag
    Bluff_Angle = 0

    #Validate the hand
    validate_hand(hand_)

    #Analyze the hand
    strength, data = hand_strength(hand_)

    #Determine which cards to throw
    throwArray = []
    if strength in {"straight_flush", "four_of_a_kind", "full_house", "flush", "straight"}:
        #Strong hands keep all cards
        throwArray = []
    elif strength == "three_of_a_kind":
        #Keep three of a kind discard the other two
        three_rank = [rank for rank, count in data.items() if count == 3][0]
        throwArray = [card for card in hand_ if card[:-1] != three_rank]
    elif strength == "two_pair":
        #Keep two pairs discard the other
        pairs = [rank for rank, count in data.items() if count == 2]
        throwArray = [card for card in hand_ if card[:-1] not in pairs]
    elif strength == "one_pair":
        #Keep the pair and the highest card outside the pair if its J Q K or A
        pair_rank = [rank for rank, count in data.items() if count == 2][0]
        high_value_ranks = {'J', 'Q', 'K', 'A'}
        non_pair_cards = [card for card in hand_ if card[:-1] != pair_rank]
        high_card = max(non_pair_cards, key=lambda card: RANK_VALUES.index(card[:-1]), default=None)

        #Had a significant high_card
        if high_card and high_card[:-1] in high_value_ranks:
            throwArray = [card for card in hand_ if card[:-1] != pair_rank and card != high_card]
            if random.random() > 0.3:
                Bluff_Angle = 1

        else:
            throwArray = [card for card in hand_ if card[:-1] != pair_rank]
    elif strength == "high_card":
        # Check for almost-flush or almost-straight cases
        suits = [card[-1] for card in hand_]
        most_common_suit = max(set(suits), key=suits.count)
        suited_cards = [card for card in hand_ if card[-1] == most_common_suit]

        if len(suited_cards) >= 4:  #Almost flush
            throwArray = [card for card in hand_ if card[-1] != most_common_suit]
        else:
            #Check for almost straight
            sorted_ranks = sorted([RANK_VALUES.index(card[:-1]) for card in hand_])
            for i in range(len(sorted_ranks) - 3):
                if sorted_ranks[i + 3] - sorted_ranks[i] <= 4:
                    straight_ranks = set(sorted_ranks[i:i + 4])
                    throwArray = [card for card in hand_ if RANK_VALUES.index(card[:-1]) not in straight_ranks]
                    break
            else:
                # Weak hand: Keep all high-value cards (J, Q, K, A)
                high_value_ranks = {'J', 'Q', 'K', 'A'}
                throwArray = [card for card in hand_ if card[:-1] not in high_value_ranks]
                if len(throwArray) <= 2 and random.random() <= 0.2:
                    Bluff_Angle = 1
                    

    #Make string separated by space
    return ' '.join(throwArray) + ' ', Bluff_Angle