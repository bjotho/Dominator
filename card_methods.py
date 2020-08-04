import numpy as np
import constants as c

# TODO: Implement method for each card


def confirm_card(confirmation_string, mute_n=False):
    while True:
        confirmation = input(confirmation_string)
        if confirmation not in ["y", "n"]:
            print("Please type \"y\" or \"n\"")
            continue
        if confirmation == "n":
            if not mute_n:
                print("Aborted")
            return False
        return True


def cellar_card(player):
    discard_list = []
    if player.human:
        if player.game.verbose:
            player.print_hand()
            print("Select cards to discard (card names, separate with comma):")
        discard_cards_str = input()
        try:
            tmp_hand = player.hand.copy()
            for s in discard_cards_str.split(","):
                i = 0
                while tmp_hand[i].name.lower() != s.strip().lower():
                    i += 1

                discard_list.append(tmp_hand[i])
                del tmp_hand[i]

            for card in discard_list:
                print(card.name)
            if not confirm_card("The listed cards will be discarded (y/n):"):
                return False
        except:
            print("Invalid card selection")
            return cellar_card(player)
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
    trash_list = []
    if player.human:
        if player.game.verbose:
            player.print_hand()
            print("Select cards to trash (card names, separate with comma):")
        trash_cards_str = input()
        try:
            tmp_hand = player.hand.copy()
            for s in trash_cards_str.split(","):
                i = 0
                while tmp_hand[i].name.lower() != s.strip().lower():
                    i += 1

                trash_list.append(tmp_hand[i])
                del tmp_hand[i]

            for card in trash_list:
                print(card.name)
            if not confirm_card("The listed cards will be trashed (y/n):"):
                return False
        except:
            print("Invalid card selection")
            return chapel_card(player)
    else:
        for card in player.hand:
            if np.random.random() > 0.5:
                trash_list.append(card)

    for card in trash_list:
        player.trash(player.hand, card)

    return True


def moat_card(player):
    for _ in range(2):
        player.draw()

    if player.game.verbose:
        player.print_hand()

    return True
# TODO: Complete reaction


def chancellor_card(player):
    player.coins += 2
    if confirm_card("Discard deck (y/n)?", mute_n=True):
        for card in player.deck:
            player.discard(player.deck, card)

    return True


def harbinger_card(player):
    player.draw()
    player.actions += 1
    player.print_discard_pile()
    deck_card = input("Put a card from the discard pile on top of your deck? (card name, \"x\" for none):")
    if deck_card == "x":
        print("No card moved")
        return True
    discard_cards = [card.name for card in player.discard_pile]
    if deck_card not in discard_cards:
        print("Invalid input")
        return harbinger_card(player)
    for card in player.discard_pile:
        if card.name == deck_card:
            if not confirm_card("Move " + card.name + " to top of deck (y/n)?"):
                return False
            player.deck.append(card)
            player.discard_pile.remove(card)
            break

    return True


def merchant_card(player):
    player.draw()
    player.actions += 1
    player.effects.append(c.merchant)

    return True


# card_text = {
#     moat: txf.bold("+2 Cards") + "\n" + hl + "\nWhen another player plays an Attack card, you may first reveal this "
#         "from your hand, to be unaffected by it.",
#
#     vassal: txf.coins(2) + "\nDiscard the top card of your deck. If it's an Action card, you may play it."
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
