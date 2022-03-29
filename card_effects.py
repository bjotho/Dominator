import constants as c
from card_methods import np, confirm_card


""" This file contains implementations of the side-effects of each card.
    Each card has it's own function with the card name followed by _effect"""


def trade_route_effect(game, pile):
    if c.trade_route in [_pile.name for _pile in list(game.supply.piles.values())]:
        if c.victory in pile.types:
            if pile.name not in game.trade_route_mat:
                game.trade_route_mat.append(pile.name)
                if game.verbose:
                    game.output(f"Coin token moved from {pile.colored_name()} pile to Trade Route mat", client=c.ALL)


def quarry_effect(player, pile, cost):
    active_card_names = [card.name for card in player.active_cards]
    if c.quarry in active_card_names:
        if c.action in pile.cards[-1].types:
            cost = max(0, cost - (2 * active_card_names.count(c.quarry)))

    return cost


def talisman_effect(player, pile, gained_card, cost, card_class):
    active_card_names = [card.name for card in player.active_cards]
    if c.talisman in active_card_names:
        if pile.number > 0:
            if c.victory not in gained_card.types and cost <= 4:
                for _ in range([card.name for card in player.active_cards].count(c.talisman)):
                    if pile.number > 0:
                        if player.game.verbose:
                            card_name = card_class(**c.card_list[c.talisman]).colored_name()
                            player.game.output(card_name + " grants you a copy of " + pile.colored_name())
                            if player.game.multiplayer():
                                player.game.output(card_name + " grants " + player.name + " a copy of " +
                                                   pile.colored_name(), client=c.OTHERS)
                        player.gain(pile, mute=True)
                    else:
                        if player.game.verbose:
                            card_name = card_class(**c.card_list[c.talisman]).colored_name()
                            player.game.output(card_name + " would have granted you a copy of " + pile.colored_name() +
                                               "; however, the pile is empty.")
                            if player.game.multiplayer():
                                player.game.output(card_name + " would have granted " + player.name + " a copy of " +
                                                   pile.colored_name() + "; however, the pile is empty.",
                                                   client=c.OTHERS)
        else:
            if player.game.verbose:
                card_name = card_class(**c.card_list[c.talisman]).colored_name()
                player.game.output(card_name + " would have granted you a copy of " + pile.colored_name() +
                                   ", however the pile is empty.")
                if player.game.multiplayer():
                    player.game.output(card_name + " would have granted " + player.name + " a copy of " +
                                       pile.colored_name() + ", however the pile is empty.", client=c.OTHERS)


def contraband_effect(player, pile):
    if c.contraband in player.effects:
        if pile.name in player.effects[c.contraband][c.contraband_cards]:
            player.game.output(pile.colored_name() + " pile blocked by Contraband", client=c.ALL)
            return False

    return True


def mint_effect(player):
    if not confirm_card(player, "Trash all active treasure cards (y/n)?"):
        return False
    for active_t_card in [card for card in player.active_cards if c.treasure in card.types]:
        player.trash(from_pile=player.active_cards, card=active_t_card)

    return True


def royal_seal_effect(player, card, to_pile=None):
    if not to_pile:
        to_pile = player.discard_pile

    if c.royal_seal in [card.name for card in player.active_cards] and to_pile is not player.deck:
        if player.human:
            if confirm_card(player, "Place " + card.colored_name() + " on top of deck (y/n)?", mute_n=True):
                player.game.output(player.name + " places " + card.colored_name() + " on top of their deck",
                                   client=c.ALL)
                to_pile = player.deck
        else:
            if np.random.random() > 0.5:
                player.game.output(player.name + " places " + card.colored_name() + " on top of their deck",
                                   client=c.ALL)
                to_pile = player.deck

    return to_pile


def goons_effect(player, card_class):
    active_card_names = [card.name for card in player.active_cards]
    if c.goons in active_card_names:
        try:
            player.gain_vt(num=player.effects[c.goons][c.number])
        except Exception:
            player.game.output(f"{card_class(**c.card_list[c.goons]).colored_name()} was unable to grant any VT",
                               client=c.ALL)


def hoard_effect(player, gained_card, card_class):
    if c.hoard in player.effects:
        gold_pile = player.game.supply.piles[c.gold]
        if gold_pile.number > 0:
            if c.victory in gained_card.types:
                for _ in range([card.name for card in player.active_cards].count(c.hoard)):
                    if gold_pile.number > 0:
                        if player.game.verbose:
                            card_name = card_class(**c.card_list[c.hoard]).colored_name()
                            player.game.output(card_name + " grants you a " + gold_pile.colored_name())
                            if player.game.multiplayer():
                                player.game.output(card_name + " grants " + player.name + " a " + gold_pile.colored_name(),
                                                   client=c.OTHERS)
                        player.gain(gold_pile, mute=True)
                    else:
                        if player.game.verbose:
                            card_name = card_class(**c.card_list[c.hoard]).colored_name()
                            player.game.output(card_name + " would have granted you a " + gold_pile.colored_name() +
                                               "; however, the pile is empty.")
                            if player.game.multiplayer():
                                player.game.output(card_name + " would have granted " + player.name + " a " +
                                                   gold_pile.colored_name() + "; however, the pile is empty.",
                                                   client=c.OTHERS)
        else:
            if player.game.verbose:
                card_name = card_class(**c.card_list[c.talisman]).colored_name()
                player.game.output(card_name + " would have granted you a " + gold_pile.colored_name() +
                                   ", however the pile is empty.")
                if player.game.multiplayer():
                    player.game.output(card_name + " would have granted " + player.name + " a " + gold_pile.colored_name() +
                                       ", however the pile is empty.", client=c.OTHERS)
