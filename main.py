import numpy as np
import constants as c
import text_formatting as txf


class Player:
    def __init__(self, game, name=None):
        self.game = game
        self.name = name
        self.hand = []
        self.discard_pile = []
        self.active_cards = []

        self.deck = self.create_deck()
        self.set_player_name(name)

    def set_player_name(self, name=None):
        if name:
            self.name = name
        else:
            self.name = "Player " + str(len(self.game.players))

    def create_deck(self):
        _deck = []
        for card_name in list(c.starting_deck.keys()):
            for _ in range(c.starting_deck[card_name]):
                _deck.append(Card(**c.card_list[card_name]))

        return _deck

    def play(self):
        pass

    def shuffle_deck(self):
        pass

    def draw(self):
        pass

    def gain(self, card):
        pass

    def trash(self, card):
        pass

    def discard(self, card):
        pass

    def play_card(self, card):
        pass

    def reveal(self, card):
        pass

    def reveal_hand(self):
        pass


class Card:
    def __init__(self, name, set, types:list, cost, text, actions=None, villagers=None, cards=None,
                 buys=None, coins=None, coffers=None, trash=None, exile=None, junk=None, gain=None,
                 victory_points=None, **kargs):
        self.name = name
        self.set = set
        self.types = types
        self.cost = cost
        self.text = text
        # self.actions = actions
        # self.villagers = villagers
        # self.cards = cards
        # self.buys = buys
        # self.coins = coins
        # self.coffers = coffers
        # self.trash = trash
        # self.exile = exile
        # self.junk = junk
        # self.gain = gain
        # self.victory_points = victory_points

    def resolve(self):
        pass

    def __str__(self):
        output = " " + "_" * (txf.card_width - 2) + " \n"
        output += "|" + " " * (txf.card_width - 2) + "|\n"
        output += txf.center(txf.title(self.name))
        output += "|" + "_" * (txf.card_width - 2) + "|\n"
        output += "|" + " " * (txf.card_width - 2) + "|\n"
        output += txf.center(self.text)
        output += "|" + " " * (txf.card_width - 2) + "|\n"
        output += "|" + "_" * (txf.card_width - 2) + "|\n"
        types_string = ""
        for t in self.types:
            types_string += txf.italic(t) + " - "

        output += txf.center(types_string[:-3])
        cost_string_left = "|" + txf.coins(self.cost, plain=True)
        cost_string_right = " " * (txf.card_width - (txf.formatted_str_len(cost_string_left) + 3)) + "|\n"
        output += cost_string_left + cost_string_right
        output += "|" + "_" * (txf.card_width - 2) + "|\n"
        return output


class Supply:
    def __init__(self, game, supply=None, sets=None, platina=False, colonies=False, shelters=False):
        self.game = game
        if supply is None:
            supply = []

        self.piles = self.setup_piles(supply, sets, platina, colonies, shelters)

    def setup_piles(self, supply, sets, platina, colonies, shelters):
        _piles = {}
        for pile in c.initial_supplies:
            _piles[pile] = Pile(self.game, pile)

        _kingdom_cards = {}
        for pile in list(_piles.keys()):
            _kingdom_cards[pile] = Pile(self.game, pile)

        while len(_kingdom_cards) < 10:
            new_pile = np.random.choice(list(c.card_list.keys()))
            if new_pile not in [p for p in list(_piles.keys()) + list(_kingdom_cards.keys())]:
                _kingdom_cards[new_pile] = Pile(self.game, new_pile)

        return {**_piles, **_kingdom_cards}

    def empty_piles(self):
        _empty_piles = 0
        for p in self.piles:
            if self.piles[p].number == 0:
                _empty_piles += 1

        return _empty_piles

    def provinces_empty(self):
        if self.piles[c.province].number == 0:
            return True

        return False


class Pile:
    def __init__(self, game, card_name):
        self.game = game
        self.name = card_name
        self.cards = self.create_pile(card_name)

    def create_pile(self, card):
        _pile = []
        pile_size = c.card_list[card][c.pile_size]
        if type(pile_size) is list:
            self.number = pile_size[len(self.game.players) - 2]
        else:
            self.number = pile_size

        for _ in range(self.number):
            _pile.append(Card(**c.card_list[card]))

        return _pile

    def add(self, card):
        self.cards.append(card)

    def remove(self):
        self.cards.pop()
        self.number -= 1


class Game:
    def __init__(self, players:int, supply=None, sets=None, platina=False, colonies=False, shelters=False):
        self.players = []
        self.players = [Player(self) for _ in range(players)]
        self.supply = Supply(self, supply, sets, platina, colonies, shelters)
        self.trash = []
        self.colonies = colonies
        self.turn = 0

    def gameloop(self):
        global game_over
        self.players[self.turn % len(self.players)].play()
        game_over = self.end_conditions()

    def end_conditions(self):
        if self.supply.empty_piles() >= 3 or self.supply.provinces_empty():
            return True

        return False


game_over = False
num_players = 2

game = Game(num_players)

# for card in list(c.card_list.keys()):
#     print(Card(**c.card_list[card]))

# while not game_over:
#     game.gameloop()

# card_list = {
#     c.cellar: {c.name: c.cellar, c.set: c.base, c.types: [c.action], c.cost: 2, c.text: c.card_text[c.cellar],
#                c.actions: 1, c.cards: c.var},
#     c.chapel: {c.name: c.chapel, c.set: c.base, c.types: [c.action], c.cost: 2, c.text: c.card_text[c.chapel],
#                c.trash: 4},
#     c.moat: {c.name: c.moat, c.set: c.base, c.types: [c.action, c.reaction], c.cost: 2, c.text: c.card_text[c.moat],
#              c.cards: 2},
#     c.chancellor: {c.name: c.chancellor, c.set: c.base_1e, c.types: [c.action], c.cost: 3,
#                    c.text: c.card_text[c.chancellor], c.coins: 2},
#     c.harbinger: {c.name: c.harbinger, c.set: c.base_2e, c.types: [c.action], c.cost: 3,
#                   c.text: c.card_text[c.harbinger], c.actions: 1, c.cards: 1},
#     c.merchant: {c.name: c.merchant, c.set: c.base_2e, c.types: [c.action], c.cost: 3, c.text: c.card_text[c.merchant],
#                  c.actions: 1, c.cards: 1, c.coins: c.var},
#     c.vassal: {c.name: c.vassal, c.set: c.base_2e, c.types: [c.action], c.cost: 3, c.text: c.card_text[c.vassal],
#                c.coins: 2},
#     c.village: {c.name: c.village, c.set: c.base, c.types: [c.action], c.cost: 3, c.text: c.card_text[c.village],
#                 c.actions: 2, c.cards: 1},
#     c.woodcutter: {c.name: c.woodcutter, c.set: c.base_1e, c.types: [c.action], c.cost: 3,
#                    c.text: c.card_text[c.woodcutter], c.buys: 1, c.coins: 2},
#     c.workshop: {c.name: c.workshop, c.set: c.base, c.types: [c.action], c.cost: 3, c.text: c.card_text[c.workshop],
#                  c.gain: 1}
# }
