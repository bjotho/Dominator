import sys

import numpy as np
import constants as c
import text_formatting as txf
import card_methods
import card_reactions


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
            print(self.name + "\'s turn:")
            if not self.human:
                self.print_hand()
                print("")

        while self.actions > 0:
            if self.human:
                if self.game.verbose:
                    print("Deck: " + str(len(self.deck)) + ",\tDiscard Pile: " + str(len(self.discard_pile)))
                    self.print_hand()
                    print("")
                    print("Actions: " + str(self.actions))
                    print("Buys: " + str(self.buys))
                    if len(self.active_cards) > 0:
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
                    if not card_methods.confirm_card("Play " + self.hand[card_ix].colored_name() + " (y/n)?"):
                        continue

                self.hand[card_ix].play(self)
            else:
                action_cards = [card for card in self.hand if c.action in card.types]
                if len(action_cards) == 0:
                    break
                else:
                    card = np.random.choice(action_cards)
                    if self.game.verbose:
                        print(self.name + " plays " + card.colored_name())
                    card.play(self)

        self.buy()

    def buy(self, direct_buy=False):
        if self.game.verbose:
            print("---Buying phase---")
        treasure_cards = [c.copper, c.silver, c.gold]
        if self.game.platina:
            treasure_cards.append(c.platina)
        hand_treasures = [card for card in self.hand if c.treasure in card.types]
        while any(card.name not in treasure_cards for card in hand_treasures):
            if self.human:
                if self.game.verbose:
                    print("Deck: " + str(len(self.deck)) + ",\tDiscard Pile: " + str(len(self.discard_pile)))
                    self.print_hand()
                    print("")
                    print("Coins: " + txf.coins(self.coins, plain=True) + "\tBuys: " + str(self.buys))
                    if len(self.active_cards) > 0:
                        self.print_active_cards()
                card_string = input("Select a treasure card to play (card name), \"e\" to end turn, \"b\" to buy, or "
                                    "\"h\" to view hand:")
                if card_string == "x":
                    sys.exit(0)
                elif card_string == "e":
                    return
                elif card_string == "b":
                    break
                elif card_string == "h":
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
                    if not card_methods.confirm_card("Play " + self.hand[card_ix].colored_name() + " (y/n)?"):
                        continue

                self.hand[card_ix].play(self, action=False)
                hand_treasures.remove(self.hand[card_ix])

            else:
                playable_hand_treasures = [card for card in hand_treasures if card not in treasure_cards]
                card = np.random.choice(playable_hand_treasures)
                if self.game.verbose:
                    print(self.name + " plays " + card.colored_name())
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
                            print(self.name + " buys " + pile.colored_name())
                        self.gain(pile, mute=True)
                        self.coins -= cost
                        self.buys -= 1
                    else:
                        print("You do not have enough coins")
                        continue
                else:
                    print("The " + pile.colored_name() + " pile is empty")
                    continue
            else:
                affordable_cards = [pile for pile in list(self.game.supply.piles.values())
                                    if self.coins >= pile.cost and pile.number > 0]
                pile = self.game.supply.piles[np.random.choice(affordable_cards).name]
                if self.game.verbose:
                    print(self.name + " buys " + pile.cards[-1].colored_name())
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
            self.draw(mute=True)

    def draw(self, mute=False, named=True, return_card=False):
        if len(self.deck) <= 0:
            if len(self.discard_pile) <= 0:
                return
            else:
                self.shuffle_deck()

        if not mute and self.game.verbose:
            if named:
                print(self.name + " draws " + self.deck[-1].colored_name())
            else:
                print(self.name + " draws a card")
        card = self.deck[-1]
        self.hand.append(card)
        self.deck.pop()

        if return_card:
            return card

    def gain(self, pile, to_pile=None, mute=False):
        if pile.number <= 0:
            return

        if to_pile is None:
            to_pile = self.discard_pile

        if self.game.verbose and not mute:
            print(self.name + " gains " + pile.colored_name())
        to_pile.append(pile.cards[-1])
        pile.remove()

    def trash(self, from_pile, card):
        try:
            assert card in from_pile
            if self.game.verbose:
                print(self.name + " trashes " + card.colored_name())
            self.game.trash.append(card)
            from_pile.remove(card)
        except:
            if self.game.verbose:
                print(card.name + " is not in expected location and was not trashed")

    def discard(self, from_pile, card):
        assert card in from_pile
        self.discard_pile.append(card)
        from_pile.remove(card)

    def reveal(self, cards):
        if self.game.verbose:
            print(self.name + " reveals:")
            if type(cards) is Card:
                print("  " + cards.colored_name())
            elif type(cards) is list:
                for card in cards:
                    print("  " + card.colored_name())

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
                if c.reaction in card.types:
                    print("  " + txf.reaction(card.name))
                elif c.action in card.types:
                    print("  " + txf.action(card.name))
                elif c.treasure in card.types:
                    print("  " + txf.treasure(card.name))
                elif c.victory in card.types:
                    print("  " + txf.victory(card.name))
                elif c.curse in card.types:
                    print("  " + txf.curse_card(card.name))
                else:
                    print("  " + card.name)

    def print_active_cards(self):
        print("Cards played this turn:")
        for card in self.active_cards:
            if self.game.verbose >= 2:
                print(card)
            else:
                print(card.colored_name() + "\t", end="")

        if self.game.verbose < 2:
            print("")

    def print_discard_pile(self):
        print(self.name + "\'s discard pile:")
        if self.game.verbose >= 2:
            for card in self.discard_pile:
                print(card)
        else:
            for card in self.discard_pile:
                print(card.colored_name())


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

        self.color = self.get_color()

    def play(self, player:Player, action=True, discard=True):
        tmp_deck = player.deck.copy()
        tmp_hand = player.hand.copy()
        tmp_active_cards = player.active_cards.copy()
        tmp_discard_pile = player.discard_pile.copy()
        tmp_actions = player.actions
        tmp_buys = player.buys
        tmp_coins = player.coins
        tmp_player_effects = {}
        for p in player.game.players:
            tmp_player_effects[p.name] = p.effects

        if c.attack in self.types:
            _players = [p for p in player.game.players if p is not player]
            for p in _players:
                for card in p.hand:
                    if c.reaction in card.types:
                        if c.reaction_triggers[card.name] == c.attack:
                            if p.human:
                                if card_methods.confirm_card("Will " + p.name + " reveal " + card.colored_name()
                                                             + " reaction card (y/n)?"):
                                    eval("card_reactions." + card.name.lower() + "_reaction(p, card)")
                            else:
                                if np.random.random() > 0:
                                    eval("card_reactions." + card.name.lower() + "_reaction(p, card)")

        if discard:
            player.active_cards.append(self)
            player.hand.remove(self)
        success = eval("card_methods." + self.name.lower() + "_card(player)")
        for p in player.game.players:
            p.effects = tmp_player_effects[p.name]
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

    def get_color(self):
        if c.reaction in self.types:
            return txf.BRIGHT_BLUE_BG
        elif c.action in self.types:
            return txf.WHITE_BG
        elif c.treasure in self.types:
            return txf.BRIGHT_YELLOW_BG
        elif c.victory in self.types:
            return txf.BRIGHT_GREEN_BG
        elif c.curse in self.types:
            return txf.BRIGHT_MAGENTA_BG
        else:
            return ""

    def colored_name(self):
        return self.color + " " + self.name + " " + txf.END

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
        self.spacing = self.spacing()

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

    def spacing(self):
        return max([txf.visible_str_len(txf.bold("1234") + pile.colored_name() + ":") for pile in list(self.piles.values())])

    def __str__(self):
        output = "Supply:\n"
        if self.game.verbose >= 2:
            for pile in self.piles.items():
                output += pile[1].__str__() + "\n"
        else:
            for pile in list(self.piles.values()):
                line = txf.bold(str(pile.cost))
                while txf.visible_str_len(line) < 4:
                    line += " "
                line += pile.colored_name() + ":"
                while txf.visible_str_len(line) < self.spacing:
                    line += " "
                output += line + "  " + pile.get_color() + str(pile.number) + txf.END + "\n"

        return output


class Pile:
    def __init__(self, num_players, card_name):
        self.num_players = num_players
        self.name = card_name
        self.cards = self.create_pile(card_name)

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

        tmp_card = Card(**c.card_list[card])
        self.set = tmp_card.set
        self.types = tmp_card.types
        self.cost = tmp_card.cost

        return _pile

    def add(self, card):
        self.cards.append(card)
        self.number += 1

    def remove(self):
        self.cards.pop()
        self.number -= 1

    def colored_name(self):
        tmp_card = Card(**c.card_list[self.name])
        return tmp_card.colored_name()

    def get_color(self):
        if self.number <= 2:
            return txf.RED

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
        print("\n---Results---")
        for player in self.players:
            for card in player.all_cards():
                if c.victory in card.types or c.curse in card.types:
                    card.play(player, action=False, discard=False)

        self.players.sort(key=lambda p: p.victory_points, reverse=True)
        for i in range(len(self.players)):
            print("#" + str(i + 1) + ": " + self.players[i].name + " with "
                  + str(self.players[i].victory_points) + " VP")

        print("\n~~~Congratulations, " + self.players[0].name + "!~~~")

    def print_decks(self):
        print("\nPlayer decks:")
        for p in self.players:
            print("\n" + p.name + "\'s deck (" + str(len(p.all_cards())) + " cards):")
            breakdown = self.deck_breakdown(p.all_cards())
            for pair in list(breakdown.items()):
                card = Card(**c.card_list[pair[0]])
                print(txf.bold(str(pair[1]) + "x") + "\t" + card.colored_name())

    @staticmethod
    def deck_breakdown(deck:list):
        breakdown = {}
        for card in deck:
            if card.name not in list(breakdown.keys()):
                breakdown[card.name] = 1
            else:
                breakdown[card.name] += 1

        return breakdown


game_over = False
num_players = 2
supply_cards = [c.moat, c.village, c.woodcutter, c.vassal, c.merchant, c.bureaucrat, c.gardens, c.militia,
                c.moneylender, c.poacher]

game = Game(players=num_players, supply=supply_cards, platina=False, colonies=False, verbose=1)
while not game_over:
    game.gameloop()

game.score()
if card_methods.confirm_card("Show final decks (y/n)?"):
    game.print_decks()
