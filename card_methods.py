import numpy as np
import constants as c
import text_formatting as txf

# TODO: Implement method for each card


def confirm_card(confirmation_str, mute_n=False):
    while True:
        confirmation = input(confirmation_str)
        if confirmation not in ["y", "n"]:
            print("Please type \"y\" or \"n\"")
            continue
        if confirmation == "n":
            if not mute_n:
                print("Aborted")
            return False
        return True


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
                tmp_hand = player.hand.copy()
                for s in discard_cards_str.split(","):
                    i = 0
                    while tmp_hand[i].name.lower() != s.strip().lower():
                        i += 1

                    discard_list.append(tmp_hand[i])
                    del tmp_hand[i]

                for card in discard_list:
                    print(card.colored_name())
                if not confirm_card("The listed cards will be discarded (y/n):"):
                    discard_list.clear()
                    continue
                break
            except:
                print("Invalid input")
                discard_list.clear()
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
                tmp_hand = player.hand.copy()
                for s in trash_cards_str.split(","):
                    i = 0
                    while tmp_hand[i].name.lower() != s.strip().lower():
                        i += 1

                    trash_list.append(tmp_hand[i])
                    del tmp_hand[i]

                if len(trash_list) > 4:
                    if player.game.verbose:
                        print("You can only trash up to 4 cards")
                        trash_list.clear()
                        continue
                for card in trash_list:
                    print(card.colored_name())
                if not confirm_card("The listed cards will be trashed (y/n):"):
                    trash_list.clear()
                    continue
                break
            except:
                print("Invalid input")
                trash_list.clear()
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
            deck_card = deck_card[0].upper() + deck_card[1:].lower()
            discard_cards = [card.name for card in player.discard_pile]
            if deck_card not in discard_cards:
                print("Invalid input")
                continue
            outer_break = False
            for card in player.discard_pile:
                if card.name == deck_card:
                    if not confirm_card("Move " + card.colored_name() + " to top of deck (y/n)?"):
                        break
                    player.deck.append(card)
                    player.discard_pile.remove(card)
                    outer_break = True
                    break
            if outer_break:
                break
    else:
        if np.random.random() > 0.5 and len(player.discard_pile) > 0:
            card = np.random.choice(player.discard_pile)
            player.deck.append(card)
            player.discard_pile.remove(card)

    return True


def merchant_card(player):
    player.draw()
    player.actions += 1
    player.effects.append(c.merchant)

    return True


def vassal_card(player):
    player.coins += 2
    card = player.draw(return_card=True)
    player.discard(player.hand, card)
    if player.game.verbose:
        print(player.name + " discards " + card.colored_name())
    if c.action in card.types:
        if player.human:
            if confirm_card("Play " + card.colored_name() + " (y/n)?"):
                card.play(player, action=False, discard=False)
        else:
            card.play(player, action=False, discard=False)

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
            gain_card = gain_card[0].upper() + gain_card[1:].lower()
            gainable_cards = [pile.name for pile in list(player.game.supply.piles.values()) if pile.cost <= 4
                              and pile.number > 0]
            if gain_card not in gainable_cards:
                print("Invalid input")
                continue

        player.gain(player.game.supply.piles[gain_card])
    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 4
                          and pile.number > 0]
        if len(gainable_cards) > 0:
            gain_card = np.random.choice(gainable_cards)
            player.gain(gain_card)

    return True


def bureaucrat_card(player):
    player.gain(player.game.supply.piles[c.silver], to_pile=player.deck, mute=True)
    if player.game.verbose:
        print(player.name + " gains " + txf.treasure(c.silver) + " and puts it on top of their deck")

    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for victim in victims:
        victory_cards = [card for card in victim.hand if c.victory in card.types]
        if len(victory_cards) <= 0:
            victim.reveal_hand()
        elif len(victory_cards) == 1:
            victim.reveal(victory_cards[0])
            victim.deck.append(victory_cards[0])
            victim.hand.remove(victory_cards[0])
            if player.game.verbose:
                print("... And puts it on top of their deck")
        else:
            if victim.human:
                if player.game.verbose:
                    print("Victory cards:")
                for card in victory_cards:
                    if player.game.verbose:
                        if player.game.verbose >= 2:
                            print(card)
                        else:
                            print("  " + card.colored_name())

                reveal_card_str = ""
                while reveal_card_str not in [card.name for card in victory_cards]:
                    reveal_card_str = input("Select victory card to reveal (card name):")
                    try:
                        reveal_card_str = reveal_card_str[0].upper() + reveal_card_str[1:].lower()
                        reveal_card = None
                        for card in victory_cards:
                            if card.name == reveal_card_str:
                                reveal_card = card
                                break

                        if not reveal_card:
                            print("Invalid input")
                            continue
                        victim.reveal(reveal_card)
                        victim.deck.append(reveal_card)
                        victim.hand.remove(reveal_card)
                        if player.game.verbose:
                            print("... And puts it on top of their deck")
                    except:
                        print("Invalid input")
                        continue
            else:
                reveal_card = np.random.choice(victory_cards)
                victim.reveal(reveal_card)
                victim.deck.append(reveal_card)
                victim.hand.remove(reveal_card)
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
        while True:
            if player.game.verbose:
                print(player.game.supply)
            gain_card = input("Select a card to gain costing up to " + txf.coins(5, plain=True) + " (card name):")
            if len(gain_card) < 1:
                print("Invalid input")
                continue
            gain_card = gain_card[0].upper() + gain_card[1:].lower()
            gainable_cards = [pile.name for pile in list(player.game.supply.piles.values()) if pile.cost <= 5
                              and pile.number > 0]
            if gain_card not in gainable_cards:
                print("Invalid input")
                continue
            player.gain(player.game.supply.piles[gain_card])
            break
    else:
        gainable_cards = [pile for pile in list(player.game.supply.piles.values()) if pile.cost <= 5
                          and pile.number > 0]
        if len(gainable_cards) > 0:
            gain_card = np.random.choice(gainable_cards)
            player.gain(gain_card)

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
                    tmp_hand = v.hand.copy()
                    for s in discard_cards_str.split(","):
                        i = 0
                        while tmp_hand[i].name.lower() != s.strip().lower():
                            i += 1

                        discard_list.append(tmp_hand[i])
                        del tmp_hand[i]

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
                    tmp_hand = player.hand.copy()
                    for s in discard_cards_str.split(","):
                        i = 0
                        while tmp_hand[i].name.lower() != s.strip().lower():
                            i += 1

                        discard_list.append(tmp_hand[i])
                        del tmp_hand[i]

                    assert len(discard_list) == empty_piles
                    for card in discard_list:
                        print(card.colored_name())
                    if not confirm_card("The listed cards will be discarded (y/n):"):
                        return False

                    break
                except:
                    print("Invalid input")
                    discard_list.clear()
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
                remodel_card_str = remodel_card_str[0].upper() + remodel_card_str[1:].lower()
                _remodel_card = None
                for card in player.hand:
                    if card.name == remodel_card_str:
                        _remodel_card = card
                        break

                if not _remodel_card:
                    if player.game.verbose:
                        print("Invalid input")
                    continue

                if not confirm_card(_remodel_card.colored_name() + " will be trashed (y/n):"):
                    continue

                gain_coins = _remodel_card.cost + 2
                if player.game.verbose:
                    print(player.game.supply)
                    print("Select a card to gain costing up to " + txf.coins(gain_coins, plain=True) + " (card name):")
                gain_card_str = input()

                if len(gain_card_str) < 1:
                    print("Invalid input")
                    continue
                gain_card_str = gain_card_str[0].upper() + gain_card_str[1:].lower()
                gainable_cards = [pile.name for pile in list(player.game.supply.piles.values())
                                  if pile.cost <= gain_coins and pile.number > 0]
                if gain_card_str not in gainable_cards:
                    print("Invalid input")
                    continue
                player.trash(player.hand, _remodel_card)
                player.gain(player.game.supply.piles[gain_card_str])
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
                gain_card = np.random.choice(gainable_cards)
                player.trash(player.hand, _remodel_card)
                player.gain(gain_card)

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
        _reveal_card = p.draw(mute=True, return_card=True, to_pile=p.set_aside_cards)
        p.reveal(_reveal_card)
        if player.human:
            if confirm_card("Put back on deck (y) or discard (n)?:", mute_n=True):
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " put back on deck")
                p.deck.append(_reveal_card)
                p.set_aside_cards.pop()
            else:
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " discarded")
                p.discard(p.set_aside_cards, _reveal_card)
        else:
            if np.random.random() > 0.5:
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " discarded")
                p.discard(p.set_aside_cards, _reveal_card)
            else:
                if player.game.verbose:
                    print(_reveal_card.colored_name() + " put back on deck")
                p.deck.append(_reveal_card)
                p.set_aside_cards.pop()

    return True


def thief_card(player):
    victims = [p for p in player.game.players if (c.moat not in p.effects) and (p is not player)]
    for v in victims:
        for _ in range(2):
            v.draw(mute=True, to_pile=v.set_aside_cards)
        v.reveal(v.set_aside_cards)
        eligible_cards = [card for card in v.set_aside_cards if c.treasure in card.types]
        trash_card = None
        if len(eligible_cards) <= 0:
            continue
        elif len(eligible_cards) == 1:
            trash_card = eligible_cards[0]
            v.trash(v.set_aside_cards, trash_card)
        else:
            if v.human:
                while True:
                    trash_card_str = input("Select card to trash (card name):")
                    try:
                        trash_card_str = trash_card_str[0].upper() + trash_card_str[1:].lower()
                        for card in eligible_cards:
                            if card.name == trash_card_str:
                                trash_card = card
                                break
                        assert trash_card in eligible_cards
                        v.trash(v.set_aside_cards, trash_card)
                        break
                    except:
                        if player.game.verbose:
                            print("Invalid input")
                            continue
            else:
                trash_card = np.random.choice(eligible_cards)
                v.trash(v.set_aside_cards, trash_card)

        if player.human:
            if confirm_card("Gain " + trash_card.colored_name() + " (y/n)?", mute_n=True):
                if player.game.verbose:
                    print(player.name + " gains " + trash_card.colored_name())
                player.discard_pile.append(trash_card)
                player.game.trash[::-1].remove(trash_card)
        else:
            if np.random.random() > 0.5:
                if player.game.verbose:
                    print(player.name + " gains " + trash_card.colored_name())
                player.discard_pile.append(trash_card)
                player.game.trash[::-1].remove(trash_card)

    for v in victims:
        for card in v.set_aside_cards:
            v.discard(v.set_aside_cards, card)

    return True

# card_text = {
#     throne_room: "You may play an Action card from your hand twice.",
#     bandit: "Gain a Gold. Each other player reveals the top 2 cards of their deck, trashes a revealed Treasure other "
#         "than Copper, and discards the rest.",
#     council_room: txf.bold("+4 Cards") + "\n" + txf.bold("+1 Buy") + "\nEach other player draws a card.",
#     festival: txf.bold("+2 Actions") + "\n" + txf.bold("+1 Buy") + "\n" + txf.coins(2),
#     laboratory: txf.bold("+2 Cards") + "\n" + txf.bold("+1 Action"),
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


def platina_card(player):
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
