import sys

import numpy as np
import constants as c
import text_formatting as txf
import card_methods


class Player:
    def __init__(self, game, human=True, name=None):
        self.game = game
        self.human = human
        self.name = name
        self.hand = []
        self.discard_pile = []
        self.active_cards = []
        self.actions = 1
        self.buys = 1
        self.coins = 0

        self.deck = self.create_deck()
        self.shuffle_deck()
        self.cleanup()
        self.set_player_name(name)

    def set_player_name(self, name=None):
        if name:
            self.name = name
        else:
            self.name = "Player " + str(len(self.game.players))

    @staticmethod
    def create_deck():
        _deck = []
        for card_name in list(c.starting_deck.keys()):
            for _ in range(c.starting_deck[card_name]):
                _deck.append(Card(**c.card_list[card_name]))

        return _deck

    def play(self, display_hand=False):
        while self.actions > 0:
            if self.game.verbose and display_hand:
                print(self.name + "'s turn")
                self.print_hand()

            card_ix = -1
            if self.human:
                card_string = input("Select a card to play (1-" + str(len(self.hand)) + "), \"b\" to buy, \"e\" to "
                                    "end turn, or \"x\" to exit game:")
                try:
                    if card_string == "x":
                        sys.exit(0)
                    elif card_string == "e":
                        return
                    elif card_string == "b":
                        break
                    card_ix = int(card_string) - 1
                    assert 0 <= card_ix < len(self.hand)
                except:
                    print("Invalid card, please try again.")
                    continue

                if self.game.verbose:
                    self.confirm_card(card_ix)
            else:
                card_ix = np.random.randint(0, len(self.hand))

            self.play_card(card_ix)

        self.buy()

    def confirm_card(self, card_ix):
        confirmation = input("Play " + str(self.hand[card_ix].name + " (y/n)?"))
        if confirmation not in ["y", "n"]:
            print("Please type \"y\" or \"n\"")
            self.confirm_card(card_ix)
            return
        if confirmation == "n":
            print("Aborted")
            self.play()
            return

    def play_card(self, card_ix, use_action=True):
        card = self.hand[card_ix]
        self.active_cards.append(card)
        self.hand.remove(card)
        eval("card_methods." + card.name.lower() + "_card(self)")
        if use_action:
            self.actions -= 1

    def buy(self):
        treasure_cards = [c.copper, c.silver, c.gold]
        if self.game.platina:
            treasure_cards.append(c.platina)
        for card in self.hand:
            if card.name in treasure_cards:
                card.play(self, use_action=False)

        while self.buys > 0:
            if self.human:
                buy_or_view = input("Input \"b\" to buy a card, \"v\" to view a card from the supply, or \"e\" to end "
                                    "turn:")
                if buy_or_view not in ["b", "v", "e"]:
                    print("Please type \"b\", \"v\" or \"e\"")
                    continue
                if buy_or_view == "e":
                    return
                for card in self.game.supply:
                    print(card.name + ": " + str(self.game.supply.piles[card.name].number))
                card_string = input("Select a card (card name):")
                if card_string not in list(self.game.supply.piles.keys()):
                    print("Invalid card")
                    continue
                pile = self.game.supply.piles[card_string]
                if buy_or_view == "v":
                    print(Card(**c.card_list[pile.name]))
                    continue
                if pile.number > 0:
                    cost = c.card_list[pile.name][c.cost]
                    if self.coins >= cost:
                        self.gain(pile)
                        self.coins -= cost
                        self.buys -= 1
                    else:
                        print("You do not have enough coins")
                        continue
                else:
                    print("The " + pile.name + " pile is empty")
                    continue

    def shuffle_deck(self):
        for card in self.discard_pile:
            self.deck.append(card)
        self.discard_pile.clear()
        np.random.shuffle(self.deck)

    def cleanup(self):
        for card in self.hand:
            self.discard_pile.append(card)
        for card in self.active_cards:
            self.discard_pile.append(card)
        self.hand.clear()
        self.active_cards.clear()
        for _ in range(5):
            self.draw()

    def draw(self):
        if len(self.deck) <= 0:
            if len(self.discard_pile) <= 0:
                return
            else:
                self.shuffle_deck()

        self.hand.append(self.deck[-1])
        self.deck.pop()

    def gain(self, pile):
        if pile.number <= 0:
            return
        self.discard_pile.append(pile.cards[-1])
        pile.cards.pop()

    def trash(self, from_pile, card):
        assert card in from_pile
        self.game.trash.append(card)
        from_pile.remove(card)

    def discard(self, from_pile, card):
        assert card in from_pile
        self.discard_pile.append(card)
        from_pile.remove(card)

    def reveal(self, cards):
        print(self.name, "revealing")
        if type(cards) is Card:
            print(cards.name)
        elif type(cards) is list:
            for card in cards:
                print(card.name)

    def reveal_hand(self):
        self.reveal(self.hand)

    def print_hand(self):
        if self.game.verbose >= 2:
            for card in self.hand:
                print(card)
        else:
            for card in self.hand:
                print(card.name)


class Card:
    def __init__(self, name, set, types:list, cost, text, actions=None, villagers=None, cards=None,
                 buys=None, coins=None, coffers=None, trash=None, exile=None, junk=None, gain=None,
                 victory_points=None, **kwargs):
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

    def play(self, player:Player, use_action=True):
        player.active_cards.append(self)
        player.hand.remove(self)
        eval("card_methods." + self.name.lower() + "_card(player)")
        if use_action:
            player.actions -= 1

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
            _piles[pile] = Pile(len(self.game.players), pile)

        _kingdom_cards = {}
        for pile in list(_piles.keys()):
            _kingdom_cards[pile] = Pile(len(self.game.players), pile)

        while len(_kingdom_cards) < 10:
            new_pile = np.random.choice(list(c.card_list.keys()))
            if new_pile not in [p for p in list(_piles.keys()) + list(_kingdom_cards.keys())]:
                _kingdom_cards[new_pile] = Pile(len(self.game.players), new_pile)

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
    def __init__(self, num_players, card_name):
        self.num_players = num_players
        self.name = card_name
        self.cards = self.create_pile(card_name)

    def create_pile(self, card):
        _pile = []
        pile_size = c.card_list[card][c.pile_size]
        if type(pile_size) is list:
            self.number = pile_size[self.num_players - 2]
        else:
            self.number = pile_size

        for _ in range(self.number):
            _pile.append(Card(**c.card_list[card]))

        return _pile

    def add(self, card):
        self.cards.append(card)
        self.number += 1

    def remove(self):
        self.cards.pop()
        self.number -= 1


class Game:
    def __init__(self, players:int, supply=None, sets=None, platina=False, colonies=False, shelters=False, verbose=1):
        self.players = []
        self.players = [Player(self) for _ in range(players)]
        self.supply = Supply(self, supply, sets, platina, colonies, shelters)
        self.trash = []
        self.platina = platina
        self.colonies = colonies
        self.verbose = verbose
        self.turn = 0

    def gameloop(self):
        global game_over
        self.players[self.turn % len(self.players)].play(display_hand=True)
        game_over = self.end_conditions()

    def end_conditions(self):
        if self.supply.empty_piles() >= 3 or self.supply.provinces_empty():
            return True

        return False


game_over = False
num_players = 2

game = Game(num_players)
game.gameloop()

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
