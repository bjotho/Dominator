import sys

import numpy as np
import constants as c
import text_formatting as txf
import card_methods


class Player:
    def __init__(self, game, human=True, name=None, shelters=False):
        self.game = game
        self.human = human
        self.name = name
        self.hand = []
        self.discard_pile = []
        self.active_cards = []
        self.effects = []
        self.actions = 1
        self.buys = 1
        self.coins = 0
        self.victory_points = 0

        self.deck = self.create_deck(shelters)
        self.shuffle_deck()
        self.cleanup()
        self.set_player_name(name)

    def set_player_name(self, name=None):
        if name:
            self.name = name
        else:
            self.name = "Player " + str(len(self.game.players) + 1)

    @staticmethod
    def create_deck(shelters):
        _deck = []
        for card_name in list(c.starting_deck.keys()):
            for _ in range(c.starting_deck[card_name]):
                _deck.append(Card(**c.card_list[card_name]))

        return _deck

    def play(self):
        if self.game.verbose:
            print(self.name + "'s turn:")
            print("Deck: " + str(len(self.deck)) + ",\tDiscard Pile: " + str(len(self.discard_pile)))
            self.print_hand()

        while self.actions > 0:
            if self.human:
                if self.game.verbose and len(self.active_cards) > 0:
                    self.print_active_cards()
                card_string = input("Select an action card to play (card name), \"b\" to initiate buying phase, \"h\" "
                                    "to view hand, \"e\" to end turn, or \"x\" to exit game:")
                if card_string == "x":
                    sys.exit(0)
                elif card_string == "e":
                    return
                elif card_string == "b":
                    break
                elif card_string == "h":
                    self.print_hand()
                    continue
                elif card_string == "bb":
                    self.buy(direct_buy=True)
                    return
                elif card_string == "hh":
                    v_tmp = self.game.verbose
                    self.game.verbose = 2
                    self.print_hand()
                    self.game.verbose = v_tmp
                    continue
                try:
                    card_string = card_string[0].upper() + card_string[1:].lower()
                    i = 0
                    while card_string != self.hand[i].name:
                        i += 1

                    assert c.action in self.hand[i].types
                    card_ix = i
                except:
                    print("Invalid input, please try again.")
                    continue

                if self.game.verbose:
                    if not card_methods.confirm_card("Play " + str(self.hand[card_ix].name + " (y/n)?")):
                        continue

                self.hand[card_ix].play(self)
            else:
                action_cards = [card for card in self.hand if c.action in card.types]
                if len(action_cards) == 0:
                    break
                else:
                    card = np.random.choice(action_cards)
                    if self.game.verbose:
                        print(self.name + " plays " + card.name)
                    card.play(self)

        self.buy()

    def buy(self, direct_buy=False):
        if self.game.verbose:
            print("Buying phase")
        treasure_cards = [c.copper, c.silver, c.gold]
        if self.game.platina:
            treasure_cards.append(c.platina)
        hand_treasures = [card for card in self.hand if c.treasure in card.types]
        while any(card.name not in treasure_cards for card in hand_treasures):
            if self.human:
                card_string = input("Select a treasure card to play (card name), \"e\" to end turn, \"b\" to buy, or "
                                    "\"h\" to view hand:")
                if card_string == "x":
                    sys.exit(0)
                elif card_string == "e":
                    return
                elif card_string == "b":
                    break
                elif card_string == "h":
                    self.print_hand()
                    continue
                elif card_string == "hh":
                    v_tmp = self.game.verbose
                    self.game.verbose = 2
                    self.print_hand()
                    self.game.verbose = v_tmp
                    continue
                try:
                    card_string = card_string[0].upper() + card_string[1:].lower()
                    i = 0
                    while card_string != self.hand[i].name:
                        i += 1

                    assert c.treasure in self.hand[i].types
                    card_ix = i
                except:
                    print("Invalid input, please try again.")
                    continue

                if self.game.verbose:
                    if not card_methods.confirm_card("Play " + str(self.hand[card_ix].name + " (y/n)?")):
                        continue

                self.hand[card_ix].play(self, action=False)
                hand_treasures.remove(self.hand[card_ix])

            else:
                playable_hand_treasures = [card for card in hand_treasures if card not in treasure_cards]
                card = np.random.choice(playable_hand_treasures)
                if self.game.verbose:
                    print(self.name + " plays " + card.name)
                card.play(self, action=False)
                hand_treasures.remove(card)

        for t_card in hand_treasures:
            t_card.play(self, action=False)

        while self.buys > 0:
            if self.human:
                if self.game.verbose:
                    print("Coins: " + txf.coins(self.coins, plain=True) + "\tBuys: " + str(self.buys))
                    if len(self.active_cards) > 0:
                        self.print_active_cards()
                if direct_buy:
                    buy_or_view = "b"
                    direct_buy = False
                else:
                    buy_or_view = input("Input \"b\" to buy a card, \"v\" to view a card from the supply, \"h\" to "
                                        "view hand, or \"e\" to end turn:")
                if buy_or_view not in ["b", "v", "vv", "h", "hh", "e"]:
                    print("Please type \"b\", \"v\", \"h\" or \"e\"")
                    continue
                if buy_or_view == "e":
                    return
                elif buy_or_view == "h":
                    self.print_hand()
                    continue
                elif buy_or_view == "vv":
                    v_tmp = self.game.verbose
                    self.game.verbose = 2
                    print(self.game.supply)
                    self.game.verbose = v_tmp
                    continue
                elif buy_or_view == "hh":
                    v_tmp = self.game.verbose
                    self.game.verbose = 2
                    self.print_hand()
                    self.game.verbose = v_tmp
                    continue
                print(self.game.supply)
                card_string = input("Select a card (card name):")
                if len(card_string) == 0:
                    print("Invalid card")
                    continue
                card_string = card_string[0].upper() + card_string[1:].lower()
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
                        if self.game.verbose:
                            print(self.name + " buys " + pile.name)
                        self.gain(pile, mute=True)
                        self.coins -= cost
                        self.buys -= 1
                    else:
                        print("You do not have enough coins")
                        continue
                else:
                    print("The " + pile.name + " pile is empty")
                    continue
            else:
                affordable_cards = [pile for pile in list(self.game.supply.piles.keys())
                                    if self.coins >= c.card_list[pile][c.cost]]
                pile = self.game.supply.piles[np.random.choice(affordable_cards)]
                if self.game.verbose:
                    print(self.name + " buys " + pile.name)
                self.gain(pile, mute=True)
                self.coins -= c.card_list[pile.name][c.cost]
                self.buys -= 1

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
        self.effects.clear()
        self.actions = 1
        self.buys = 1
        self.coins = 0
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

    def gain(self, pile, mute=False):
        if pile.number <= 0:
            return

        if self.game.verbose and not mute:
            print(self.name + " gains " + pile.name)
        self.discard_pile.append(pile.cards[-1])
        pile.remove()

    def trash(self, from_pile, card):
        assert card in from_pile
        if self.game.verbose:
            print(self.name + " trashes " + card.name)
        self.game.trash.append(card)
        from_pile.remove(card)

    def discard(self, from_pile, card):
        assert card in from_pile
        self.discard_pile.append(card)
        from_pile.remove(card)

    def reveal(self, cards):
        print(self.name + " reveals:")
        if type(cards) is Card:
            print("  " + cards.name)
        elif type(cards) is list:
            for card in cards:
                print("  " + card.name)

    def reveal_hand(self):
        self.reveal(self.hand)

    def all_cards(self):
        return self.deck + self.hand + self.active_cards + self.discard_pile

    def print_hand(self):
        print(self.name + "\'s hand:")
        if self.game.verbose >= 2:
            for card in self.hand:
                print(card)
        else:
            for card in self.hand:
                if c.action in card.types:
                    print("  " + txf.action(card.name))
                elif c.treasure in card.types:
                    print("  " + txf.treasure(card.name))
                elif c.victory in card.types:
                    print("  " + txf.victory(card.name))
                else:
                    print("  " + card.name)

    def print_active_cards(self):
        print("Cards played this turn:")
        for card in self.active_cards:
            if self.game.verbose >= 2:
                print(card)
            else:
                print(card.name + "\t", end="")

        if self.game.verbose < 2:
            print("")

    def print_discard_pile(self):
        print(self.name + " discard pile:")
        if self.game.verbose >= 2:
            for card in self.discard_pile:
                print(card)
        else:
            for card in self.discard_pile:
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

    def play(self, player:Player, action=True, discard=True):
        tmp_deck = player.deck.copy()
        tmp_hand = player.hand.copy()
        tmp_active_cards = player.active_cards.copy()
        tmp_discard_pile = player.discard_pile.copy()
        tmp_actions = player.actions
        tmp_buys = player.buys
        tmp_coins = player.coins
        player.active_cards.append(self)
        if discard:
            player.hand.remove(self)
        success = eval("card_methods." + self.name.lower() + "_card(player)")
        if not success:
            player.deck = tmp_deck
            player.hand = tmp_hand
            player.active_cards = tmp_active_cards
            player.discard_pile = tmp_discard_pile
            player.actions = tmp_actions
            player.buys = tmp_buys
            player.coins = tmp_coins
            return
        if action:
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
    def __init__(self, game, supply=None, sets=None):
        self.game = game
        if supply is None:
            supply = []

        self.piles = self.setup_piles(supply, sets)

    def setup_piles(self, supply:list, sets):
        _piles = {}
        for pile in c.initial_treasures:
            _piles[pile] = Pile(len(self.game.players), pile)
        if self.game.platina:
            _piles[c.platina] = Pile(len(self.game.players), c.platina)
        for pile in c.initial_victory_cards:
            _piles[pile] = Pile(len(self.game.players), pile)
        if self.game.colonies:
            _piles[c.colony] = Pile(len(self.game.players), c.colony)
        _piles[c.curse] = Pile(len(self.game.players), c.curse)

        if sets:
            if c.base in sets:
                if c.base_1e not in sets:
                    sets.append(c.base_1e)
                if c.base_2e not in sets:
                    sets.append(c.base_2e)
            elif (c.base_1e in sets or c.base_2e in sets) and len(sets) == 1:
                sets.append(c.base)

        _kingdom_cards = {}
        assert 0 <= len(supply) <= 10
        for pile in supply:
            if pile not in list(c.card_list.keys()):
                if self.game.verbose:
                    print("Could not find card \"" + str(pile) + "\"")
                continue
            if pile not in [p for p in list(_piles.keys()) + list(_kingdom_cards.keys())]:
                _kingdom_cards[pile] = Pile(len(self.game.players), pile)

        while len(_kingdom_cards) < 10:
            new_pile = np.random.choice(list(c.card_list.keys()))
            if new_pile == c.platina or new_pile == c.colony:
                continue
            if new_pile not in [p for p in list(_piles.keys()) + list(_kingdom_cards.keys())]:
                if sets:
                    if c.card_list[new_pile][c.set] not in sets:
                        continue
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

    def colonies_empty(self):
        if self.piles[c.colony].number == 0:
            return True

        return False

    def __str__(self):
        output = "Supply:\n"
        if self.game.verbose >= 2:
            for pile in self.piles.items():
                output += pile[1].__str__() + "\n"
        else:
            for pile in list(self.piles.items()):
                output +=  "  " + pile[0] + ": " + pile[1].get_color() + str(pile[1].number) + txf.END + "\n"

        return output


class Pile:
    def __init__(self, num_players, card_name):
        self.num_players = num_players
        self.name = card_name
        self.cards = self.create_pile(card_name)
        self.color = txf.GREEN

    def create_pile(self, card):
        _pile = []
        pile_size = c.card_list[card][c.pile_size]
        if type(pile_size) is list:
            try:
                self.number = pile_size[self.num_players - 2]
            except IndexError:
                self.number = pile_size[-1]
        else:
            self.number = pile_size

        self.max_number = self.number

        for _ in range(self.number):
            _pile.append(Card(**c.card_list[card]))

        return _pile

    def add(self, card):
        self.cards.append(card)
        self.number += 1

    def remove(self):
        self.cards.pop()
        self.number -= 1

    def get_color(self):
        if self.number <= 0:
            return txf.DARK_RED

        frac = float(self.number / self.max_number)
        if frac > 0.5:
            return txf.GREEN
        elif 0.2 < frac <= 0.5:
            return txf.YELLOW
        else:
            return txf.RED

    def __str__(self):
        output = "Size: " + self.get_color() + str(self.number) + txf.END + "\n"
        return output + Card(**c.card_list[self.name]).__str__()


class Game:
    def __init__(self, players:int, supply=None, sets=None, platina=False, colonies=False, shelters=False, verbose=1):
        self.platina = platina
        self.colonies = colonies
        self.verbose = verbose
        self.trash = []
        self.turn = 0
        self.players = [Player(self, name="Player " + str(i + 1), shelters=shelters) for i in range(players)]
        self.players[0].set_player_name("Bjorni")
        self.players[-1].human = False
        self.supply = Supply(self, supply, sets)

        if self.verbose:
            print(self.supply)

    def gameloop(self):
        global game_over
        if self.verbose:
            print("\nTurn " + str(self.turn + 1) + "\n")
        player = self.players[self.turn % len(self.players)]
        player.play()
        player.cleanup()
        game_over = self.end_conditions()
        self.turn += 1

    def end_conditions(self):
        if self.colonies:
            if self.supply.colonies_empty():
                return True
        if self.supply.empty_piles() >= 3 or self.supply.provinces_empty():
            return True

        return False

    def score(self):
        print("Results:")
        for player in self.players:
            for card in player.all_cards():
                if c.victory in card.types:
                    card.play(player, action=False, discard=False)

        self.players.sort(key=lambda p: p.victory_points, reverse=True)
        for i in range(len(self.players)):
            print("#" + str(i + 1) + ": " + self.players[i].name + " with " + str(self.players[i].victory_points) + " VP")

        print("\n~~~Congratulations, " + self.players[0].name + "!~~~")


game_over = False
num_players = 2

game = Game(players=num_players, supply=[c.moat, c.chancellor], platina=True, colonies=True, verbose=1)
while not game_over:
    game.gameloop()

game.score()

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
