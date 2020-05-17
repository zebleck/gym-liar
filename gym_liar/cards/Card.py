import logging
logger = logging.getLogger(__name__)

class Card:

    rankDict = {
            1: 'Ace',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
            11: 'Jack',
            12: 'Queen',
            13: 'King'
        }

    # ranks: 1(A),2,3,4,5,6,7,8,9,10,11(J),12(Q),13(K)
    # suits: C, D, H, S

    def __init__(self, rank, suit):
        assert rank in range(1, 14)
        assert suit in ['Clubs', 'Diamonds', 'Hearts', 'Spades']            
        
        self.rank = rank
        self.suit = suit

    def  __str__(self):
        return Card.rankDict[self.rank] + ' of ' + self.suit
