import constants as c


def moat_reaction(player, card):
    player.reveal(card)
    player.effects.append(c.moat)
    return True
