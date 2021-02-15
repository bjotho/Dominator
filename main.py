import sys

import numpy as np
import constants as c
import text_formatting as txf
import card_methods
import card_reactions
import card_costs


class Player:
    def __init__(self, game, human=True, name=None, shelters=False):
        self.game = game
        self.human = human
        self.name = name
        self.hand = []
        self.discard_pile = []
        self.active_cards = []
        self.revealed_cards = []
        self.set_aside_cards = []
        self.effects = {}
        self.actions = 1
        self.buys = 1
        self.coins = 0
        self.victory_points = 0
        self.victory_tokens = 0
        self.autoplay_treasures = True

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

    def toggle_autoplay_treasures(self):
        if self.game.verbose:
            message = "Autoplay treasures is currently turned "
            if self.autoplay_treasures:
                message += "ON, turn OFF? (y/n):"
            else:
                message += "OFF, turn ON? (y/n):"
            if not card_methods.confirm_card(message, mute_n=True):
                return

        self.autoplay_treasures = not self.autoplay_treasures

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
                    if self.game.use_victory_tokens:
                        print(txf.vt(self.victory_tokens, plain=True))
                    if len(self.active_cards) > 0:
                        self.print_active_cards()
                card_str = input("Select an action card to play (card name):")
                if card_str == "help":
                    print(txf.help_message)
                    continue
                elif card_str == "x":
                    if card_methods.confirm_card("Exit game (y/n)?"):
                        self.game.game_over = True
                        return
                    continue
                elif card_str == "e":
                    return
                elif card_str == "b":
                    break
                elif card_str == "a":
                    self.toggle_autoplay_treasures()
                    continue
                elif card_str == "fx":
                    self.print_active_effects()
                    continue
                elif card_str == "h":
                    if not self.game.verbose:
                        self.print_hand()
                    continue
                elif card_str == "hh":
                    v_tmp = self.game.verbose
                    self.game.verbose = 2
                    self.print_hand()
                    self.game.verbose = v_tmp
                    continue
                elif card_str == "v":
                    card_str = input("Select card to view (card name):")
                    piles = [Card(**c.card_list[pile.name]) for pile in list(self.game.supply.piles.values())]
                    view_card = txf.get_card(card_str, piles)
                    pile = self.game.supply.piles[view_card.name]
                    print(Card(**c.card_list[pile.name]))
                    continue
                try:
                    play_card = txf.get_card(card_str, self.hand)

                    assert c.action in play_card.types
                except:
                    print("Invalid input, please try again.")
                    continue

                if self.game.verbose:
                    if not card_methods.confirm_card("Play " + play_card.colored_name() + " (y/n)?"):
                        continue

                play_card.play(self, mute=True)
            else:
                action_cards = [card for card in self.hand if c.action in card.types]
                if len(action_cards) == 0:
                    break
                else:
                    card = np.random.choice(action_cards)
                    card.play(self)

        self.buy()

    def buy(self):
        if self.game.verbose:
            print("---Buying phase---")

        play_treasure_output = self.play_treasure()
        if play_treasure_output == "x":
            return
        elif play_treasure_output == "e":
            return

        while self.buys > 0:
            if self.human:
                view = False
                if self.game.verbose:
                    coins_buys_str = "\nCoins: " + txf.coins(self.coins, plain=True) + "\tBuys: " + str(self.buys)
                    if len(self.effects) > 0:
                        self.update_active_effects()
                        coins_buys_str += "\t\tEffects: " + str(len(self.effects))
                    print(coins_buys_str)
                    if len(self.active_cards) > 0:
                        self.print_active_cards()
                print(self.game.supply)
                card_str = input("Select a card to buy (card name):")
                if card_str == "help":
                    print(txf.help_message)
                    continue
                elif card_str == "x":
                    if card_methods.confirm_card("Exit game (y/n)?"):
                        self.game.game_over = True
                        return
                    continue
                elif card_str == "e":
                    return
                # elif card_str == "p":
                #     self.play_treasure(manual=True)
                #     continue
                elif card_str == "a":
                    self.toggle_autoplay_treasures()
                    continue
                elif card_str == "fx":
                    self.print_active_effects()
                    continue
                elif card_str == "h":
                    self.print_hand()
                    continue
                elif card_str == "vv":
                    v_tmp = self.game.verbose
                    self.game.verbose = 3
                    print(self.game.supply)
                    self.game.verbose = v_tmp
                    continue
                elif card_str == "hh":
                    v_tmp = self.game.verbose
                    self.game.verbose = 2
                    self.print_hand()
                    self.game.verbose = v_tmp
                    continue
                elif card_str == "v":
                    view = True
                    card_str = input("Select card to view (card name):")
                if len(card_str) == 0:
                    print("Invalid card")
                    continue
                piles = [Card(**c.card_list[pile.name]) for pile in list(self.game.supply.piles.values())]
                buy_card = txf.get_card(card_str, piles)
                if buy_card is None:
                    print("Invalid input")
                    continue
                pile = self.game.supply.piles[buy_card.name]
                if view:
                    print(Card(**c.card_list[pile.name]))
                    continue
                if pile.number > 0:
                    if c.contraband in self.effects:
                        if pile.name in self.effects[c.contraband][c.contraband_cards]:
                            print("Pile blocked by Contraband")
                            continue
                    cost = pile.cards[-1].get_cost(player=self)
                    if cost < 0:
                        continue
                    active_card_names = [card.name for card in self.active_cards]
                    if c.quarry in active_card_names:
                        if c.action in pile.cards[-1].types:
                            cost = max(0, cost - (2 * active_card_names.count(c.quarry)))
                    if self.coins >= cost >= 0:
                        if pile.name == c.mint:
                            if not card_methods.confirm_card("Trash all active treasure cards (y/n)?"):
                                continue
                            for active_t_card in [card for card in self.active_cards if c.treasure in card.types]:
                                self.trash(from_pile=self.active_cards, card=active_t_card)
                        if self.game.verbose:
                            print(self.name + " buys " + pile.colored_name())
                        gained_card = self.gain(pile, mute=True, return_card=True)
                        self.coins -= cost
                        self.buys -= 1
                        if c.talisman in active_card_names:
                            self.talisman_effect(pile, gained_card, cost)
                        if c.goons in active_card_names:
                            self.goons_effect()
                        if c.hoard in self.effects:
                            self.hoard_effect(gained_card)
                    else:
                        print("You do not have enough coins")
                        continue
                else:
                    print("The " + pile.colored_name() + " pile is empty")
                    continue
            else:
                affordable_cards = [pile for pile in list(self.game.supply.piles.values())
                                    if self.coins >= pile.get_cost(player=self, mute=True) >= 0 and pile.number > 0]
                active_card_names = [card.name for card in self.active_cards]
                if c.quarry in active_card_names:
                    additional_piles = [pile for pile in list(self.game.supply.piles.values())
                                        if c.action in pile.types and pile not in affordable_cards]
                    for pile in additional_piles:
                        if pile.number > 0 and pile.get_cost(player=self, mute=True) >= 0\
                           and self.coins >= max(0, pile.get_cost(self, mute=True)
                                                 - (2 * active_card_names.count(c.quarry))):
                            affordable_cards.append(pile)
                if c.contraband in self.effects:
                    for blocked_pile in self.effects[c.contraband][c.contraband_cards]:
                        for _pile in affordable_cards:
                            if _pile.name == blocked_pile:
                                affordable_cards.remove(_pile)
                pile = self.game.supply.piles[np.random.choice(affordable_cards).name]
                cost = pile.get_cost(player=self)
                if c.quarry in self.effects and c.action in pile.types:
                    cost = max(0, cost - (2 * self.effects[c.quarry][c.number]))
                if pile.name == c.mint:
                    for active_t_card in [card for card in self.active_cards if c.treasure in card.types]:
                        self.trash(from_pile=self.active_cards, card=active_t_card)
                if self.game.verbose:
                    print(self.name + " buys " + pile.colored_name())
                gained_card = self.gain(pile, mute=True, return_card=True)
                self.coins -= pile.get_cost(player=self)
                self.buys -= 1
                if c.talisman in active_card_names:
                    self.talisman_effect(pile, gained_card, cost)
                if c.goons in active_card_names:
                    self.goons_effect()
                if c.hoard in self.effects:
                    self.hoard_effect(gained_card)

    def play_treasure(self, manual=False):
        hand_treasures = [card for card in self.hand if c.treasure in card.types]
        if len(hand_treasures) == 0 and manual and self.game.verbose:
            print("You have no treasure cards in your hand to play!")

        while (len(hand_treasures) > 0 and not self.autoplay_treasures) or manual:
            if self.human:
                if self.game.verbose:
                    print("Deck: " + str(len(self.deck)) + ",\tDiscard Pile: " + str(len(self.discard_pile)))
                    self.print_hand()
                    coins_buys_str = "\nCoins: " + txf.coins(self.coins, plain=True) + "\tBuys: " + str(self.buys)
                    if len(self.effects) > 0:
                        self.update_active_effects()
                        coins_buys_str += "\t\tEffects: " + str(len(self.effects))
                    print(coins_buys_str)
                    if len(self.active_cards) > 0:
                        self.print_active_cards()
                card_str = input("Select a treasure card to play (card name):")
                if card_str == "help":
                    print(txf.help_message)
                    continue
                if card_str == "x":
                    if card_methods.confirm_card("Exit game (y/n)?"):
                        self.game.game_over = True
                        return "x"
                    continue
                elif card_str == "e":
                    return "e"
                elif card_str == "b":
                    break
                elif card_str == "fx":
                    self.print_active_effects()
                    continue
                elif card_str == "h":
                    continue
                elif card_str == "hh":
                    v_tmp = self.game.verbose
                    self.game.verbose = 2
                    self.print_hand()
                    self.game.verbose = v_tmp
                    continue
                elif card_str == "a":
                    self.toggle_autoplay_treasures()
                    continue
                try:
                    treasure_card = txf.get_card(card_str, self.hand)

                    assert c.treasure in treasure_card.types
                except:
                    print("Invalid input, please try again.")
                    continue

                num = 0
                for card in hand_treasures:
                    if card.name == treasure_card.name:
                        num += 1

                if num > 1:
                    if not card_methods.confirm_card("Play all " + treasure_card.colored_name() + " in hand (y/n)?",
                                                     mute_n=True):
                        treasure_card.play(self, action=False)
                        hand_treasures.remove(treasure_card)
                        continue
                    for card in hand_treasures.copy():
                        if card.name == treasure_card.name:
                            card.play(self, action=False)
                            hand_treasures.remove(card)

                else:
                    if self.game.verbose:
                        if not card_methods.confirm_card("Play " + treasure_card.colored_name() + " (y/n)?"):
                            continue

                    treasure_card.play(self, action=False)
                    hand_treasures.remove(treasure_card)

            else:
                card = np.random.choice(hand_treasures)
                card.play(self, action=False)
                hand_treasures.remove(card)

        if self.autoplay_treasures:
            if [card.name for card in hand_treasures].count(c.bank) > 0:
                offset = 0
                for index in range(len(hand_treasures)):
                    i = index - offset
                    if hand_treasures[i].name == c.bank:
                        hand_treasures.append(hand_treasures.pop(i))
                        offset += 1

            for card in hand_treasures:
                card.play(self, action=False)

    def talisman_effect(self, pile, gained_card, cost):
        if pile.number > 0:
            if c.victory not in gained_card.types and cost <= 4:
                for _ in range([card.name for card in self.active_cards].count(c.talisman)):
                    if pile.number > 0:
                        if self.game.verbose:
                            print(Card(**c.card_list[c.talisman]).colored_name() +
                                  " grants you a copy of " + pile.colored_name())
                        self.gain(pile, mute=True)
                    else:
                        if self.game.verbose:
                            print(Card(**c.card_list[c.talisman]).colored_name() +
                                  " would have granted you a copy of " + pile.colored_name() +
                                  "; however, the pile is empty.")
        else:
            if self.game.verbose:
                print(Card(**c.card_list[c.talisman]).colored_name() +
                      " would have granted you a copy of " + pile.colored_name() + ", however the pile is empty.")

    def goons_effect(self):
        try:
            self.gain_vt(num=self.effects[c.goons][c.number])
        except:
            print(Card(**c.card_list[c.goons]).colored_name() + " was unable to grant any VT")

    def hoard_effect(self, gained_card):
        gold_pile = self.game.supply.piles[c.gold]
        if gold_pile.number > 0:
            if c.victory in gained_card.types:
                for _ in range([card.name for card in self.active_cards].count(c.hoard)):
                    if gold_pile.number > 0:
                        if self.game.verbose:
                            print(Card(**c.card_list[c.hoard]).colored_name() + " grants you a " +
                                  gold_pile.colored_name())
                        self.gain(gold_pile, mute=True)
                    else:
                        if self.game.verbose:
                            print(Card(**c.card_list[c.hoard]).colored_name() +
                                  " would have granted you a " + gold_pile.colored_name() +
                                  "; however, the pile is empty.")
        else:
            if self.game.verbose:
                print(Card(**c.card_list[c.talisman]).colored_name() +
                      " would have granted you a " + gold_pile.colored_name() + ", however the pile is empty.")

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
        for card in self.set_aside_cards:
            self.discard_pile.append(card)
        for card in self.revealed_cards:
            self.discard_pile.append(card)
        self.hand.clear()
        self.active_cards.clear()
        self.revealed_cards.clear()
        self.set_aside_cards.clear()
        self.effects.clear()
        self.actions = 1
        self.buys = 1
        self.coins = 0
        for _ in range(5):
            self.draw(mute=True)

    def draw(self, mute=False, named=True, return_card=False, to_pile=None):
        if len(self.deck) <= 0:
            if len(self.discard_pile) <= 0:
                if self.game.verbose >= 1:
                    print("There are no cards to draw")
                return
            else:
                self.shuffle_deck()

        card = self.deck[-1]
        if not mute and self.game.verbose:
            if named:
                print(self.name + " draws " + card.colored_name())
            else:
                print(self.name + " draws a card")
        if to_pile is None:
            self.hand.append(card)
        else:
            to_pile.append(card)
        self.deck.pop()

        if return_card:
            return card

    def gain(self, pile, to_pile=None, mute=False, return_card=False):
        if pile.number <= 0:
            if self.game.verbose:
                print("The " + pile.colored_name() + " pile is empty!")
            return

        if c.royal_seal in [card.name for card in self.active_cards] and to_pile is not self.deck:
            if self.human:
                if card_methods.confirm_card("Place " + pile.colored_name() + " on top of deck (y/n)?", mute_n=True):
                    to_pile = self.deck
            else:
                if np.random.random() > 0.5:
                    to_pile = self.deck

        if to_pile is None:
            to_pile = self.discard_pile

        if self.game.verbose and not mute:
            print(self.name + " gains " + pile.colored_name())
        gain_card = pile.cards[-1]
        to_pile.append(gain_card)
        pile.remove()

        if to_pile is self.deck and self.game.verbose and not mute:
            print(self.name + " places " + pile.colored_name() + " on top of their deck")

        for card in self.hand:
            if c.reaction in card.types:
                if c.reaction_triggers[card.name] == c.gain:
                    if self.human:
                        if card_methods.confirm_card("Will " + self.name + " reveal " + card.colored_name()
                                                     + " reaction card (y/n)?", mute_n=True):
                            eval("card_reactions." + card.name.lower().replace(" ", "_")
                                 + "_reaction(self, card, gain_card, to_pile)")
                    else:
                        if np.random.random() > 0:
                            eval("card_reactions." + card.name.lower().replace(" ", "_")
                                 + "_reaction(self, card, gain_card, to_pile)")

        if c.trade_route in [_pile.name for _pile in list(self.game.supply.piles.values())]:
            if c.victory in pile.types:
                if pile.name not in self.game.trade_route_mat:
                    self.game.trade_route_mat.append(pile.name)
                    if self.game.verbose:
                        print("Coin token moved from " + pile.colored_name() + " pile to Trade Route mat")

        if return_card:
            return gain_card

    def gain_vt(self, num):
        if self.game.verbose:
            print(self.name + " gains " + txf.vt(num=num, plain=True))
        self.victory_tokens += num

    def trash(self, from_pile, card):
        try:
            assert card in from_pile
            if self.game.verbose:
                print(self.name + " trashes " + card.colored_name())
            self.game.trash.append(card)
            from_pile.remove(card)
        except:
            if self.game.verbose:
                print(card.colored_name() + " is not in expected location and was not trashed")

    def discard(self, from_pile, card, mute=True):
        try:
            assert card in from_pile
            if self.game.verbose and not mute:
                print(self.name + " discards " + card.colored_name())
            self.discard_pile.append(card)
            from_pile.remove(card)
        except:
            if self.game.verbose:
                print(card.name + " is not in expected location and was not discarded")

    def set_aside(self, from_pile, card):
        try:
            assert card in from_pile
            self.set_aside_cards.append(card)
            from_pile.remove(card)
        except:
            if self.game.verbose:
                print(card.name + " is not in expected location and was not set aside")

    def move(self, from_pile, to_pile, card, mute=False):
        try:
            assert card in from_pile
            to_pile.append(card)
            from_pile.remove(card)
        except:
            if self.game.verbose and not mute:
                print(card.colored_name() + " is not in expected location and was not moved")

    def reveal(self, from_pile, cards=None, num=1, move=True, return_cards=False):
        if from_pile == self.deck:
            cards = []
            for _ in range(num):
                cards.append(self.draw(to_pile=self.revealed_cards, mute=True, return_card=True))

        if cards:
            if self.game.verbose:
                print(self.name + " reveals:")
                if type(cards) is Card:
                    print("  " + cards.colored_name())
                elif type(cards) is list:
                    for card in cards:
                        print("  " + card.colored_name())

        if move:
            try:
                if type(cards) is Card:
                    assert cards in from_pile
                    self.revealed_cards.append(cards)
                    from_pile.remove(cards)
                elif type(cards) is list:
                    for card in cards:
                        assert card in from_pile
                        self.revealed_cards.append(card)
                        from_pile.remove(card)
            except:
                pass

        if return_cards:
            return cards

    def reveal_hand(self):
        self.reveal(self.hand, self.hand, move=False)

    def all_cards(self):
        return self.deck + self.hand + self.active_cards + self.revealed_cards + self.set_aside_cards\
               + self.discard_pile

    def update_active_effects(self):
        active_card_names = [card.name for card in self.active_cards]
        for effect in list(self.effects.items()):
            if c.req_active in effect[1].keys():
                if effect[1][c.req_active]:
                    effect[1][c.number] = active_card_names.count(effect[0])
                    if effect[1][c.number] == 0:
                        del self.effects[effect[0]]

    def print_active_effects(self):
        if len(self.effects) == 0:
            print("You have no active effects.")
            return
        print("Effects:")
        for effect in self.effects.items():
            if effect[0] == c.contraband:
                output = txf.bold(effect[0] + " x" + str(effect[1][c.number])) + ":\t" + effect[1][c.description]
                for pile_name in effect[1][c.contraband_cards]:
                    output += Card(**c.card_list[pile_name]).colored_name() + "  "
                print(output)
            else:
                print(txf.bold(effect[0] + " x" + str(effect[1][c.number])) + ":\t" + effect[1][c.description])

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
                print(card.colored_name() + "  ", end="")

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

    def __repr__(self):
        return self.name


class Card:
    def __init__(self, name, set, types:list, cost, text, **kwargs):
        self.name = name
        self.set = set
        self.types = types
        if type(cost) is int:
            self.cost = cost
        else:
            self.cost = eval("card_costs." + self.name.lower().replace(" ", "_") + "_cost")
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

    def play(self, player:Player, action=True, discard=True, mute=False):
        tmp_supply = [(pile.name, pile.cards, pile.number) for pile in list(player.game.supply.piles.values())]
        tmp_deck = player.deck.copy()
        tmp_hand = player.hand.copy()
        tmp_active_cards = player.active_cards.copy()
        tmp_discard_pile = player.discard_pile.copy()
        tmp_revealed_cards = player.revealed_cards.copy()
        tmp_set_aside_cards = player.set_aside_cards.copy()
        tmp_actions = player.actions
        tmp_buys = player.buys
        tmp_coins = player.coins
        tmp_player_effects = {}
        for p in player.game.players:
            tmp_player_effects[p.name] = p.effects

        if player.game.verbose and not mute:
            print(player.name + " plays " + self.colored_name())

        if c.attack in self.types:
            _players = [p for p in player.game.players if p is not player]
            for p in _players:
                for card in p.hand:
                    if c.reaction in card.types:
                        if c.reaction_triggers[card.name] == c.attack:
                            if p.human:
                                if card_methods.confirm_card("Will " + p.name + " reveal " + card.colored_name()
                                                             + " reaction card (y/n)?", mute_n=True):
                                    eval("card_reactions." + card.name.lower().replace(" ", "_") + "_reaction(p, card)")
                            else:
                                if np.random.random() > 0:
                                    eval("card_reactions." + card.name.lower().replace(" ", "_") + "_reaction(p, card)")

        if discard:
            player.move(from_pile=player.hand, to_pile=player.active_cards, card=self, mute=mute)
        success = eval("card_methods." + self.name.lower().replace(" ", "_").replace("\'", "") + "_card(player)")
        for p in player.game.players:
            p.effects = tmp_player_effects[p.name]
        if not success:
            for pile in list(player.game.supply.piles.values()):
                for tmp_pile in tmp_supply:
                    if pile.name == tmp_pile[0]:
                        pile.cards = tmp_pile[1]
                        pile.number = tmp_pile[2]
            player.deck = tmp_deck
            player.hand = tmp_hand
            player.active_cards = tmp_active_cards
            player.discard_pile = tmp_discard_pile
            player.revealed_cards = tmp_revealed_cards
            player.set_aside_cards = tmp_set_aside_cards
            player.actions = tmp_actions
            player.buys = tmp_buys
            player.coins = tmp_coins
            return False
        if action:
            player.actions -= 1

        return True

    def get_cost(self, player=None, printing=False, default=False, mute=False):
        if type(self.cost) is int:
            return self.cost
        else:
            return self.cost(player, printing, default, mute)

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
        return txf.BLACK + self.color + " " + self.name + " " + txf.END

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
        cost_string = txf.coins(self.get_cost(printing=True), plain=True)
        len_cost_string_left = txf.formatted_str_len(cost_string)
        cost_string_right = " " * ((txf.card_width - len_cost_string_left) - 2) + "|\n"
        output += "|" + cost_string + cost_string_right
        output += "|" + "_" * (txf.card_width - 2) + "|\n"
        return output

    def __repr__(self):
        return self.name


class Supply:
    def __init__(self, game, supply=None, sets=None):
        self.game = game
        if supply is None:
            supply = []

        self.piles = self.setup_piles(supply, sets)
        self.spacing = self.spacing()

    def setup_piles(self, supply:list, sets):
        _piles = {}
        if self.game.platinum:
            _piles[c.platinum] = Pile(len(self.game.players), c.platinum)
        for pile in c.initial_treasures:
            _piles[pile] = Pile(len(self.game.players), pile)
        if self.game.colonies:
            _piles[c.colony] = Pile(len(self.game.players), c.colony)
        for pile in c.initial_victory_cards:
            _piles[pile] = Pile(len(self.game.players), pile)
        _piles[c.curse] = Pile(len(self.game.players), c.curse)

        if sets:
            if c.base in sets:
                if c.base_1e not in sets:
                    sets.append(c.base_1e)
                if c.base_2e not in sets:
                    sets.append(c.base_2e)
            elif (c.base_1e in sets or c.base_2e in sets) and len(sets) == 1:
                sets.append(c.base)

        _kingdom_card_piles = []
        assert 0 <= len(supply) <= 10
        for pile in supply:
            if pile not in list(c.card_list.keys()):
                if self.game.verbose:
                    print("Could not find card \"" + str(pile) + "\"")
                continue
            if pile not in [p for p in list(_piles.keys()) + _kingdom_card_piles]:
                _kingdom_card_piles.append(Pile(len(self.game.players), pile))

        while len(_kingdom_card_piles) < 10:
            new_pile = np.random.choice(list(c.card_list.keys()))
            if new_pile == c.platinum or new_pile == c.colony:
                continue
            if new_pile not in [p for p in list(_piles.keys()) + [kcp.name for kcp in _kingdom_card_piles]]:
                if sets:
                    if c.card_list[new_pile][c.set] not in sets:
                        continue
                _kingdom_card_piles.append(Pile(len(self.game.players), new_pile))

        _kingdom_card_piles.sort(key=lambda p: p.get_cost(), reverse=True)

        _kingdom_cards = {}
        for pile in _kingdom_card_piles:
            _kingdom_cards[pile.name] = pile

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
        return max([txf.visible_str_len(txf.bold("1234") + pile.colored_name() + ":")
                    for pile in list(self.piles.values())])

    def __str__(self):
        output = "Supply:\n"
        if self.game.verbose >= 3:
            for pile in self.piles.items():
                output += pile[1].__str__() + "\n"
        else:
            for pile in list(self.piles.values()):
                line = txf.bold(str(pile.get_cost(printing=True)))
                while txf.visible_str_len(line) < 4:
                    line += " "
                line += pile.colored_name() + ":"
                while txf.visible_str_len(line) < self.spacing:
                    line += " "
                output += line + "  " + pile.get_color() + str(pile.number) + txf.END + "\n"

        if c.trade_route in [pile.name for pile in list(self.piles.values())]:
            output += "\nTrade Route mat tokens: " + txf.coins(num=len(self.game.trade_route_mat), plain=True) + "\n"

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

    def get_cost(self, player=None, printing=False, default=False, mute=False):
        if type(self.cost) is int:
            return self.cost
        else:
            return self.cost(player, printing, default, mute)

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

    def __repr__(self):
        return self.name + " pile object"


class Game:
    def __init__(self, players:int, supply=None, sets=None, platinum=False, colonies=False, shelters=False, verbose=1):
        self.platinum = platinum
        self.colonies = colonies
        self.verbose = verbose
        self.trash = []
        self.trade_route_mat = []
        self.turn = 0
        self.game_over = False
        self.players = [Player(self, name="Player " + str(i + 1), shelters=shelters) for i in range(players)]
        if c.set_name:
            name = input("Input your name:")
            self.players[0].set_player_name(name)
        else:
            self.players[0].set_player_name("Bjørni")
        for p in self.players[1:]:
            p.human = False
        self.supply = Supply(self, supply, sets)
        self.use_victory_tokens = self.check_victory_tokens()

        if self.verbose:
            print(self.supply)
            print("Type \"help\" to view list of all commands")

    def gameloop(self):
        if self.verbose:
            print("\nTurn " + str(self.turn + 1) + "\n")
        player = self.players[self.turn % len(self.players)]
        player.play()
        # print("player.effects: {")
        # for effect, attributes in player.effects.items():
        #     print("  " + str(effect) + ": {")
        #     for a in list(attributes.items()):
        #         print("    " + str(a[0]) + ":", a[1])
        #     print("  }")
        # print("}")
        player.cleanup()
        if not self.game_over:
            self.game_over = self.end_conditions()
        self.turn += 1

    def end_conditions(self):
        if self.colonies:
            if self.supply.colonies_empty():
                return True
        if self.supply.empty_piles() >= 3 or self.supply.provinces_empty():
            return True

        return False

    def check_victory_tokens(self):
        card_descriptions = []
        for pile in list(self.supply.piles.values()):
            card_descriptions.append(c.card_text[pile.name])

        return any([" VT " + txf.END in s for s in card_descriptions])

    def score(self):
        print("\n---Results---")
        for player in self.players:
            if self.use_victory_tokens:
                player.victory_points += player.victory_tokens
            for card in player.all_cards():
                if c.victory in card.types or c.curse in card.types:
                    card.play(player, action=False, discard=False, mute=True)

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

            if self.use_victory_tokens:
                print("Victory tokens: " + txf.vt(num=p.victory_tokens, plain=True))

    def print_trash(self):
        print("\nTrash (" + str(len(self.trash)) + " cards):")
        breakdown = self.deck_breakdown(self.trash)
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


num_players = 2
supply_cards = []
active_sets = []

game = Game(players=num_players, supply=supply_cards, sets=active_sets, platinum=True, colonies=True, verbose=1)
while not game.game_over:
    game.gameloop()

game.score()
if card_methods.confirm_card("Show final decks (y/n)?", mute_n=True):
    game.print_decks()
    game.print_trash()
