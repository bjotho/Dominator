import numpy as np
import constants as c
import text_formatting as txf


def confirm_card(confirmation_str, mute_n=False):
    while True:
        confirmation = input(confirmation_str)
        if confirmation not in ["", "y", "n"]:
            print("Please type \"y\" or \"n\"")
            continue
        if confirmation == "n":
            if not mute_n:
                print("Aborted")
            return False
        return True


# Base game cards

def cellar_card(player):
    if len(player.hand) == 0:
        player.actions += 1
        return True

    discard_list = []
    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
            discard_cards_str = input("Select cards to discard (card names, separate with comma):")
            try:
                discard_list = txf.get_cards(discard_cards_str, player.hand)
                if discard_list is None:
                    print("Invalid input")
                    discard_list = []
                    continue
                for card in discard_list:
                    print(card.colored_name())
                if not confirm_card("The listed cards will be discarded (y/n):"):
                    return False
                break
            except:
                print("Invalid input")
                discard_list = []
                continue
    else:
        for card in player.hand:
            if np.random.random() > 0.5:
                discard_list.append(card)

    for card in discard_list:
        player.discard(player.hand, card)

    for _ in range(len(discard_list)):
        player.draw()

    player.actions += 1

    return True


def chapel_card(player):
    if len(player.hand) == 0:
        return True

    trash_list = []
    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
            trash_cards_str = input("Select up to 4 cards to trash (card names, separate with comma):")
            try:
                trash_list = txf.get_cards(trash_cards_str, player.hand)
                if trash_list is None:
                    print("Invalid input")
                    trash_list = []
                    continue

                if len(trash_list) > 4:
                    if player.game.verbose:
                        print("You can only trash up to 4 cards")
                    trash_list = []
                    continue
                for card in trash_list:
                    print(card.colored_name())
                if not confirm_card("The listed cards will be trashed (y/n):"):
                    return False
                break
            except:
                print("Invalid input")
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
        if confirm_card("Discard deck (y/n)?", mute_n=True):
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
            print(player.name + "\'s discard pile is empty")
        return True

    if player.human:
        player.print_discard_pile()
        while True:
            deck_card = input("Put a card from the discard pile on top of your deck? (card name, \"x\" for none):")
            if deck_card == "x":
                print("No card moved")
                return True
            if len(deck_card) < 1:
                print("Invalid input")
                continue
            deck_card = txf.get_card(deck_card, player.discard_pile)
            if not confirm_card("Move " + deck_card.colored_name() + " to top of deck (y/n)?"):
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
    player.effects.append(c.merchant)

    return True


def vassal_card(player):
    player.coins += 2
    card = player.draw(return_card=True, to_pile=player.discard_pile)
    if player.game.verbose:
        print(player.name + " discards " + card.colored_name())
    if c.action in card.types:
        if player.human:
            if confirm_card("Play " + card.colored_name() + " (y/n)?"):
                success = card.play(player, action=False, discard=False)
                if success:
                    player.move(from_pile=player.discard_pile, to_pile=player.active_cards, card=card)
        else:
            success = card.play(player, action=False, discard=False)
            if success:
                player.move(from_pile=player.discard_pile, to_pile=player.active_cards, card=card)

    return True


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
            print(player.game.supply)
        while True:
            gain_card = input("Select a card to gain costing up to " + txf.coins(4, plain=True) + " (card name):")
            if len(gain_card) < 1:
                print("Invalid input")
                continue
            gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 4
                              and pile.number > 0]
            gain_pile = txf.get_card(gain_card, gainable_cards)
            if gain_pile is None:
                print("Invalid input")
                continue
            player.gain(gain_pile)
            break
    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 4
                          and pile.number > 0]
        if len(gainable_cards) > 0:
            gain_pile = np.random.choice(gainable_cards)
            player.gain(gain_pile)

    return True


def bureaucrat_card(player):
    player.gain(player.game.supply.piles[c.silver], to_pile=player.deck, mute=True)
    if player.game.verbose:
        print(player.name + " gains " + txf.treasure(c.silver) + " and puts it on top of their deck")

    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        victory_cards = [card for card in v.hand if c.victory in card.types]
        if len(victory_cards) <= 0:
            v.reveal_hand()
        elif len(victory_cards) == 1:
            v.reveal(v.hand, victory_cards[0])
            v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=victory_cards[0])
            if player.game.verbose:
                print("... And puts it on top of their deck")
        else:
            if v.human:
                if player.game.verbose:
                    print("Victory cards:")
                for card in victory_cards:
                    if player.game.verbose:
                        if player.game.verbose >= 2:
                            print(card)
                        else:
                            print("  " + card.colored_name())
                while True:
                    reveal_card_str = input("Select victory card to reveal (card name):")
                    try:
                        reveal_card = txf.get_card(reveal_card_str, victory_cards)
                        if reveal_card is None:
                            print("Invalid input")
                            continue
                        v.reveal(v.hand, reveal_card)
                        v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=reveal_card)
                        if player.game.verbose:
                            print("... And puts it on top of their deck")
                        break
                    except:
                        print("Invalid input")
                        continue
            else:
                reveal_card = np.random.choice(victory_cards)
                v.reveal(v.hand, reveal_card)
                v.move(from_pile=v.revealed_cards, to_pile=v.deck, card=reveal_card)
                if player.game.verbose:
                    print("... And puts it on top of their deck")

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
            print(player.game.supply)
        while True:
            gain_card_str = input("Select a card to gain costing up to " + txf.coins(5, plain=True) + " (card name):")
            if len(gain_card_str) < 1:
                print("Invalid input")
                continue
            gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 5
                              and pile.number > 0]
            gain_pile = txf.get_card(gain_card_str, gainable_cards)
            if gain_pile is None:
                print("Invalid input")
                continue
            player.gain(gain_pile)
            break
    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 5
                          and pile.number > 0]
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
                    print("Discard down to 3 cards (card names, separate with comma):")
                discard_cards_str = input()
                try:
                    discard_list = txf.get_cards(discard_cards_str, v.hand)
                    if discard_list is None:
                        print("Invalid input")
                        continue

                    if len(v.hand) - len(discard_list) != 3:
                        continue
                    for card in discard_list:
                        print(card.colored_name())
                    if not confirm_card("The listed cards will be discarded (y/n):"):
                        continue
                except:
                    print("Invalid input")
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
                print(v.name + " discards " + str(num) + " cards")

    return True


def moneylender_card(player):
    copper_card = None
    for card in player.hand:
        if card.name == c.copper:
            copper_card = card

    if not copper_card:
        if player.game.verbose:
            print(player.name + " does not have any Copper cards")
        return True
    else:
        if player.human:
            player.print_hand()
            if not confirm_card("Trash " + copper_card.name + " (y/n)?"):
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
                    print("Select " + str(empty_piles) + " cards to discard (card names):")
                discard_cards_str = input()
                try:
                    discard_list = txf.get_cards(discard_cards_str, player.hand)
                    if discard_list is None:
                        print("Invalid input")
                        discard_list = []
                        continue

                    assert len(discard_list) == empty_piles
                    for card in discard_list:
                        print(card.colored_name())
                    if not confirm_card("The listed cards will be discarded (y/n):"):
                        return False

                    break
                except:
                    print("Invalid input")
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
                print("Select a card to remodel (card name):")
            remodel_card_str = input()
            try:
                _remodel_card = txf.get_card(remodel_card_str, player.hand)
                if _remodel_card is None:
                    print("Invalid input")
                    continue

                if not confirm_card(_remodel_card.colored_name() + " will be trashed (y/n):"):
                    return False

                gain_coins = _remodel_card.cost + 2
                if player.game.verbose:
                    print(player.game.supply)
                    print("Select a card to gain costing up to " + txf.coins(gain_coins, plain=True) + " (card name):")
                gain_card_str = input()

                if len(gain_card_str) < 1:
                    print("Invalid input")
                    continue
                gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                                  if pile.cost <= gain_coins and pile.number > 0]
                gain_pile = txf.get_card(gain_card_str, gainable_cards)
                if gain_pile is None:
                    print("Invalid input")
                    continue
                player.trash(player.hand, _remodel_card)
                player.gain(gain_pile)
                break

            except:
                print("Invalid input")
                continue
    else:
        if len(player.hand) > 0:
            _remodel_card = np.random.choice(player.hand)
            gain_coins = _remodel_card.cost + 2
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if pile.cost <= gain_coins and pile.number > 0]
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
        p.reveal(p.revealed_cards, _reveal_card, move=False)
        if player.human:
            if confirm_card("Put back on deck (y) or discard (n)?:", mute_n=True):
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " put back on deck")
                p.move(from_pile=p.revealed_cards, to_pile=p.deck, card=_reveal_card)
            else:
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " discarded")
                p.discard(p.revealed_cards, _reveal_card)
        else:
            if np.random.random() > 0.5:
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " discarded")
                p.discard(p.revealed_cards, _reveal_card)
            else:
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " put back on deck")
                p.move(from_pile=p.revealed_cards, to_pile=p.deck, card=_reveal_card)

    return True


def thief_card(player):
    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        for _ in range(2):
            v.draw(mute=True, to_pile=v.revealed_cards)
        v.reveal(v.revealed_cards, v.revealed_cards, move=False)
        eligible_cards = [card for card in v.revealed_cards if c.treasure in card.types]
        trash_card = None
        if len(eligible_cards) <= 0:
            continue
        elif len(eligible_cards) == 1:
            trash_card = eligible_cards[0]
            v.trash(v.revealed_cards, trash_card)
        else:
            if v.human:
                while True:
                    trash_card_str = input("Select card to trash (card name):")
                    try:
                        trash_card = txf.get_card(trash_card_str, eligible_cards)
                        if trash_card is None:
                            print("Invalid input")
                            continue
                        v.trash(v.revealed_cards, trash_card)
                        break
                    except:
                        print("Invalid input")
                        continue
            else:
                trash_card = np.random.choice(eligible_cards)
                v.trash(v.revealed_cards, trash_card)

        if player.human:
            if confirm_card("Gain " + trash_card.colored_name() + " (y/n)?", mute_n=True):
                if player.game.verbose:
                    print(player.name + " gains " + trash_card.colored_name())
                player.move(from_pile=player.game.trash[::-1], to_pile=player.discard_pile, card=trash_card)
        else:
            if np.random.random() > 0.5:
                if player.game.verbose:
                    print(player.name + " gains " + trash_card.colored_name())
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
            print(player.name + " has no action cards to play")
    else:
        if player.human:
            if player.game.verbose:
                player.print_hand()
            while True:
                card_str = input("Select action card to play twice (card name):")
                try:
                    throned_card = txf.get_card(card_str, player.hand)

                    if throned_card is None:
                        print("Invalid input")
                        continue

                    if c.action not in throned_card.types:
                        print(throned_card.colored_name() + " is not an action card")
                        continue

                    if not confirm_card("Play " + throned_card.colored_name() + " (y/n)?"):
                        continue

                    for _ in range(2):
                        if player.game.verbose:
                            print(player.name + " plays " + throned_card.colored_name())
                        throned_card.play(player, action=False)

                    break
                except:
                    print("Invalid input")
                    continue
        else:
            eligible_cards = [card for card in player.hand if c.action in card.types]
            throned_card = np.random.choice(eligible_cards)
            for _ in range(2):
                throned_card.play(player, action=False)

    return True


def bandit_card(player):
    player.gain(player.game.supply.piles[c.gold])
    victims = [v for v in player.game.players if c.moat not in v.effects and v is not player]
    for v in victims:
        for _ in range(2):
            v.draw(mute=True, to_pile=v.revealed_cards)
        v.reveal(v.revealed_cards, v.revealed_cards, move=False)
        eligible_cards = [card for card in v.revealed_cards if (c.treasure in card.types) and (card.name != c.copper)]
        trash_card = None
        if len(eligible_cards) <= 0:
            continue
        elif len(eligible_cards) == 1:
            trash_card = eligible_cards[0]
            v.trash(v.revealed_cards, trash_card)
        else:
            if v.human:
                while True:
                    trash_card_str = input("Select card to trash (card name):")
                    try:
                        trash_card = txf.get_card(trash_card_str, eligible_cards)
                        if trash_card is None:
                            print("Invalid input")
                            continue
                        v.trash(v.revealed_cards, trash_card)
                        break
                    except:
                        print("Invalid input")
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
                if confirm_card("Set aside " + card.colored_name() + " (y/n)?", mute_n=True):
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
            print(player.name + " does not have any treasure cards")
        return True

    if player.human:
        while True:
            if player.game.verbose:
                player.print_hand()
                print("Select a treasure card to trash (card name, \"x\" for none):")
            mine_card_str = input()
            if mine_card_str == "x":
                if player.game.verbose:
                    print("No cards trashed")
                return True
            try:
                _mine_card = txf.get_card(mine_card_str, player.hand)
                if _mine_card is None or c.treasure not in _mine_card.types:
                    print("Invalid input")
                    continue

                if not confirm_card(_mine_card.colored_name() + " will be trashed (y/n):"):
                    return False

                gain_coins = _mine_card.cost + 3
                if player.game.verbose:
                    print(player.game.supply)
                    print("Select a treasure card to gain costing up to " + txf.coins(gain_coins, plain=True) + " (card name):")
                gain_card_str = input()

                if len(gain_card_str) < 1:
                    print("Invalid input")
                    continue
                gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                                  if pile.cost <= gain_coins and pile.number > 0
                                  and c.treasure in pile.types]
                gain_pile = txf.get_card(gain_card_str, gainable_cards)
                if gain_pile is None:
                    print("Invalid input")
                    continue
                player.trash(player.hand, _mine_card)
                if player.game.verbose:
                    print(player.name + " gains " + gain_pile.colored_name() + " to their hand")
                player.gain(gain_pile, to_pile=player.hand, mute=True)
                break

            except:
                print("Invalid input")
                continue
    else:
        if len(player.hand) > 0:
            _mine_card = np.random.choice(treasure_cards)
            gain_coins = _mine_card.cost + 3
            gainable_cards = [pile for pile in list(player.game.supply.piles.values())
                              if pile.cost <= gain_coins and pile.number > 0
                              and c.treasure in pile.types]
            if len(gainable_cards) > 0:
                gain_pile = np.random.choice(gainable_cards)
                player.trash(player.hand, _mine_card)
                player.gain(gain_pile, to_pile=player.hand, mute=True)
                if player.game.verbose:
                    print(player.name + " gains " + gain_pile.colored_name() + " to their hand")

    return True


def sentry_card(player):
    player.draw()
    player.actions += 1
    for _ in range(2):
        _card = player.draw(to_pile=player.set_aside_cards, mute=True, return_card=True)
        if player.game.verbose:
            print(player.name + " sets aside " + _card.colored_name())

    if player.human:
        if player.game.verbose:
            print("Cards:")
            for card in player.set_aside_cards:
                print("  " + card.colored_name())
        while True:
            trash_cards_str = input("Select cards to trash (card names, separate with comma, \"x\" for none):")
            if trash_cards_str == "x":
                if player.game.verbose:
                    print("No cards trashed")
                break
            try:
                trash_list = txf.get_cards(trash_cards_str, player.set_aside_cards)
                if trash_list is None:
                    print("Invalid input")
                    continue
                for card in trash_list:
                    print(card.colored_name())
                if not confirm_card("The listed cards will be trashed (y/n):"):
                    return False
                for card in trash_list:
                    player.trash(player.set_aside_cards, card)
                break
            except:
                print("Invalid input")
                continue

        if len(player.set_aside_cards) > 0:
            if len(player.set_aside_cards) > 1:
                if player.game.verbose:
                    print("Cards:")
                    for card in player.set_aside_cards:
                        print("  " + card.colored_name())
                while True:
                    discard_cards_str = input("Select cards to discard "
                                              "(card names, separate with comma, \"x\" for none):")
                    if discard_cards_str == "x":
                        if player.game.verbose:
                            print("No cards discarded")
                        break
                    try:
                        discard_list = txf.get_cards(discard_cards_str, player.set_aside_cards)
                        if discard_list is None:
                            print("Invalid input")
                            continue
                        for card in discard_list:
                            print(card.colored_name())
                        if not confirm_card("The listed cards will be discarded (y/n):"):
                            return False
                        for card in discard_list:
                            player.discard(player.set_aside_cards, card)
                        break
                    except:
                        print("Invalid input")
                        continue
            else:
                if confirm_card("Discard " + player.set_aside_cards[0].colored_name() + " (y/n)?", mute_n=True):
                    player.discard(player.set_aside_cards, player.set_aside_cards[0])

        if len(player.set_aside_cards) > 1:
            if player.game.verbose:
                print("Cards:")
                for card in player.set_aside_cards:
                    print("  " + card.colored_name())
            while True:
                top_deck_card_str = input("Select card to place on top of deck (card name):")
                try:
                    top_card, i = txf.get_card(top_deck_card_str, player.set_aside_cards, return_index=True)
                    if top_card is None:
                        print("Invalid input")
                        continue
                    if confirm_card(top_card.colored_name() + " will be placed on top of your deck (with "
                                    + player.set_aside_cards[1 - i].colored_name() + " directly beneath) (y/n):"):
                        player.move(from_pile=player.set_aside_cards, to_pile=player.deck,
                                    card=player.set_aside_cards[i - 1])
                        player.move(from_pile=player.set_aside_cards, to_pile=player.deck, card=top_card)
                    else:
                        return False
                    break
                except:
                    print("Invalid input")
                    continue
        elif len(player.set_aside_cards) == 1:
            if player.game.verbose:
                print(player.name + " puts " + player.set_aside_cards[0].colored_name() + " on top of their deck")
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
        _card = player.reveal(player.deck, return_cards=True)
        if c.treasure in _card.types:
            revealed_treasure_cards.append(_card)
            player.move(from_pile=player.revealed_cards, to_pile=player.hand, card=_card)

    for card in player.revealed_cards:
        player.discard(player.revealed_cards, card)

    return True


def artisan_card(player):
    if player.human:
        if player.game.verbose:
            print(player.game.supply)
        while True:
            gain_card_str = input("Select a card to gain costing up to " + txf.coins(5, plain=True) + " (card name):")
            if len(gain_card_str) < 1:
                print("Invalid input")
                continue
            gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 5
                              and pile.number > 0]
            gain_pile = txf.get_card(gain_card_str, gainable_cards)
            if gain_pile is None:
                print("Invalid input")
                continue
            player.gain(gain_pile)
            break

        if player.game.verbose:
            player.print_hand()
        while len(player.hand) > 0:
            deck_card_str = input("Put a card from your hand onto your deck (card name):")
            try:
                deck_card = txf.get_card(deck_card_str, player.hand)
                if deck_card is None:
                    print("Invalid input")
                    continue
                if not confirm_card("Put " + deck_card.colored_name() + " on top of deck (y/n)?"):
                    return False
                player.move(from_pile=player.hand, to_pile=player.deck, card=deck_card)
                break
            except:
                print("Invalid input")
                continue

    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 5
                          and pile.number > 0]
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
        revealed_card = player.reveal(from_pile=player.deck, return_cards=True)
        if c.treasure in revealed_card.types:
            if player.human:
                if confirm_card("Trash " + revealed_card.colored_name() + " (y/n)?"):
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
            trash_card_str = input("Select card to trash (card name):")
            try:
                trash_card = txf.get_card(input_str=trash_card_str, from_pile=player.hand)
                if trash_card is None:
                    print("Invalid input")
                    continue

                if not confirm_card(trash_card.colored_name() + " will be trashed (y/n):"):
                    return False
                break
            except:
                print("Invalid input")
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


# card_text = {
#     watchtower: "Draw until you have 6 cards in hand.\n" + hl + "\nWhen you gain a card, you may reveal this from your "
#         "hand, to either trash that card or put it onto your deck.",
#     bishop: txf.coins(1) + "\n" + txf.vt(1) + "\nTrash a card from your hand. " + txf.vt(1) + " per "
#         + txf.coins(2, plain=True) + " it costs (round down). Each other player may trash a card from their hand.",
#     monument: txf.coins(2) + "\n" + txf.vt(1),
# }


def copper_card(player):
    player.coins += 1

    return True


def silver_card(player):
    player.coins += 2
    if c.merchant in player.effects:
        player.coins += 1
        player.effects.remove(c.merchant)

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
