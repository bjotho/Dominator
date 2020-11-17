import constants as c


def grand_market_cost(player=None, printing=False, default=False):
    if printing:
        return "6*"

    if player is None or default:
        return 6

    coppers_in_play = False
    for card in player.active_cards:
        if card.name == c.copper:
            if player.game.verbose:
                print("You can't buy this card since you have Copper cards in play.")
            coppers_in_play = True

    if not coppers_in_play:
        return 6
    else:
        return -1


def peddler_cost(player=None, printing=False, default=False):
    if printing:
        return "8*"

    if player is None or default:
        return 8

    action_cards_in_play = 0
    for card in player.active_cards:
        if c.action in card.types:
            action_cards_in_play += 1

    cost = 8 - (2 * action_cards_in_play)

    return max(0, cost)
