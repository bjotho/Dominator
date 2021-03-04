import constants as c


def grand_market_cost(player=None, printing=False, default=False, mute=False):
    if printing:
        return "6*"

    if player is None or default:
        return 6

    coppers_in_play = any([card.name == c.copper for card in player.active_cards])
    if player.game.verbose and coppers_in_play and not mute:
        player.game.output("You can't buy Grand Market because you have Copper cards in play.")

    if not coppers_in_play:
        return 6
    else:
        return -1


def peddler_cost(player=None, printing=False, default=False, mute=False):
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
