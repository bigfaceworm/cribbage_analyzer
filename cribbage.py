#!/usr/bin/python
#
# Final project for CS50 Introduction to Programming with Python
#
# See README.md for details
#

import sys
from collections import Counter
import itertools
import functools
import operator
import re
# from itertools import tee

# Hand of cards is a list of 4-6 cards
# Card is a rank and a suit, rank is 1-13

class Card:
    _Suits = {'C', 'D', 'H', 'S'}
    _Ranks = {1,2,3,4,5,6,7,8,9,10,11,12,13}
    _RankSymbolToValue = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
                          '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10,
                          'J': 11, 'Q': 12, 'K': 13, 'A': 1}
    _RankValueToSymbol = {1: 'A', 2: '2', 3: '3', 4: '4', 5: '5',
                          6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
                          11: 'J', 12: 'Q', 13: 'K'}
    _Deck = None
    
    # Card has rank and suit
    def __init__(self, rank, suit):
        if rank not in Card._Ranks:
            raise ValueError("Unknown rank {}".format(rank))
        if suit not in Card._Suits:
            raise ValueError("Unknown suit {}".format(suit))
        
        self._rank = rank
        self._suit = suit

    @classmethod
    def Deck(cls):
        if cls._Deck == None:
            # build it
            cls._Deck = set()
            for it in itertools.product(cls._Ranks, cls._Suits):
                cls._Deck.add(Card(it[0], it[1]))
        return cls._Deck
    
    @classmethod
    def From_String(cls, card):
        cardstr = card.upper()

        # transform '10' to 'T' for easier processing
        # but first, eliminate T from input
        if 'T' in cardstr:
            raise ValueError('Invalid card: {}'.format(card))
        
        if len(cardstr) == 3 and '10' in cardstr:
            i = cardstr.find('10')
            if i == 0:
                cardstr = 'T' + cardstr[2]
            else:
                cardstr = 'T' + cardstr[0]

        # any valid cardstr now has length 2
        if len(cardstr) != 2:
            raise ValueError('Unknown card `{}`'.format(card))
        # try pulling out the suit first
        suit = ''
        rank = 0
        if cardstr[0] in Card._Suits:
            suit = cardstr[0]
            cardstr = cardstr[1]
        elif cardstr[1] in Card._Suits:
            suit = cardstr[1]
            cardstr = cardstr[0]
        elif len(cardstr) == 3 and cardstr[2] in Card._Suits:
            suit = cardstr[2]
            cards

        if cardstr[0] not in Card._RankSymbolToValue or suit == '':
            raise ValueError("Unknown card `{}`".format(card))

        rank = Card._RankSymbolToValue[cardstr[0]]

        return cls(rank, suit)
            

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return False

    def __lt__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Card):
            return self._rank < other._rank or self._rank == other._rank and self._suit < other._suit
        return False

    def __repr__(self):
        return "{0}{1}".format(Card._RankValueToSymbol[self._rank], self._suit)
    
    def __hash__(self):
        return hash(repr(self))

    @property
    def rank(self):
        return self._rank

    @property
    def suit(self):
        return self._suit


class Hand:
    # Hand is 2-6 cards
    # 
    def __init__(self, cards = []):
        if isinstance(cards, Hand):
            # copy constructor
            self._cards = cards.cards
            return
        
        # length 2-6
        if len(cards) not in range(2,7):
            raise ValueError("Hand {} is not 2-6 cards".format(cards))
        for c in cards:
            if not isinstance(c, Card):
                raise ValueError("Expected a card, was given: {}".format(c))
        cards = list(cards)
        cards.sort()
        # check for duplicates
        cset = set(cards)
        if len(cards) != len(cset):
            raise ValueError("The hand has duplicate cards: {} ".format(cards))

        self._cards = cards

    @classmethod
    def From_Strings(cls, inputlist):
        cardlist = []
        for c in inputlist:
            if isinstance(c, str):
                cardlist.append(Card.From_String(c))
            elif isinstance(c, Card):
                cardlist.append(c)
            else:
                raise ValueError("Expected a list of strings and/or cards, was given {} (input {})".format(c, inputlist))
        return Hand(cardlist)

    def __repr__(self):
        return "{}".format(self._cards)

    def __eq__(self, other):
        """Overrides the default implementation"""
        return self._cards == other._cards

    @property
    def cards(self):
        return self._cards


class CribbageHandAnalyzer:
    _Verbose = False
    
    def __init__(self, hand):
        self._hand = hand

    def __repr__(self):
        return "CribbageAnalyzer hand: {0}".format(self._hand)
    
    def score(self, starter=None, crib=False):
        if starter and not isinstance(starter, Card):
            raise TypeError('Expected starter to be a Card, given: ' + str(starter))
        if starter and starter in self._hand.cards:
            raise ValueError('Starter card ({}) is already in the hand {} !duplicate!'.format(starter, self._hand))
        
        # hand must be four cards
        if len(self._hand.cards) != 4:
            raise ValueError('Can only score hands of length 4, given the hand: ' + str(self._hand.cards))

        if CribbageHandAnalyzer._Verbose: print("Hand: {}, Starter: {}, crib: {}".format(self._hand, starter, crib))
        score = 0
        score += self.__computeFlush(starter, crib)
        if CribbageHandAnalyzer._Verbose: print("{:2} after flush".format(score))
        score += self.__computePairs(starter)
        if CribbageHandAnalyzer._Verbose: print("{:2} after pairs".format(score))
        score += self.__computeFifteens(starter)
        if CribbageHandAnalyzer._Verbose: print("{:2} after fifteens".format(score))
        score += self.__computeRuns(starter)
        if CribbageHandAnalyzer._Verbose: print("{:2} after runs".format(score))
        score += self.__computeNobs(starter)
        if CribbageHandAnalyzer._Verbose: print("{:2} after nobs".format(score))
        return score

    def __computeNobs(self, starter):
        cards = self._hand.cards.copy()
        if starter:
            for c in cards:
                if c.rank == 11 and starter.suit == c.suit:
                    return 1
        return 0
    
    def __computeFlush(self, starter, crib):
        # check for all in suit being the same
        cards = self._hand.cards.copy()
        score = 0
        target_suit = cards[0].suit
        for c in cards[1:4]:
            if c.suit != target_suit:
                return 0
        score += 4
        if starter and starter.suit == target_suit:
            score += 1

        # crib can only be a flush if all 5
        if crib and score == 4:
            score = 0

        return score

    def __computePairs(self, starter):
        # check for all pairs
        score = 0
        cards = self._hand.cards.copy()

        if starter != None:
            cards.append(starter)
            cards.sort()

        rank_counts = Counter()
        for c in cards:
            rank_counts[c.rank] += 1

        pair_counter = {0: 0, 1: 0, 2: 2, 3: 6, 4:12}
        for k,count in rank_counts.items():
            score += pair_counter[count]

        return score

    def __computeFifteens(self, starter):
        # check for all in suit being the same
        cards = self._hand.cards.copy()
        if starter != None:
            cards.append(starter)

        ranks = list(map(lambda x: x.rank if x.rank <= 10 else 10, cards))
        
        score = 0
        for numcards in range(2,len(cards)+1):
            it = itertools.combinations(ranks, numcards)
            sums = map(sum, it)
            sumlist = list(sums)
            score += sumlist.count(15)*2

        return score

    def __computeRuns(self, starter):
        score = 0
        cards = self._hand.cards.copy()
    
        if starter != None:
            cards.append(starter)
            cards.sort()
    
        ranks = list(map(lambda x: x.rank, cards))
        score = 0
        #### change loop to go from 5->3
        #### and if run is found, break out (only one length run need be found)
        for numcards in reversed(range(3, len(cards)+1)):
            it = itertools.combinations(ranks, numcards)

            for combo in it:
                citer = iter(combo)
                first = next(citer)
                sequence = 1
                for the_next in citer:
                    if first+sequence == the_next:
                        sequence += 1
                if sequence == numcards:
                    score += numcards

            if score > 0:
                break
    
        return score

def compute_hand_score(hand, starter=None):
    analyzer = CribbageHandAnalyzer(hand)
    return analyzer.score(starter=starter)

def parse_cribbage_hand(istring):
    # comma and/or space separated
    clist = re.split(' *, *| +', istring)
    if len(clist) not in {4,5,6}:
        raise ValueError("Expected 4, 5, or 6 cards, found: {}".format(len(clist)))

    hand = Hand.From_Strings(clist[0:4])
    starter = None
    sixth = None
    if len(clist) == 5:
        starter = Card.From_String(clist[4])
    if len(clist) == 6:
        # just return all 6 in the hand, no starter
        starter = None
        hand = Hand.From_Strings(clist)
    return (hand,starter)

def input_and_score_hand(cmdline):
    # repeatedly ask user for input, validating input, and computing the hand scores
    # exit cleanly if the user enters stop/quit
    stopping_conditions = ("STOP", "QUIT")
    while True:
        try:
            if cmdline == "":
                istring = input("Enter a cribbage hand: ").strip().upper()
                if istring in stopping_conditions:
                    sys.exit(0)
            else:
                istring = cmdline

            result = None
            hand,starter = parse_cribbage_hand(istring)

            if len(hand.cards) == 4:
                # just scoring
                result = "Score: {}".format(compute_hand_score(hand,starter))
            else:
                # 6 cards in the hand
                # need to figure out what cards to put into crib
                new_hand,crib_throw = determine_best_crib(hand)
                result = "Keep in hand: {}, throw to crib: {}".format(new_hand, crib_throw)

        except (ValueError) as err:
            # parsing errors will be these
            print(err)

        except (KeyboardInterrupt):
            # just exit
            sys.exit(0)
            
        except (Exception) as err:
            print("\nUnknown error.")
            print(err)
            print(err.args)
            sys.exit(0)

        if cmdline != "":
            return result
        else:
            if result: print(result)

        # print "I/O error({0}): {1}".format(e.errno, e.strerror)
        #except:
        #    print("Unexpected error:", sys.exc_info()[0])
        #    sys.exit(1)

def determine_best_crib(hand, own_crib=True):
    if len(hand.cards) != 6:
        raise ValueError("Expected a hand with 6 cards, got {}".format(len(hand.cards)))

    deck = Card.Deck()
    # try all combinations of 4
    # looking for hand with highest score
    best_hand = None
    best_high_score = 0
    best_low_score = 0
    best_starter_card = None
    best_distribution = None
    it_4_cards = itertools.combinations(hand.cards, 4)
    for four_card_hand in it_4_cards:
        this_hand = Hand(four_card_hand)
        this_hand_high = 0
        this_hand_low = None
        this_hand_scores = Counter()

        hand_set = set(four_card_hand)
        this_analyzer = CribbageHandAnalyzer(this_hand)
        for starter_card in deck.difference(hand_set):
            score = this_analyzer.score(starter_card)
            this_hand_scores[score] += 1
            if score > this_hand_high:
                this_hand_high = score
                this_starter_card = starter_card
            if this_hand_low and score < this_hand_low or not this_hand_low:
                this_hand_low = score

        if this_hand_high > best_high_score:
            best_hand = this_hand
            best_high_score = this_hand_high
            best_low_score = this_hand_low
            best_starter_card = this_starter_card
            best_distribution = this_hand_scores

    mean = sum(key * count for key, count in best_distribution.items()) / best_distribution.total()
    print("The best possible: {} / {} with high: {}, low: {}, and mean {:3.1f}.".format(best_hand, best_starter_card, best_high_score, best_low_score, mean))

    width = 80  # Adjust to desired width
    longest_key = max(len(str(key)) for key in best_distribution)
    graph_width = width - longest_key - 6
    widest = best_distribution.most_common(1)[0][1]
    scale = graph_width / float(widest)

    for key, size in sorted(best_distribution.items()):
        print('{:2}: ({:4.1f}%) {}'.format(key, (100.0*size/best_distribution.total()), int(size * scale) * '*'))

    crib = set(hand.cards).difference(set(best_hand.cards))
    return (best_hand, Hand(list(crib)))


def main():
    print(input_and_score_hand(" ".join(sys.argv[1:])))

if __name__ == "__main__":
    main()
    sys.exit(0)
