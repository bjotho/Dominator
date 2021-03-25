import numpy as np
import constants as c
import text_formatting as txf


def confirm_card(player, confirmation_str, mute_n=False):
    while True:
        confirmation = player.game.input(confirmation_str, client=player)
        if confirmation not in ["", "y", "n"]:
            player.game.output("Please type \"y\" or \"n\"")
            continue
        if confirmation == "n":
            if not mute_n:
                player.game.output("Aborted", client=c.ALL)
            return False
        return True


def handle_exception(e):
    if type(e) is ConnectionResetError:
        raise ConnectionResetError
    else:
        print(f"{txf.RED}{e}{txf.END}")


# Base game cards

def cellar_card(player):
    player.actions += 1

    if len(player.hand) == 0:
        return True

    discard_list = []
    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
            discard_cards_str = player.game.input("Select cards to discard (card names, separate with comma):")
            try:
                discard_list = txf.get_cards(discard_cards_str, player.hand)
                if discard_list is None:
                    player.game.output("Invalid input")
                    discard_list = []
                    continue
                for card in discard_list:
                    player.game.output(card.colored_name())
                if not confirm_card(player, "The listed cards will be discarded (y/n):"):
                    return False
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                discard_list = []
                continue
    else:
        for card in player.hand:
            if np.random.random() > 0.5:
                discard_list.append(card)

    for card in discard_list:
        player.discard(player.hand, card, mute=False)

    for _ in range(len(discard_list)):
        player.draw()

    return True


def chapel_card(player):
    if len(player.hand) == 0:
        return True

    trash_list = []
    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
            trash_cards_str = player.game.input("Select up to 4 cards to trash (card names, separate with comma):")
            try:
                trash_list = txf.get_cards(trash_cards_str, player.hand)
                if trash_list is None:
                    player.game.output("Invalid input")
                    trash_list = []
                    continue

                if len(trash_list) > 4:
                    if player.game.verbose:
                        player.game.output("You can only trash up to 4 cards")
                    trash_list = []
                    continue
                for card in trash_list:
                    player.game.output(card.colored_name())
                if not confirm_card(player, "The listed cards will be trashed (y/n):"):
                    return False
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                trash_list = []
                continue
    else:
        for card in player.hand:
            if len(trash_list) >= 4:
                break
            if np.random.random() > 0.5:
                trash_list.append(card)

    for card in trash_list:
        player.trash(player.hand, card)

    return True


def moat_card(player):
    for _ in range(2):
        player.draw()

    return True


def chancellor_card(player):
    player.coins += 2
    if player.human:
        if confirm_card(player, "Discard deck (y/n)?", mute_n=True):
            for card in player.deck:
                player.discard(player.deck, card)
    else:
        if np.random.random() > 0.5:
            for card in player.deck:
                player.discard(player.deck, card)

    return True


def harbinger_card(player):
    player.draw()
    player.actions += 1
    if len(player.discard_pile) == 0:
        if player.game.verbose:
            player.game.output(player.name + "\'s discard pile is empty", client=c.ALL)
        return True

    if player.human:
        player.print_discard_pile()
        while True:
            deck_card = player.game.input("Put a card from the discard pile on top of your deck? "
                                          "(card name, \"x\" for none):")
            if deck_card == "x":
                player.game.output("No card moved", client=c.ALL)
                return True
            if len(deck_card) < 1:
                player.game.output("Invalid input")
                continue
            deck_card = txf.get_card(deck_card, player.discard_pile)
            if not confirm_card(player, "Move " + deck_card.colored_name() + " to top of deck (y/n)?"):
                continue
            player.move(from_pile=player.discard_pile, to_pile=player.deck, card=deck_card)
            break
    else:
        if np.random.random() > 0.5 and len(player.discard_pile) > 0:
            deck_card = np.random.choice(player.discard_pile)
            player.move(from_pile=player.discard_pile, to_pile=player.deck, card=deck_card)

    return True


def merchant_card(player):
    player.draw()
    player.actions += 1
    if c.merchant in player.effects:
        player.effects[c.merchant][c.number] += 1
    else:
        player.effects[c.merchant] = c.effect_dict[c.merchant].copy()

    return True


def vassal_card(player):
    player.coins += 2
    card = player.draw(return_card=True, to_pile=player.discard_pile)
    if player.game.verbose:
        player.game.output(player.name + " discards " + card.colored_name(), client=c.ALL)

    success = True
    if c.action in card.types:
        if player.human:
            if confirm_card(player, "Play " + card.colored_name() + " (y/n)?"):
                success = card.play(player, action=False, discard=False, mute=True)
                if success:
                    player.move(from_pile=player.discard_pile, to_pile=player.active_cards, card=card)
        else:
            success = card.play(player, action=False, discard=False)
            if success:
                player.move(from_pile=player.discard_pile, to_pile=player.active_cards, card=card)

    return success


def village_card(player):
    player.draw()
    player.actions += 2

    return True


def woodcutter_card(player):
    player.buys += 1
    player.coins += 2

    return True


def workshop_card(player):
    if player.human:
        if player.game.verbose:
            player.game.output(player.game.supply.__str__())
        while True:
            gain_card = player.game.input("Select a card to gain costing up to " + txf.coins(4, plain=True) +
                                          " (card name):")
            if len(gain_card) < 1:
                player.game.output("Invalid input")
                continue
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if 0 <= pile.get_cost(player, mute=True) <= 4 and pile.number > 0]
            gain_pile = txf.get_card(gain_card, gainable_cards)
            if gain_pile is None:
                player.game.output("Invalid input")
                continue
            player.gain(gain_pile)
            break
    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                          if 0 <= pile.get_cost(player, mute=True) <= 4 and pile.number > 0]
        if len(gainable_cards) > 0:
            gain_pile = np.random.choice(gainable_cards)
            player.gain(gain_pile)

    return True


def bureaucrat_card(player):
    player.gain(player.game.supply.piles[c.silver], to_pile=player.deck, mute=True)
    if player.game.verbose:
        player.game.output(player.name + " gains " + txf.treasure(c.silver) + " and puts it on top of their deck",
                           client=c.ALL)

    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        victory_cards = [card for card in v.hand if c.victory in card.types]
        if len(victory_cards) == 0:
            v.reveal_hand()
        elif len(victory_cards) == 1:
            v.reveal(from_pile=v.hand, cards=victory_cards[0])
            v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=victory_cards[0])
            if player.game.verbose:
                player.game.output("... And puts it on top of their deck", client=c.ALL)
        else:
            if v.human:
                if player.game.verbose:
                    player.game.output("Victory cards:", client=v)
                for card in victory_cards:
                    if player.game.verbose:
                        if player.game.verbose >= 2:
                            player.game.output(card.__str__())
                        else:
                            player.game.output("  " + card.colored_name(), client=v)
                while True:
                    reveal_card_str = player.game.input("Select victory card to reveal (card name):", client=v)
                    try:
                        reveal_card = txf.get_card(reveal_card_str, victory_cards)
                        if reveal_card is None:
                            player.game.output("Invalid input", client=v)
                            continue
                        v.reveal(from_pile=v.hand, cards=reveal_card)
                        v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=reveal_card)
                        if player.game.verbose:
                            player.game.output("... And puts it on top of their deck", client=c.ALL)
                        break
                    except Exception as e:
                        handle_exception(e)
                        player.game.output("Invalid input", client=v)
                        continue
            else:
                reveal_card = np.random.choice(victory_cards)
                v.reveal(from_pile=v.hand, cards=reveal_card)
                v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=reveal_card)
                if player.game.verbose:
                    player.game.output("... And puts it on top of their deck", client=c.ALL)

    return True


def feast_card(player):
    self_card = None
    for card in player.active_cards:
        if card.name == c.feast:
            self_card = card

    if self_card:
        player.trash(player.active_cards, self_card)

    if player.human:
        if player.game.verbose:
            player.game.output(player.game.supply.__str__())
        while True:
            gain_card_str = player.game.input("Select a card to gain costing up to " + txf.coins(5, plain=True) +
                                              " (card name):")
            if len(gain_card_str) < 1:
                player.game.output("Invalid input")
                continue
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if 0 <= pile.get_cost(player, mute=True) <= 5 and pile.number > 0]
            gain_pile = txf.get_card(gain_card_str, gainable_cards)
            if gain_pile is None:
                player.game.output("Invalid input")
                continue
            player.gain(gain_pile)
            break
    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                          if 0 <= pile.get_cost(player, mute=True) <= 5 and pile.number > 0]
        if len(gainable_cards) > 0:
            gain_pile = np.random.choice(gainable_cards)
            player.gain(gain_pile)

    return True


def gardens_card(player):
    player.victory_points += len(player.all_cards()) // 10

    return True


def militia_card(player):
    player.coins += 2
    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        num = 0
        while len(v.hand) > 3:
            discard_list = []
            if v.human:
                if player.game.verbose:
                    v.print_hand()
                    player.game.output("Discard down to 3 cards (card names, separate with comma):", client=v)
                discard_cards_str = player.game.input(client=v)
                try:
                    discard_list = txf.get_cards(discard_cards_str, v.hand)
                    if discard_list is None:
                        player.game.output("Invalid input", client=v)
                        continue

                    if len(v.hand) - len(discard_list) != 3:
                        continue
                    for card in discard_list:
                        player.game.output(card.colored_name(), client=v)
                    if not confirm_card(v, "The listed cards will be discarded (y/n):"):
                        continue
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input", client=v)
                    continue
            else:
                tmp_hand = v.hand.copy()
                while len(v.hand) - len(discard_list) > 3:
                    discard_card = np.random.choice(tmp_hand)
                    discard_list.append(discard_card)
                    del tmp_hand[tmp_hand.index(discard_card)]

            for card in discard_list:
                v.discard(v.hand, card)
                num += 1

            if player.game.verbose:
                player.game.output(v.name + " discards " + str(num) + " cards", client=c.ALL)

    return True


def moneylender_card(player):
    copper_card = None
    for card in player.hand:
        if card.name == c.copper:
            copper_card = card

    if not copper_card:
        if player.game.verbose:
            player.game.output(player.name + " does not have any Copper cards", client=c.ALL)
        return True
    else:
        if player.human:
            player.print_hand()
            if not confirm_card(player, "Trash " + copper_card.colored_name() + " (y/n)?"):
                return True

    player.trash(player.hand, copper_card)
    player.coins += 3

    return True


def poacher_card(player):
    player.draw()
    player.actions += 1
    player.coins += 1
    empty_piles = len([pile for pile in player.game.supply.piles.values() if pile.number == 0])
    discard_list = []
    if player.human:
        if empty_piles > 0:
            while True:
                if player.game.verbose:
                    player.print_hand()
                    player.game.output("Select " + str(empty_piles) + " cards to discard (card names):")
                discard_cards_str = player.game.input()
                try:
                    discard_list = txf.get_cards(discard_cards_str, player.hand)
                    if discard_list is None:
                        player.game.output("Invalid input")
                        discard_list = []
                        continue

                    assert len(discard_list) == empty_piles
                    for card in discard_list:
                        player.game.output(card.colored_name())
                    if not confirm_card(player, "The listed cards will be discarded (y/n):"):
                        return False

                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input")
                    discard_list = []
                    continue
    else:
        for _ in range(empty_piles):
            if len(player.hand) > 0:
                discard_card = np.random.choice(player.hand)
                discard_list.append(discard_card)

    for card in discard_list:
        player.discard(player.hand, card)

    return True


def remodel_card(player):
    if len(player.hand) == 0:
        return True

    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
            remodel_card_str = player.game.input("Select a card to remodel (card name):")
            try:
                _remodel_card = txf.get_card(remodel_card_str, player.hand)
                if _remodel_card is None:
                    player.game.output("Invalid input")
                    continue

                if _remodel_card.get_cost(player, default=True) < 0:
                    continue

                if not confirm_card(player, _remodel_card.colored_name() + " will be trashed (y/n):"):
                    return False

                gain_coins = _remodel_card.get_cost(player, default=True) + 2
                if player.game.verbose:
                    player.game.output(player.game.supply.__str__())
                gain_card_str = player.game.input("Select a card to gain costing up to " +
                                                  txf.coins(gain_coins, plain=True) + " (card name):")
                gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                                  if 0 <= pile.get_cost(player, mute=True) <= gain_coins and pile.number > 0]
                gain_pile = txf.get_card(gain_card_str, gainable_cards)
                if gain_pile is None:
                    player.game.output("Invalid input")
                    continue
                player.trash(player.hand, _remodel_card)
                player.gain(gain_pile)
                break

            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                continue
    else:
        if len(player.hand) > 0:
            _remodel_card = np.random.choice(player.hand)
            gain_coins = _remodel_card.get_cost(player, default=True) + 2
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if 0 <= pile.get_cost(player, mute=True) <= gain_coins and pile.number > 0]
            if len(gainable_cards) > 0:
                gain_pile = np.random.choice(gainable_cards)
                player.trash(player.hand, _remodel_card)
                player.gain(gain_pile)

    return True


def smithy_card(player):
    for _ in range(3):
        player.draw()

    return True


def spy_card(player):
    player.draw()
    player.actions += 1
    players = [p for p in player.game.players if c.moat not in p.effects]
    for p in players:
        _reveal_card = p.draw(mute=True, return_card=True, to_pile=p.revealed_cards)
        p.reveal(from_pile=p.revealed_cards, cards=_reveal_card, move=False)
        if player.human:
            if confirm_card(p, "Put back on deck (y) or discard (n)?:", mute_n=True):
                if player.game.verbose:
                    player.game.output(_reveal_card.colored_name() + " put back on deck", client=c.ALL)
                p.move(from_pile=p.revealed_cards, to_pile=p.deck, card=_reveal_card)
            else:
                if player.game.verbose:
                    player.game.output(_reveal_card.colored_name() + " discarded", client=c.ALL)
                p.discard(p.revealed_cards, _reveal_card)
        else:
            if np.random.random() > 0.5:
                if player.game.verbose:
                    player.game.output(_reveal_card.colored_name() + " discarded", client=c.ALL)
                p.discard(p.revealed_cards, _reveal_card)
            else:
                if player.game.verbose:
                    player.game.output(_reveal_card.colored_name() + " put back on deck", client=c.ALL)
                p.move(from_pile=p.revealed_cards, to_pile=p.deck, card=_reveal_card)

    return True


def thief_card(player):
    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        for _ in range(2):
            v.draw(mute=True, to_pile=v.revealed_cards)
        v.reveal(from_pile=v.revealed_cards, cards=v.revealed_cards, move=False)
        eligible_cards = [card for card in v.revealed_cards if c.treasure in card.types]
        trash_card = None
        if len(eligible_cards) <= 0:
            continue
        elif len(eligible_cards) == 1:
            trash_card = eligible_cards[0]
            v.trash(v.revealed_cards, trash_card)
        else:
            if player.human:
                while True:
                    trash_card_str = player.game.input("Select card to trash (card name):")
                    try:
                        trash_card = txf.get_card(trash_card_str, eligible_cards)
                        if trash_card is None:
                            player.game.output("Invalid input")
                            continue
                        v.trash(v.revealed_cards, trash_card)
                        break
                    except Exception as e:
                        handle_exception(e)
                        player.game.output("Invalid input")
                        continue
            else:
                trash_card = np.random.choice(eligible_cards)
                v.trash(v.revealed_cards, trash_card)

        if player.human:
            if confirm_card(player, "Gain " + trash_card.colored_name() + " (y/n)?", mute_n=True):
                if player.game.verbose:
                    player.game.output(player.name + " gains " + trash_card.colored_name(), client=c.ALL)
                player.move(from_pile=player.game.trash[::-1], to_pile=player.discard_pile, card=trash_card)
        else:
            if np.random.random() > 0.5:
                if player.game.verbose:
                    player.game.output(player.name + " gains " + trash_card.colored_name(), client=c.ALL)
                player.move(from_pile=player.game.trash[::-1], to_pile=player.discard_pile, card=trash_card)

    for v in victims:
        for card in v.revealed_cards:
            v.discard(v.revealed_cards, card)

    return True


def throne_room_card(player):
    no_action_cards = True
    for card in player.hand:
        if c.action in card.types:
            no_action_cards = False
            break

    if no_action_cards:
        if player.game.verbose:
            player.game.output(player.name + " has no action cards to play", client=c.ALL)
    else:
        if player.human:
            if player.game.verbose:
                player.print_hand()
            while True:
                card_str = player.game.input("Select action card to play twice (card name):")
                try:
                    throned_card = txf.get_card(card_str, player.hand)

                    if throned_card is None:
                        player.game.output("Invalid input")
                        continue

                    if c.action not in throned_card.types:
                        player.game.output(throned_card.colored_name() + " is not an action card")
                        continue

                    if not confirm_card(player, "Play " + throned_card.colored_name() + " (y/n)?"):
                        continue

                    for _ in range(2):
                        if player.game.verbose:
                            player.game.output(player.name + " plays " + throned_card.colored_name(), client=c.ALL)
                        success = throned_card.play(player, action=False, mute=True)
                        if not success:
                            return False

                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input")
                    continue
        else:
            eligible_cards = [card for card in player.hand if c.action in card.types]
            throned_card = np.random.choice(eligible_cards)
            for _ in range(2):
                if player.game.verbose:
                    player.game.output(player.name + " plays " + throned_card.colored_name(), client=c.ALL)
                success = throned_card.play(player, action=False, mute=True)
                if not success:
                    return False

    return True


def bandit_card(player):
    player.gain(player.game.supply.piles[c.gold])
    victims = [v for v in player.game.players if c.moat not in v.effects and v is not player]
    for v in victims:
        for _ in range(2):
            v.draw(mute=True, to_pile=v.revealed_cards)
        v.reveal(from_pile=v.revealed_cards, cards=v.revealed_cards, move=False)
        eligible_cards = [card for card in v.revealed_cards if (c.treasure in card.types) and (card.name != c.copper)]
        if len(eligible_cards) <= 0:
            continue
        elif len(eligible_cards) == 1:
            trash_card = eligible_cards[0]
            v.trash(v.revealed_cards, trash_card)
        else:
            if v.human:
                while True:
                    trash_card_str = player.game.input("Select card to trash (card name):")
                    try:
                        trash_card = txf.get_card(trash_card_str, eligible_cards)
                        if trash_card is None:
                            player.game.output("Invalid input", client=v)
                            continue
                        v.trash(v.revealed_cards, trash_card)
                        break
                    except Exception as e:
                        handle_exception(e)
                        player.game.output("Invalid input", client=v)
                        continue
            else:
                trash_card = np.random.choice(eligible_cards)
                v.trash(v.revealed_cards, trash_card)

    for v in victims:
        for card in v.revealed_cards:
            v.discard(v.revealed_cards, card)

    return True


def council_room_card(player):
    for _ in range(4):
        player.draw()

    players = [p for p in player.game.players if p is not player]
    for p in players:
        p.draw()

    return True


def festival_card(player):
    player.actions += 2
    player.buys += 1
    player.coins += 2

    return True


def laboratory_card(player):
    for _ in range(2):
        player.draw()
    player.actions += 1

    return True


def library_card(player):
    while len(player.hand) < 7 and (len(player.deck) + len(player.discard_pile)) > 0:
        card = player.draw(return_card=True)
        if c.action in card.types:
            if player.human:
                if confirm_card(player, "Set aside " + card.colored_name() + " (y/n)?", mute_n=True):
                    player.move(from_pile=player.hand, to_pile=player.set_aside_cards, card=card)
            else:
                if player.actions - 1 <= len(player.set_aside_cards):
                    player.move(from_pile=player.hand, to_pile=player.set_aside_cards, card=card)

    for card in player.set_aside_cards:
        player.discard(player.set_aside_cards, card)

    return True


def market_card(player):
    player.draw()
    player.actions += 1
    player.buys += 1
    player.coins += 1

    return True


def mine_card(player):
    treasure_cards = [card for card in player.hand if c.treasure in card.types]
    if len(treasure_cards) == 0:
        if player.game.verbose:
            player.game.output(player.name + " does not have any treasure cards", client=c.ALL)
        return True

    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
                player.game.output("Select a treasure card to trash (card name, \"x\" for none):")
            mine_card_str = player.game.input()
            if mine_card_str == "x":
                if player.game.verbose:
                    player.game.output("No cards trashed", client=c.ALL)
                return True
            try:
                _mine_card = txf.get_card(mine_card_str, player.hand)
                if _mine_card is None or c.treasure not in _mine_card.types:
                    player.game.output("Invalid input")
                    continue

                if not confirm_card(player, _mine_card.colored_name() + " will be trashed (y/n):"):
                    return False

                gain_coins = _mine_card.get_cost(player, default=True) + 3
                if player.game.verbose:
                    player.game.output(player.game.supply.__str__())
                    player.game.output("Select a treasure card to gain costing up to " +
                                       txf.coins(gain_coins, plain=True) + " (card name):")
                gain_card_str = player.game.input()

                if len(gain_card_str) < 1:
                    player.game.output("Invalid input")
                    continue
                gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                                  if 0 <= pile.get_cost(player, mute=True) <= gain_coins and pile.number > 0
                                  and c.treasure in pile.types]
                gain_pile = txf.get_card(gain_card_str, gainable_cards)
                if gain_pile is None:
                    player.game.output("Invalid input")
                    continue
                player.trash(player.hand, _mine_card)
                if player.game.verbose:
                    player.game.output(player.name + " gains " + gain_pile.colored_name() + " to their hand",
                                       client=c.ALL)
                player.gain(gain_pile, to_pile=player.hand, mute=True)
                break

            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                continue
    else:
        if len(player.hand) > 0:
            _mine_card = np.random.choice(treasure_cards)
            gain_coins = _mine_card.get_cost(player, default=True) + 3
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if 0 <= pile.get_cost(player, mute=True) <= gain_coins and pile.number > 0
                              and c.treasure in pile.types]
            if len(gainable_cards) > 0:
                gain_pile = np.random.choice(gainable_cards)
                player.trash(player.hand, _mine_card)
                player.gain(gain_pile, to_pile=player.hand, mute=True)
                if player.game.verbose:
                    player.game.output(player.name + " gains " + gain_pile.colored_name() + " to their hand",
                                       client=c.ALL)

    return True


def sentry_card(player):
    player.draw()
    player.actions += 1
    for _ in range(2):
        _card = player.draw(to_pile=player.set_aside_cards, mute=True, return_card=True)
        if _card is None:
            break
        if player.game.verbose:
            player.game.output(player.name + " sets aside " + _card.colored_name(), client=c.ALL)

    if len(player.set_aside_cards) == 0:
        if player.game.verbose:
            player.game.output(player.name + " has no cards to set aside", client=c.ALL)
        return True

    if player.human:
        if player.game.verbose:
            player.game.output("Cards:")
            for card in player.set_aside_cards:
                player.game.output("  " + card.colored_name())
        while True:
            trash_cards_str = player.game.input("Select cards to trash "
                                                "(card names, separate with comma, \"x\" for none):")
            if trash_cards_str == "x":
                if player.game.verbose:
                    player.game.output("No cards trashed", client=c.ALL)
                break
            try:
                trash_list = txf.get_cards(trash_cards_str, player.set_aside_cards)
                if trash_list is None:
                    player.game.output("Invalid input")
                    continue
                for card in trash_list:
                    player.game.output(card.colored_name())
                if not confirm_card(player, "The listed cards will be trashed (y/n):"):
                    return False
                for card in trash_list:
                    player.trash(player.set_aside_cards, card)
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                continue

        if len(player.set_aside_cards) > 0:
            if len(player.set_aside_cards) > 1:
                if player.game.verbose:
                    player.game.output("Cards:")
                    for card in player.set_aside_cards:
                        player.game.output("  " + card.colored_name())
                while True:
                    discard_cards_str = player.game.input("Select cards to discard "
                                                          "(card names, separate with comma, \"x\" for none):")
                    if discard_cards_str == "x":
                        if player.game.verbose:
                            player.game.output("No cards discarded", client=c.ALL)
                        break
                    try:
                        discard_list = txf.get_cards(discard_cards_str, player.set_aside_cards)
                        if discard_list is None:
                            player.game.output("Invalid input")
                            continue
                        for card in discard_list:
                            player.game.output(card.colored_name())
                        if not confirm_card(player, "The listed cards will be discarded (y/n):"):
                            return False
                        for card in discard_list:
                            player.discard(player.set_aside_cards, card)
                        break
                    except Exception as e:
                        handle_exception(e)
                        player.game.output("Invalid input")
                        continue
            else:
                if confirm_card(player, "Discard " + player.set_aside_cards[0].colored_name() + " (y/n)?", mute_n=True):
                    player.discard(player.set_aside_cards, player.set_aside_cards[0])

        if len(player.set_aside_cards) > 1:
            if player.game.verbose:
                player.game.output("Cards:")
                for card in player.set_aside_cards:
                    player.game.output("  " + card.colored_name())
            while True:
                top_deck_card_str = player.game.input("Select card to place on top of deck (card name):")
                try:
                    top_card, i = txf.get_card(top_deck_card_str, player.set_aside_cards, return_index=True)
                    if top_card is None:
                        player.game.output("Invalid input")
                        continue
                    if confirm_card(player, top_card.colored_name() + " will be placed on top of your deck (with "
                                    + player.set_aside_cards[1 - i].colored_name() + " directly beneath) (y/n):"):
                        if player.game.multiplayer():
                            player.game.output(player.name + "puts two cards on top of their deck", client=c.OTHERS)
                        player.move(from_pile=player.set_aside_cards, to_pile=player.deck,
                                    card=player.set_aside_cards[i - 1])
                        player.move(from_pile=player.set_aside_cards, to_pile=player.deck, card=top_card)
                    else:
                        return False
                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input")
                    continue
        elif len(player.set_aside_cards) == 1:
            if player.game.verbose:
                player.game.output("You put " + player.set_aside_cards[0].colored_name() + " on top of your deck")
                if player.game.multiplayer():
                    player.game.output(player.name + " puts a card on top of their deck", client=c.OTHERS)

            player.move(from_pile=player.set_aside_cards, to_pile=player.deck, card=player.set_aside_cards[0])
    else:
        re_deck_cards = [None, None]
        for card in player.set_aside_cards:
            choice = np.random.random()
            if choice <= 0.33:
                player.trash(player.set_aside_cards, card)
            elif 0.33 < choice <= 0.66:
                player.discard(player.set_aside_cards, card)
            else:
                re_deck_cards[np.random.randint(0, 2)] = card

        for card in re_deck_cards:
            if card:
                player.move(from_pile=player.set_aside_cards, to_pile=player.deck, card=card)

    return True


def witch_card(player):
    for _ in range(2):
        player.draw()

    victims = [p for p in player.game.players if c.moat not in p.effects and p is not player]
    for v in victims:
        v.gain(player.game.supply.piles[c.curse])

    return True


def adventurer_card(player):
    revealed_treasure_cards = []
    while len(revealed_treasure_cards) < 2 and (len(player.deck) + len(player.discard_pile)) > 0:
        _card = player.reveal(from_pile=player.deck, return_cards=True)[0]
        if c.treasure in _card.types:
            revealed_treasure_cards.append(_card)
            player.move(from_pile=player.revealed_cards, to_pile=player.hand, card=_card)

    for card in player.revealed_cards:
        player.discard(player.revealed_cards, card)

    return True


def artisan_card(player):
    if player.human:
        if player.game.verbose:
            player.game.output(player.game.supply.__str__())
        while True:
            gain_card_str = player.game.input("Select a card to gain costing up to " + txf.coins(5, plain=True) +
                                              " (card name):")
            if len(gain_card_str) < 1:
                player.game.output("Invalid input")
                continue
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if 0 <= pile.get_cost(player, mute=True) <= 5 and pile.number > 0]
            gain_pile = txf.get_card(gain_card_str, gainable_cards)
            if gain_pile is None:
                player.game.output("Invalid input")
                continue
            player.gain(gain_pile)
            break

        if player.game.verbose:
            player.print_hand()
        while len(player.hand) > 0:
            deck_card_str = player.game.input("Put a card from your hand onto your deck (card name):")
            try:
                deck_card = txf.get_card(deck_card_str, player.hand)
                if deck_card is None:
                    player.game.output("Invalid input")
                    continue
                if not confirm_card(player, "Put " + deck_card.colored_name() + " on top of deck (y/n)?"):
                    return False
                if player.game.multiplayer():
                    player.game.output(player.name + " puts a card onto their deck", client=c.OTHERS)
                player.move(from_pile=player.hand, to_pile=player.deck, card=deck_card)
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                continue

    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                          if 0 <= pile.get_cost(player, mute=True) <= 5 and pile.number > 0]
        if len(gainable_cards) > 0:
            gain_pile = np.random.choice(gainable_cards)
            player.gain(gain_pile)

        if len(player.hand) > 0:
            deck_card = np.random.choice(player.hand)
            player.move(from_pile=player.hand, to_pile=player.deck, card=deck_card)

    return True


# Prosperity cards

def loan_card(player):
    player.coins += 1

    while len(player.deck) + len(player.discard_pile) > 0:
        revealed_card = player.reveal(from_pile=player.deck, return_cards=True)[0]
        if c.treasure in revealed_card.types:
            if player.human:
                if confirm_card(player, "Trash " + revealed_card.colored_name() + " (y/n)?", mute_n=True):
                    player.trash(from_pile=player.revealed_cards, card=revealed_card)
            else:
                if np.random.random() > 0.5:
                    player.trash(from_pile=player.revealed_cards, card=revealed_card)
            break

    for card in player.revealed_cards:
        player.discard(from_pile=player.revealed_cards, card=card)

    return True


def trade_route_card(player):
    player.buys += 1

    if player.human:
        trash_card = None
        while True:
            if player.game.verbose:
                player.print_hand()
            trash_card_str = player.game.input("Select card to trash (card name):")
            try:
                trash_card = txf.get_card(input_str=trash_card_str, from_pile=player.hand)
                if trash_card is None:
                    player.game.output("Invalid input")
                    continue

                if not confirm_card(player, trash_card.colored_name() + " will be trashed (y/n):"):
                    return False
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                continue
        player.trash(from_pile=player.hand, card=trash_card)
    else:
        player.trash(from_pile=player.hand, card=np.random.choice(player.hand))

    player.coins += len(player.game.trade_route_mat)

    return True


def watchtower_card(player):
    while len(player.hand) < 6:
        player.draw()

    return True


def bishop_card(player):
    player.coins += 1
    player.gain_vt(1)

    trash_card = None
    if player.human:
        if player.game.verbose:
            player.print_hand()
        while True:
            trash_card_str = player.game.input("Select card to trash (card name):")
            try:
                trash_card = txf.get_card(input_str=trash_card_str, from_pile=player.hand)
                if trash_card is None:
                    player.game.output("Invalid input")
                    continue

                if not confirm_card(player, trash_card.colored_name() + " will be trashed (y/n):"):
                    return False
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                continue
        player.trash(from_pile=player.hand, card=trash_card)
    else:
        trash_card = np.random.choice(player.hand)
        player.trash(from_pile=player.hand, card=trash_card)

    vt_gain = trash_card.get_cost(default=True) // 2
    player.gain_vt(vt_gain)

    players = [p for p in player.game.players if p is not player]
    for p in players:
        trash_card = None
        if p.human:
            if player.game.verbose:
                p.print_hand()
            while True:
                if player.game.multiplayer():
                    player.game.output(p.name + " may trash a card from their hand...")
                    trash_card_str = player.game.input("You may trash a card from your hand "
                                                       "(card name, \"x\" for none):", client=p)
                else:
                    trash_card_str = player.game.input(p.name + " may trash a card from their hand "
                                                                "(card name, \"x\" for none):", client=p)
                if trash_card_str == "x":
                    if player.game.verbose:
                        player.game.output(p.name + " trashes no cards", client=c.ALL)
                    break
                try:
                    trash_card = txf.get_card(input_str=trash_card_str, from_pile=p.hand)
                    if trash_card is None:
                        player.game.output("Invalid input", client=p)
                        continue

                    if not confirm_card(p, trash_card.colored_name() + " will be trashed (y/n):"):
                        return False
                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input", client=p)
                    continue
            if trash_card:
                p.trash(from_pile=p.hand, card=trash_card)
        else:
            if np.random.random() > 0.5:
                trash_card = np.random.choice(p.hand)
                p.trash(from_pile=p.hand, card=trash_card)

    return True


def monument_card(player):
    player.coins += 2
    player.gain_vt(1)

    return True


def quarry_card(player):
    player.coins += 1
    if c.quarry in player.effects:
        player.effects[c.quarry][c.number] += 1
    else:
        player.effects[c.quarry] = c.effect_dict[c.quarry].copy()

    return True


def talisman_card(player):
    player.coins += 1
    if c.talisman in player.effects:
        player.effects[c.talisman][c.number] += 1
    else:
        player.effects[c.talisman] = c.effect_dict[c.talisman].copy()

    return True


def workers_village_card(player):
    player.draw()
    player.actions += 2
    player.buys += 1

    return True


def city_card(player):
    player.draw()
    player.actions += 2

    empty_piles = len([pile for pile in player.game.supply.piles.values() if pile.number == 0])
    if empty_piles >= 1:
        player.draw()

        if empty_piles >= 2:
            player.buys += 1
            player.coins += 1

    return True


def contraband_card(player):
    player.coins += 3
    player.buys += 1

    blocked_pile = None
    left_player = player.game.players[(player.game.players.index(player) + 1) % len(player.game.players)]
    if left_player.human:
        while True:
            blocked_pile_str = player.game.input(left_player.name + ", select pile to prevent " + player.name +
                                                 " from buying (pile name):", client=left_player)
            try:
                blocked_pile = txf.get_pile(input_str=blocked_pile_str, supply_piles=player.game.supply.piles)
                assert blocked_pile is not None
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input", client=left_player)
                continue
    else:
        blocked_pile = np.random.choice(list(player.game.supply.piles.values()))

    if c.contraband in player.effects:
        player.effects[c.contraband][c.number] += 1
        if blocked_pile.name not in player.effects[c.contraband][c.contraband_cards]:
            player.effects[c.contraband][c.contraband_cards].append(blocked_pile.name)
        else:
            if player.game.verbose:
                player.game.output(blocked_pile.colored_name() + " pile is already blocked", client=c.ALL)
    else:
        player.effects[c.contraband] = c.effect_dict[c.contraband].copy()
        player.effects[c.contraband][c.contraband_cards] = [blocked_pile.name]

    if player.game.verbose:
        player.game.output(left_player.name + " blocks the " + blocked_pile.colored_name() + " pile", client=c.ALL)

    return True


def counting_house_card(player):
    discarded_coppers = [card for card in player.discard_pile if card.name == c.copper]
    num = 0
    if player.human:
        if len(discarded_coppers) == 0:
            if player.game.verbose:
                player.game.output("You have no coppers in your discard pile")
                if player.game.multiplayer():
                    player.game.output(player.name + " has no coppers in their discard pile", client=c.OTHERS)
            return True
        else:
            if player.game.verbose:
                player.game.output("Your discard pile contains " + txf.bold(str(len(discarded_coppers)) + "x ") +
                                   discarded_coppers[0].colored_name())
            while True:
                num_str = player.game.input("How many coppers will you reveal and put into your hand (0-" +
                                            str(len(discarded_coppers)) + ")?")
                try:
                    num = int(num_str)
                    assert len(discarded_coppers) >= num >= 0
                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input")
                    continue
    else:
        num = np.random.randint(0, len(discarded_coppers) + 1)

    player.reveal(from_pile=player.discard_pile, cards=discarded_coppers[:num])
    for card in discarded_coppers[:num]:
        player.move(from_pile=player.revealed_cards, to_pile=player.hand, card=card)

    if player.game.verbose:
        if len(discarded_coppers) == 1:
            player.game.output("... And puts it into their hand", client=c.ALL)
        elif len(discarded_coppers) > 1:
            player.game.output("... And puts them into their hand", client=c.ALL)

    return True


def mint_card(player):
    hand_treasures = [card for card in player.hand if c.treasure in card.types]
    copy_card = None
    if len(hand_treasures) == 0:
        if player.game.verbose:
            player.game.output("You have no treasures in your hand")
            if player.game.multiplayer():
                player.game.output("No treasures revealed", client=c.OTHERS)
        return True
    elif len(hand_treasures) == 1:
        if player.human:
            if confirm_card(player, "Reveal and copy " + hand_treasures[0].colored_name() + " (y/n)?"):
                copy_card = hand_treasures[0]
            else:
                return False
        else:
            if np.random.random() > 0.5:
                copy_card = hand_treasures[0]
    else:
        if player.human:
            while True:
                copy_card_str = player.game.input("Select treasure card to reveal and copy "
                                                  "(card name, \"x\" for none):")
                if copy_card_str == "x":
                    player.game.output("No treasures revealed", client=c.ALL)
                    return True
                try:
                    copy_card = txf.get_card(copy_card_str, hand_treasures)
                    if copy_card is None:
                        player.game.output("Invalid input")
                        continue
                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input")
                    continue
        else:
            if np.random.random() > 0.5:
                copy_card = np.random.choice(hand_treasures)

    if copy_card:
        player.reveal(from_pile=player.hand, cards=copy_card, move=False)
        copy_pile = txf.get_pile(input_str=copy_card.name, supply_piles=player.game.supply.piles)
        player.gain(pile=copy_pile)

    return True


def mountebank_card(player):
    player.coins += 2

    curse_pile = player.game.supply.piles[c.curse]
    copper_pile = player.game.supply.piles[c.copper]
    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        curse_cards = [card for card in v.hand if c.curse in card.types]
        if len(curse_cards) == 0:
            v.gain(curse_pile)
            v.gain(copper_pile)
        else:
            if v.human:
                if player.game.verbose:
                    v.print_hand()
                if confirm_card(v, "Discard a curse card (y/n)?"):
                    v.discard(from_pile=v.hand, card=curse_cards[0])
                    if player.game.verbose:
                        player.game.output(v.name + " discards " + curse_cards[0].colored_name(), client=c.ALL)
                else:
                    v.gain(curse_pile)
                    v.gain(copper_pile)
            else:
                if np.random.random() > 0.5:
                    v.discard(from_pile=v.hand, card=curse_cards[0])
                    if player.game.verbose:
                        player.game.output(v.name + " discards " + curse_cards[0].colored_name(), client=c.ALL)
                else:
                    v.gain(curse_pile)
                    v.gain(copper_pile)

    return True


def rabble_card(player):
    for _ in range(3):
        player.draw()

    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        _revealed_cards = v.reveal(from_pile=v.deck, num=3, return_cards=True)
        other_human_players = [p for p in player.game.players if p is not v and p.human]
        for card in v.revealed_cards.copy():
            if c.action in card.types or c.treasure in card.types:
                if player.game.verbose:
                    player.game.output(v.name + " discards " + card.colored_name(), client=c.ALL)
                v.discard(from_pile=v.revealed_cards, card=card)
                _revealed_cards.remove(card)

        if len(_revealed_cards) == 1:
            if player.game.verbose:
                player.game.output(v.name + " puts a card on top of their deck", client=other_human_players)
                if player.game.multiplayer():
                    player.game.output("You put " + _revealed_cards[0].colored_name() + "on top of your deck", client=v)
            v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=_revealed_cards[0])
        elif len(_revealed_cards) > 1:
            if v.human:
                if player.game.verbose:
                    player.game.output("Cards:", client=v)
                    for card in _revealed_cards:
                        player.game.output("  " + card.colored_name(), client=v)
                while True:
                    order_str = player.game.input("Select the order the revealed cards should appear on top of the "
                                                  "deck (card names, separate with comma):", client=v)
                    try:
                        order_list = txf.get_cards(order_str, v.revealed_cards)
                        if order_list is None:
                            player.game.output("Invalid input", client=v)
                            order_list = []
                            continue
                        elif len(order_list) < len(_revealed_cards):
                            player.game.output("Please include all cards", client=v)
                            order_list = []
                            continue
                        break
                    except Exception as e:
                        handle_exception(e)
                        player.game.output("Invalid input", client=v)
                        order_list = []
                        continue

            else:
                order_list = v.revealed_cards
                np.random.shuffle(order_list)

            for card in order_list[::-1]:
                if player.game.verbose:
                    player.game.output(v.name + " places a card back onto their deck", client=other_human_players)
                    if player.game.multiplayer():
                        player.game.output("You place " + card.colored_name() + " back onto the deck", client=v)
                v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=card)

    return True


def royal_seal_card(player):
    player.coins += 2
    player.effects[c.royal_seal] = c.effect_dict[c.royal_seal].copy()

    return True


def vault_card(player):
    for _ in range(2):
        player.draw()

    discard_list = []
    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
            discard_cards_str = player.game.input("Select cards to discard "
                                                  "(card names, separate with comma, \"x\" for none):")
            if discard_cards_str == "x":
                break
            try:
                discard_list = txf.get_cards(discard_cards_str, player.hand)
                if discard_list is None:
                    player.game.output("Invalid input")
                    discard_list = []
                    continue
                for card in discard_list:
                    player.game.output(card.colored_name())
                if not confirm_card(player, "The listed cards will be discarded (y/n):"):
                    return False
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                discard_list = []
                continue
    else:
        for card in player.hand:
            if np.random.random() > 0.5:
                discard_list.append(card)

    for card in discard_list:
        player.discard(player.hand, card, mute=False)

    player.coins += len(discard_list)

    for p in [_p for _p in player.game.players if _p is not player]:
        discard_list = []
        if p.human:
            if player.game.verbose:
                p.print_hand()
            while True:
                discard_cards_str = player.game.input("You may discard two cards to draw a new card "
                                                      "(card names, separate with comma, \"x\" for none):", client=p)
                if discard_cards_str == "x":
                    break
                try:
                    discard_list = txf.get_cards(discard_cards_str, p.hand)
                    if discard_list is None:
                        player.game.output("Invalid input", client=p)
                        discard_list = []
                        continue
                    if len(discard_list) != 2:
                        player.game.output("You have to select two cards to discard", client=p)
                        discard_list = []
                        continue
                    for card in discard_list:
                        player.game.output(card.colored_name(), client=p)
                    if not confirm_card(p, "The listed cards will be discarded (y/n):"):
                        continue
                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input", client=p)
                    discard_list = []
                    continue
        else:
            if np.random.random() > 0.5:
                while len(discard_list) < 2:
                    discard_list.append(np.random.choice(p.hand))

        if len(discard_list) == 2:
            for card in discard_list:
                p.discard(from_pile=p.hand, card=card, mute=False)
            p.draw()

    return True


def venture_card(player):
    player.coins += 1

    revealed_cards = []
    while not any([c.treasure in card.types for card in revealed_cards])\
            and len(player.deck) + len(player.discard_pile) > 0:
        revealed_cards.append(player.reveal(from_pile=player.deck, return_cards=True)[0])

    if len(revealed_cards) == 0:
        return True

    t_card = revealed_cards[-1] if c.treasure in revealed_cards[-1].types else None
    if t_card:
        revealed_cards.pop()

    for card in revealed_cards:
        player.discard(player.revealed_cards, card, mute=False)

    t_card.play(player, action=False, discard=False)
    player.move(from_pile=player.revealed_cards, to_pile=player.active_cards, card=t_card)

    return True


def goons_card(player):
    player.buys += 1
    player.coins += 2

    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        num = 0
        while len(v.hand) > 3:
            discard_list = []
            if v.human:
                if player.game.verbose:
                    v.print_hand()
                    player.game.output("Discard down to 3 cards (card names, separate with comma):", client=v)
                discard_cards_str = player.game.input(client=v)
                try:
                    discard_list = txf.get_cards(discard_cards_str, v.hand)
                    if discard_list is None:
                        player.game.output("Invalid input", client=v)
                        continue

                    if len(v.hand) - len(discard_list) != 3:
                        continue
                    for card in discard_list:
                        player.game.output(card.colored_name(), client=v)
                    if not confirm_card(v, "The listed cards will be discarded (y/n):"):
                        continue
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input", client=v)
                    continue
            else:
                tmp_hand = v.hand.copy()
                while len(v.hand) - len(discard_list) > 3:
                    discard_card = np.random.choice(tmp_hand)
                    discard_list.append(discard_card)
                    del tmp_hand[tmp_hand.index(discard_card)]

            for card in discard_list:
                v.discard(v.hand, card)
                num += 1

            if player.game.verbose:
                player.game.output(v.name + " discards " + str(num) + " cards", client=c.ALL)

    if c.goons in player.effects:
        player.effects[c.goons][c.number] += 1
    else:
        player.effects[c.goons] = c.effect_dict[c.goons].copy()

    return True


def grand_market_card(player):
    player.draw()
    player.actions += 1
    player.buys += 1
    player.coins += 2

    return True


def hoard_card(player):
    player.coins += 2

    if c.hoard in player.effects:
        player.effects[c.hoard][c.number] += 1
    else:
        player.effects[c.hoard] = c.effect_dict[c.hoard].copy()

    return True


def bank_card(player):
    player.coins += [c.treasure in card.types for card in player.active_cards].count(True)

    return True


def expand_card(player):
    if len(player.hand) == 0:
        return True

    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
            expand_card_str = player.game.input("Select a card to expand (card name):")
            try:
                _expand_card = txf.get_card(expand_card_str, player.hand)
                if _expand_card is None:
                    player.game.output("Invalid input")
                    continue

                if _expand_card.get_cost(player, default=True) < 0:
                    continue

                if not confirm_card(player, _expand_card.colored_name() + " will be trashed (y/n):"):
                    return False

                gain_coins = _expand_card.get_cost(player, default=True) + 3
                if player.game.verbose:
                    player.game.output(player.game.supply.__str__())
                gain_card_str = player.game.input("Select a card to gain costing up to " +
                                                  txf.coins(gain_coins, plain=True) + " (card name):")
                gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                                  if 0 <= pile.get_cost(player, mute=True) <= gain_coins and pile.number > 0]
                gain_pile = txf.get_card(gain_card_str, gainable_cards)
                if gain_pile is None:
                    player.game.output("Invalid input")
                    continue
                player.trash(player.hand, _expand_card)
                player.gain(gain_pile)
                break

            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                continue
    else:
        if len(player.hand) > 0:
            _expand_card = np.random.choice(player.hand)
            gain_coins = _expand_card.get_cost(player, default=True) + 3
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if 0 <= pile.get_cost(player, mute=True) <= gain_coins and pile.number > 0]
            if len(gainable_cards) > 0:
                gain_pile = np.random.choice(gainable_cards)
                player.trash(player.hand, _expand_card)
                player.gain(gain_pile)

    return True


def forge_card(player):
    trash_list = []
    if player.human:
        if player.game.verbose:
            player.print_hand()
        while True:
            trash_cards_str = player.game.input("Select any number of cards to trash "
                                                "(card names, separate with comma, \"x\" for none):")
            try:
                if trash_cards_str == "x":
                    break

                trash_list = txf.get_cards(trash_cards_str, player.hand)
                if trash_list is None:
                    player.game.output("Invalid input")
                    trash_list = []
                    continue

                for card in trash_list:
                    player.game.output(card.colored_name())
                if not confirm_card(player, "The listed cards will be trashed (y/n):"):
                    return False
                break
            except Exception as e:
                handle_exception(e)
                player.game.output("Invalid input")
                trash_list = []
                continue
    else:
        for card in player.hand:
            if np.random.random() > 0.5:
                trash_list.append(card)

    gain_coins = 0
    for card in trash_list:
        gain_coins += card.get_cost(player, default=True)
        player.trash(player.hand, card)

    gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                      if pile.get_cost(player, mute=True) == gain_coins and pile.number > 0]
    if player.human:
        if len(gainable_cards) == 0:
            if player.game.verbose:
                player.game.output("The supply contains no cards costing " + txf.coins(gain_coins, plain=True) + ".",
                                   client=c.ALL)
                if not confirm_card(player, "Do you still want to trash the listed cards (y/n)?"):
                    return False

                return True

        if player.game.verbose:
            player.game.output(player.game.supply.__str__())
        while True:
            gain_card_str = player.game.input("Select a card to gain costing exactly " +
                                              txf.coins(gain_coins, plain=True) + " (card name, \"x\" to cancel):")
            if gain_card_str == "x":
                return False
            gain_pile = txf.get_card(gain_card_str, gainable_cards)
            if gain_pile is None:
                player.game.output("Invalid input")
                continue
            player.gain(gain_pile)
            break
    else:
        player.gain(np.random.choice(gainable_cards))

    return True


def kings_court_card(player):
    no_action_cards = True
    for card in player.hand:
        if c.action in card.types:
            no_action_cards = False
            break

    if no_action_cards:
        if player.game.verbose:
            player.game.output(player.name + " has no action cards to play", client=c.ALL)
    else:
        if player.human:
            if player.game.verbose:
                player.print_hand()
            while True:
                card_str = player.game.input("Select action card to play three times (card name):")
                try:
                    kings_courted_card = txf.get_card(card_str, player.hand)

                    if kings_courted_card is None:
                        player.game.output("Invalid input")
                        continue

                    if c.action not in kings_courted_card.types:
                        player.game.output(kings_courted_card.colored_name() + " is not an action card")
                        continue

                    if not confirm_card(player, "Play " + kings_courted_card.colored_name() + " (y/n)?"):
                        continue

                    for _ in range(3):
                        if player.game.verbose:
                            player.game.output(player.name + " plays " + kings_courted_card.colored_name(),
                                               client=c.ALL)
                        success = kings_courted_card.play(player, action=False, mute=True)
                        if not success:
                            return False

                    break
                except Exception as e:
                    handle_exception(e)
                    player.game.output("Invalid input")
                    continue
        else:
            eligible_cards = [card for card in player.hand if c.action in card.types]
            kings_courted_card = np.random.choice(eligible_cards)
            for _ in range(3):
                if player.game.verbose:
                    player.game.output(player.name + " plays " + kings_courted_card.colored_name(), client=c.ALL)
                success = kings_courted_card.play(player, action=False, mute=True)
                if not success:
                    return False

    return True


def peddler_card(player):
    player.draw()
    player.actions += 1
    player.coins += 1

    return True


def copper_card(player):
    player.coins += 1

    return True


def silver_card(player):
    player.coins += 2
    if c.merchant in player.effects:
        player.coins += player.effects[c.merchant][c.number]
        del player.effects[c.merchant]

    return True


def gold_card(player):
    player.coins += 3

    return True


def platinum_card(player):
    player.coins += 5

    return True


def estate_card(player):
    player.victory_points += 1

    return True


def duchy_card(player):
    player.victory_points += 3

    return True


def province_card(player):
    player.victory_points += 6

    return True


def colony_card(player):
    player.victory_points += 10

    return True


def curse_card(player):
    player.victory_points -= 1

    return True


# def test_card(player):
#     for card in player.hand:
#         if c.action in card.types:
#             player.actions += 1
#
#     for p in player.game.players:
#         p.draw()
