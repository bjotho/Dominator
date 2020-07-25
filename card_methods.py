
"""
TODO: Implement method for each card
"""


def confirm_card(confirmation_string):
    while True:
        confirmation = input(confirmation_string)
        if confirmation not in ["y", "n"]:
            print("Please type \"y\" or \"n\"")
            continue
        if confirmation == "n":
            print("Aborted")
            return False
        return True


def cellar_card(player):
    if player.game.verbose:
        print("Select cards to discard (1-" + str(len(player.hand)) + ", separate with comma):")
    discard_cards_str = input()
    try:
        discard_list = [player.hand[int(s.strip()) - 1] for s in discard_cards_str.split(",")]
        for card in discard_list:
            print(card.name)
        if not confirm_card("The listed cards will be discarded (y/n):"):
            return
    except:
        print("Invalid card selection")
        cellar_card(player)
        return

    for card in discard_list:
        player.discard(player.hand, card)

    for _ in range(len(discard_list)):
        player.draw()

    player.actions += 1


def chapel_card(player):
    if player.game.verbose:
        print("Select cards to trash (1-" + str(len(player.hand)) + ", separate with comma):")
    trash_cards_str = input()
    try:
        trash_list = [player.hand[int(s.strip()) - 1] for s in trash_cards_str.split(",")]
        for card in trash_list:
            print(card.name)
        if not confirm_card("The listed cards will be trashed (y/n):"):
            return
    except:
        print("Invalid card selection")
        chapel_card(player)
        return

    for card in trash_list:
        player.trash(player.hand, card)


def copper_card(player):
    player.coins += 1


def silver_card(player):
    player.coins += 2


def gold_card(player):
    player.coins += 3


def platina_card(player):
    player.coins += 5


# card_text = {
#     # Base game cards
#     chapel: "Trash up to 4 cards from your hand.",
#     moat: txf.bold("+2 Cards") + "\n" + hl + "\nWhen another player plays an Attack card, you may first reveal this "
#         "from your hand, to be unaffected by it.",
#     chancellor: txf.coins(2) + "\nYou may immediately put your deck into your discard pile.",
#     harbinger: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\nLook through your discard pile. You may put a "
#         "card from it onto your deck.",
#     merchant: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\nThe first time you play a Silver this turn, "
#         + txf.coins(1) + ".",
#     vassal: txf.coins(2) + "\nDiscard the top card of your deck. If it's an Action card, you may play it."
# }