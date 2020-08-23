import constants as c


def moat_reaction(player, card):
    player.reveal(player.hand, card, move=False)
    player.effects.append(c.moat)

    return True
