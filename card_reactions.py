import constants as c
from card_methods import np, confirm_card


def moat_reaction(player, self_card):
    player.reveal(player.hand, self_card, move=False)
    player.effects[c.moat] = c.effect_dict[c.moat]

    return True


def watchtower_reaction(player, self_card, gain_card, to_pile):
    player.reveal(player.hand, self_card, move=False)
    if player.human:
        while True:
            if confirm_card(player, "Trash " + gain_card.colored_name() + " (y/n)?", mute_n=True):
                player.trash(from_pile=to_pile, card=gain_card)
                break
            elif confirm_card(player, gain_card.colored_name() + " will be placed on top of the deck (y/n):",
                              mute_n=True):
                if player.game.verbose:
                    player.game.output(player.name + " places " + gain_card.colored_name() + " on top of their deck",
                                       client=c.ALL)
                player.move(from_pile=to_pile, to_pile=player.deck, card=gain_card)
                break
            else:
                if player.game.verbose:
                    player.game.output("Invalid input", client=player)
    else:
        if np.random.random() > 0.5:
            player.trash(from_pile=to_pile, card=gain_card)
        else:
            if player.game.verbose:
                player.game.output(player.name + " places " + gain_card.colored_name() + " on top of their deck",
                                   client=c.ALL)
            player.move(from_pile=to_pile, to_pile=player.deck, card=gain_card)

    return True
