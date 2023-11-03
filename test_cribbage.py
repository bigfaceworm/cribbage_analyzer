import pytest
from cribbage import Card, Hand, CribbageHandAnalyzer, compute_hand_score, parse_cribbage_hand, determine_best_crib, input_and_score_hand

def test_Card_bad_cards():
    with pytest.raises(ValueError) as v:
        Card.From_String('')
    with pytest.raises(ValueError) as v:
        Card.From_String('ZQ')
    with pytest.raises(ValueError) as v:
        Card.From_String('1SS')
    with pytest.raises(ValueError) as v:
        Card.From_String('TD')
    with pytest.raises(ValueError) as v:
        Card.From_String('13S')
    with pytest.raises(ValueError) as v:
        Card.From_String('1D0')
    with pytest.raises(ValueError) as v:
        Card.From_String('9w')
    
def test_Card_good_cards():
    AS = Card(1, 'S')
    assert(AS.rank == 1)
    assert(AS.suit == 'S')

    JC = Card(11, 'C')
    assert(JC.rank == 11)
    assert(JC.suit == 'C')

def test_Card_input_string():
    # Ace of Clubs
    AC = Card.From_String('ac')
    assert(AC.rank == 1)
    assert(AC.suit == 'C')

    CA = Card.From_String('ca')
    assert(AC == CA)

    onec = Card.From_String('1c')
    assert(onec == CA)

    cone = Card.From_String('c1')
    assert(cone == CA)

    # Kings
    KD = Card.From_String('kd')
    assert(KD.rank == 13)
    assert(KD.suit == 'D')

    DK = Card.From_String('DK')
    assert(KD == DK)

    KH = Card.From_String('KH')
    assert(KH.rank == DK.rank)

    # Numbers
    tenD = Card.From_String('10d')
    assert(tenD.rank == 10)
    assert(tenD.suit == 'D')

    dTen = Card.From_String('d10')
    assert(tenD == dTen)

    # Numbers
    fourS = Card.From_String('4S')
    assert(fourS.rank == 4)
    assert(fourS.suit == 'S')

    sFour = Card.From_String('s4')
    assert(fourS == sFour)

def test_Card_comparison():
    assert(Card.From_String('5D') == Card.From_String('D5'))
    assert(Card.From_String('5D') == Card.From_String('5D'))
    assert(Card.From_String('5D') < Card.From_String('6D'))
    assert(Card.From_String('5D') < Card.From_String('5H'))
    assert(Card.From_String('5D') < Card.From_String('5S'))
    assert(Card.From_String('5C') < Card.From_String('5D'))
    assert(Card.From_String('5S') < Card.From_String('6D'))

def test_Card_Deck():
    deck = Card.Deck()
    assert(Card.From_String('5C') in deck)
    assert(Card.From_String('6D') in deck)
    assert(Card.From_String('AS') in deck)
    assert(Card.From_String('JS') in deck)
    
def test_Hand_construction():
    cardList = [Card.From_String('2D'), Card.From_String('KS'), Card.From_String('JH'), Card.From_String('4C'), Card.From_String('5C'), Card.From_String('2S'), Card.From_String('9H')]

    # too many
    with pytest.raises(ValueError) as v:
        Hand(cardList)
    # too few
    with pytest.raises(ValueError) as v:
        Hand(cardList[0:1])
    with pytest.raises(ValueError) as v:
        Hand(cardList[0:0])

    # expects lists of 4 to 6
    Hand(cardList[0:4])
    Hand(cardList[1:5])
    Hand(cardList[1:6])
    Hand(cardList[1:7])

    # Hand does not allow duplicates
    with pytest.raises(ValueError) as v:
        Hand(cardList[0:4] + [cardList[3]])

def test_Hand_cards():
    cardList = [Card.From_String('4H'), Card.From_String('QD'), Card.From_String('S10'), Card.From_String('7H'), Card.From_String('5C'), Card.From_String('DA'), Card.From_String('6D')]

    # hand just stores sorted list of the cards
    four = cardList[0:4]
    h = Hand(four)
    four.sort()
    assert(h.cards == four)

    another_four = Hand.From_Strings(['7h', '4H', 'S10', 'QD'])
    assert(another_four.cards == four)

def test_CribbageHandAnalyzer_nothing():
    with pytest.raises(ValueError) as v:
        # too many cards
        five_cards_analyzer = CribbageHandAnalyzer(Hand.From_Strings(['S10', 'QD', '2D', 'AC', '5H']))
        five_cards_analyzer.score()

    nothingburger = CribbageHandAnalyzer(Hand.From_Strings(['4H', 'S10', 'QD', '2D']))
    assert(nothingburger.score() == 0)

def test_CribbageHandAnalyzer_flushes():
    three_spades = CribbageHandAnalyzer(Hand.From_Strings(['AH', 'QS', '3S', '6S']))
    assert(three_spades.score() == 0)
    assert(three_spades.score(Card.From_String('7S')) == 0)
    
    flush = CribbageHandAnalyzer(Hand.From_Strings(['AS', 'QS', '3S', '6S']))
    assert(flush.score() == 4)
    assert(flush.score(crib=False) == 4)
    assert(flush.score(Card.From_String('7S')) == 5)
    assert(flush.score(Card.From_String('7S'), crib=False) == 5)

    # crib flush
    assert(flush.score(crib=True) == 0)
    assert(flush.score(crib=True, starter=Card.From_String('7S')) == 5)
    assert(flush.score(crib=True, starter=Card.From_String('7D')) == 0)

def test_CribbageHandAnalyzer_pairs():
    # one pair
    one_pair = CribbageHandAnalyzer(Hand.From_Strings(['AS', '2C', '2D', '5H']))
    assert(one_pair.score() == 2)
    # still one pair
    assert(one_pair.score(Card.From_String('4C')))

    # two pairs
    assert(one_pair.score(Card.From_String('AC')) == 4)
    two_pair = CribbageHandAnalyzer(Hand.From_Strings(['5S', '2C', '2D', '5H']))
    assert(two_pair.score() == 4)
    # still just two pairs
    assert(two_pair.score(Card.From_String('7S')))

    # triplet
    assert(one_pair.score(Card.From_String('2S')) == 6)
    bare_triplet = CribbageHandAnalyzer(Hand.From_Strings(['3S', '3C', '3D', '5H']))
    assert(bare_triplet.score() == 6)
    # triplet and a pair
    assert(two_pair.score(Card.From_String('2S')) == 8)

    assert(bare_triplet.score(Card.From_String('2S')) == 6)
    assert(bare_triplet.score(Card.From_String('5S')) == 8)

    # a quad
    assert(bare_triplet.score(Card.From_String('3H')) == 12)
    the_quad = CribbageHandAnalyzer(Hand.From_Strings(['3S', '3C', '3D', '3H']))
    assert(the_quad.score() == 12)
    assert(the_quad.score(Card.From_String('8S')) == 12)

def test_CribbageHandAnalyzer_fifteens():
    # simple 15
    one_fifteen = CribbageHandAnalyzer(Hand.From_Strings(['8S', '7D', '3D', 'AH']))
    assert(one_fifteen.score() == 2)
    assert(one_fifteen.score(Card.From_String('KS')) == 2)

    # two 15
    two_fifteen = CribbageHandAnalyzer(Hand.From_Strings(['7S', '8D', '5D', 'KS']))
    assert(two_fifteen.score() == 4)
    assert(two_fifteen.score(Card.From_String('4S')) == 4)

    # three 15
    assert(one_fifteen.score(Card.From_String('4S')) == 6)

def test_CribbageHandAnalyzer_runs():
    # simple 3 card run
    run_of_3 = CribbageHandAnalyzer(Hand.From_Strings(['3S', '4D', '5D', 'AH']))
    assert(run_of_3.score() == 3)

    # simple 4 card run
    run_of_4 = CribbageHandAnalyzer(Hand.From_Strings(['2S', '3D', '4D', '5H']))
    assert(run_of_4.score() == 4)
    # another simple 4 card run
    another_run_of_4 = CribbageHandAnalyzer(Hand.From_Strings(['9S', '10D', 'JD', 'QH']))
    assert(another_run_of_4.score() == 4)

    # bump previous runs up with starter
    assert(another_run_of_4.score(Card.From_String('KH')) == 5)
    assert(another_run_of_4.score(Card.From_String('8H')) == 5)

def test_CribbageHandAnalyzer_nobs():
    # nobs
    nobs = CribbageHandAnalyzer(Hand.From_Strings(['8S', '10D', 'JD', '3S']))
    # no nobs if no starter
    assert(nobs.score() == 0)
    # yes nobs
    assert(nobs.score(Card.From_String('AD')) == 1)

    # inverter nobs, not a thing
    notnobs = CribbageHandAnalyzer(Hand.From_Strings(['8S', '10D', 'AD', '3S']))
    assert(notnobs.score() == 0)
    assert(notnobs.score(Card.From_String('JD')) == 0)
    
def test_CribbageHandAnalyzer_more_complex_hands():
    # double run
    double_run = CribbageHandAnalyzer(Hand.From_Strings(['9S', '10D', 'JD', '10S']))
    assert(double_run.score() == 8)
    assert(double_run.score(Card.From_String('10C')) == 15)

    # double long run
    assert(double_run.score(Card.From_String('8D')) == 11)

    # double run with 15s
    assert(double_run.score(Card.From_String('5C')) == 14)

    # 15s and pairs
    fifteens = CribbageHandAnalyzer(Hand.From_Strings(['7S', '8S', '7D', '3D']))
    assert(fifteens.score() == 6)
    assert(fifteens.score(Card.From_String('7C')) == 12)

    # 15s and pairs and runs
    mid_run = CribbageHandAnalyzer(Hand.From_Strings(['4C', '5C', '6S', '6H']))
    assert(mid_run.score() == 12)
    # double long run, with 15s
    assert(mid_run.score(Card.From_String('7D')) == 14)
    assert(mid_run.score(Card.From_String('3D')) == 16)
    # double double run, with 15s
    assert(mid_run.score(Card.From_String('4S')) == 24)

    # with a flush
    flush_and_stuff = CribbageHandAnalyzer(Hand.From_Strings(['3S', '4S', '5S', 'KS']))
    assert(flush_and_stuff.score() == 9)
    assert(flush_and_stuff.score(Card.From_String('6S')) == 13)
    assert(flush_and_stuff.score(Card.From_String('10S')) == 12)
    assert(flush_and_stuff.score(Card.From_String('10D')) == 11)

    assert(flush_and_stuff.score(crib=True) == 5)
    assert(flush_and_stuff.score(crib=True, starter=Card.From_String('6S')) == 13)

# need 3 tests, for three procs
def test_compute_hand_score():
    assert(compute_hand_score(Hand.From_Strings(['3S', '4S', '5S', 'KS'])) == 9)

def test_determine_best_crib():
    with pytest.raises(ValueError) as v:
        # not enough cards
        h,c = determine_best_crib(Hand.From_Strings(['3S', '4S', '5S', 'KS']))

    with pytest.raises(ValueError) as v:
        # not enough cards
        h,c = determine_best_crib(Hand.From_Strings(['3S', '4S', '5S', 'KS', 'QS']))

    # seems obvious that with 4 5's, and two cards that don't make anything
    # with the 5s, that those cards should be the crib.  so let's test that
    # and see where we get
    h,c = determine_best_crib(Hand.From_Strings(['5S', '5C', '5H', '5D', 'AS', '2C']))
    assert(Hand.From_Strings(['AS', '2C']) == c)
    assert(Hand.From_Strings(['5S', '5C', '5H', '5D']) == h)

    h,c = determine_best_crib(Hand.From_Strings(['3S', '4C', '5H', '8D', 'JS', 'QC']))
    assert(Hand.From_Strings(['JS', 'QC']) == c)
    assert(Hand.From_Strings(['3S', '4C', '5H', '8D']) == h)

    
def test_parse_cribbage_hand():
    # each of these should raise errors
    user_errors = ('too,few,cards',
                   'too,many,cards,as,input,here',
                   '7H, 8H, 9H, bad')
    for ue in user_errors:
        with pytest.raises(ValueError) as v:
            parse_cribbage_hand(ue)
        
    ahand = Hand.From_Strings(['3S', '5S', '4S', '6S'])
    bhand,astarter = parse_cribbage_hand('4S , 5S , 6S   3S')
    assert(ahand == bhand)
    assert(astarter == None)

    # input 5 cards, 5th is the starter
    dhand,dstarter = parse_cribbage_hand('4S , 5S , 6S   3S 9C')
    nine_clubs = Card.From_String('9C')
    assert(dhand == bhand)
    assert(dstarter == nine_clubs)

    # input 6 cards, all in the hand, starter is None
    shand,sstarter = parse_cribbage_hand('4S , 5S , 6S   3S 9C, JS')
    sixhand = Hand.From_Strings(['4S', '5S', '6S', '3S', '9C', 'JS'])
    assert(shand == sixhand)
    assert(sstarter == None)

def test_input_and_score_hand():
    assert(input_and_score_hand('5H 2C 3C 10S JS QS') == "Keep in hand: [5H, 10S, JS, QS], throw to crib: [2C, 3C]")
    assert(input_and_score_hand('5H 2C 3C 10S JS') == 'Score: 8')
    assert(input_and_score_hand('5H 2C 3C 10S') == 'Score: 4')
