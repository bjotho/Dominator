import text_formatting as txf


hl = "_" * (txf.text_width - 4)

set_name = True

# Dictionary keys
name = "name"
set = "set"
types = "types"
cost = "cost"
text = "text"
pile_size = "pile size"
# actions = "actions"
# villagers = "villagers"
# draws = "draws"
# buys = "buys"
# coins = "coins"
# coffers = "coffers"
# trash = "trash"
# exile = "exile"
# junk = "junk"
# gain = "gain"
# victory_points = "victory points"
req_active = "require active"
number = "number"
description = "description"
contraband_cards = "contraband cards"

# Dominion set names
base = "Base"
base_1e = "Base, 1E"
base_2e = "Base, 2E"
intrigue = "Intrigue"
intrigue_1e = "Intrigue, 1E"
intrigue_2e = "Intrigue, 2E"
seaside = "Seaside"
alchemy = "Alchemy"
prosperity = "Prosperity"
cornucopia = "Cornucopia"
hinterlands = "Hinterlands"
dark_ages = "Dark Ages"
guilds = "Guilds"
adventures = "Adventures"
empires = "Empires"
nocturne = "Nocturne"
renaissance = "Renaissance"
menagerie = "Menagerie"
promo = "Promotional"

# Card types
action = "Action"
reaction = "Reaction"
attack = "Attack"   # Also reaction trigger
treasure = "Treasure"
victory = "Victory"
curse = "Curse"     # Also name of a card
prize = "Prize"
looter = "Looter"
command = "Command"
ruins = "Ruins"
knight = "Knight"
shelter = "Shelter"
reserve = "Reserve"
traveller = "Traveller"
duration = "Duration"
event = "Event"
gathering = "Gathering"
castle = "Castle"
landmark = "Landmark"
fate = "Fate"
night = "Night"
doom = "Doom"
spirit = "Spirit"
zombie = "Zombie"
heirloom = "Heirloom"
boon = "Boon"
hex = "Hex"
state = "State"
artifact = "Artifact"
project = "Project"
way = "Way"

# Reaction triggers
gain = "Gain"

# Card names

# Base game cards
cellar = "Cellar"
chapel = "Chapel"
moat = "Moat"
chancellor = "Chancellor"
harbinger = "Harbinger"
merchant = "Merchant"
vassal = "Vassal"
village = "Village"
woodcutter = "Woodcutter"
workshop = "Workshop"
bureaucrat = "Bureaucrat"
feast = "Feast"
gardens = "Gardens"
militia = "Militia"
moneylender = "Moneylender"
poacher = "Poacher"
remodel = "Remodel"
smithy = "Smithy"
spy = "Spy"
thief = "Thief"
throne_room = "Throne Room"
bandit = "Bandit"
council_room = "Council Room"
festival = "Festival"
laboratory = "Laboratory"
library = "Library"
market = "Market"
mine = "Mine"
sentry = "Sentry"
witch = "Witch"
adventurer = "Adventurer"
artisan = "Artisan"
copper = "Copper"
silver = "Silver"
gold = "Gold"
estate = "Estate"
duchy = "Duchy"
province = "Province"

# Prosperity cards
loan = "Loan"
trade_route = "Trade Route"
watchtower = "Watchtower"
bishop = "Bishop"
monument = "Monument"
quarry = "Quarry"
talisman = "Talisman"
workers_village = "Worker\'s Village"
city = "City"
contraband = "Contraband"
counting_house = "Counting House"
mint = "Mint"
mountebank = "Mountebank"
rabble = "Rabble"
royal_seal = "Royal Seal"
vault = "Vault"
venture = "Venture"
goons = "Goons"
grand_market = "Grand Market"
hoard = "Hoard"
bank = "Bank"
expand = "Expand"
forge = "Forge"
kings_court = "King\'s Court"
peddler = "Peddler"
platinum = "Platinum"
colony = "Colony"

# Dictionary for player effects
effect_dict = {
    moat: {number: 1, req_active: False, description: "You are unaffected by other players\' attacks this turn."},
    merchant: {number: 1, req_active: False, description: "The first time you play a silver this turn, " + txf.coins(1)
               + "."},
    quarry: {number: 1, req_active: True, description: "Action cards cost " + txf.coins(2, plain=True) + " less, but "
             "not less than " + txf.coins(0, plain=True) + "."},
    talisman: {number: 1, req_active: True, description: "When you buy a non-Victory card costing " +
               txf.coins(4, plain=True) + " or less, gain a copy of it."},
    contraband: {number: 1, req_active: False, description: "You are unable to buy from the following piles: ",
                 contraband_cards: []},
    royal_seal: {number: 1, req_active: True, description: "While this is in play, when you gain a card, you may put "
                 "that card onto your deck."},
    goons: {number: 1, req_active: True, description: "While this is in play, when you buy a card, " + txf.vt(1) + "."},
    hoard: {number: 1, req_active: True, description: "While this is in play, when you buy a Victory card, gain a "
            "Gold."}
}

# Starting deck for each player
starting_deck = {
    copper: 7,
    estate: 3
}

initial_treasures = [gold, silver, copper]
initial_victory_cards = [province, duchy, estate]

# Dictionary for card text
card_text = {
    # Base game cards
    cellar: txf.bold("+1 Action") + "\nDiscard any number of cards, then draw that many.",
    chapel: "Trash up to 4 cards from your hand.",
    moat: txf.bold("+2 Cards") + "\n" + hl + "\nWhen another player plays an Attack card, you may first reveal this "
        "from your hand, to be unaffected by it.",
    chancellor: txf.coins(2) + "\nYou may immediately put your deck into your discard pile.",
    harbinger: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\nLook through your discard pile. You may put a "
        "card from it onto your deck.",
    merchant: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\nThe first time you play a Silver this turn, "
        + txf.coins(1) + ".",
    vassal: txf.coins(2) + "\nDiscard the top card of your deck. If it's an Action card, you may play it.",
    village: txf.bold("+1 Card") + "\n" + txf.bold("+2 Actions"),
    woodcutter: txf.bold("+1 Buy") + "\n" + txf.coins(2),
    workshop: "Gain a card costing up to " + txf.coins(4, plain=True) + ".",
    bureaucrat: "Gain a Silver onto your deck. Each other player reveals a Victory card from their hand and puts it "
        "onto their deck (or reveals a hand with no Victory cards).",
    feast: "Trash this card. Gain a card costing up to " + txf.coins(5, plain=True) + ".",
    gardens: "Worth " + txf.vp(1, plain=True) + " per 10 cards you have (round down).",
    militia: txf.coins(2) + "\nEach other player discards down to 3 cards in hand.",
    moneylender: "You may trash a Copper from your hand for " + txf.coins(3) + ".",
    poacher: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\n" + txf.coins(1) + "\nDiscard a card per empty "
        "Supply pile.",
    remodel: "Trash a card from your hand. Gain a card costing up to " + txf.coins(2, plain=True) + " more than it.",
    smithy: txf.bold("+3 Cards"),
    spy: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\nEach player (including you) reveals the top card of "
        "their deck and either discards it or puts it back, your choice.",
    thief: "Each other player reveals the top 2 cards of their deck.\nIf they revealed any Treasure cards, they trash "
        "one of them that you choose. You may gain any or all of these trashed cards. They discard the other revealed "
        "cards.",
    throne_room: "You may play an Action card from your hand twice.",
    bandit: "Gain a Gold. Each other player reveals the top 2 cards of their deck, trashes a revealed Treasure other "
        "than Copper, and discards the rest.",
    council_room: txf.bold("+4 Cards") + "\n" + txf.bold("+1 Buy") + "\nEach other player draws a card.",
    festival: txf.bold("+2 Actions") + "\n" + txf.bold("+1 Buy") + "\n" + txf.coins(2),
    laboratory: txf.bold("+2 Cards") + "\n" + txf.bold("+1 Action"),
    library: "Draw until you have 7 cards in hand, skipping any Action cards you choose to; set those aside, "
        "discarding them afterwards.",
    market: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\n" + txf.bold("+1 Buy") + "\n" + txf.coins(1),
    mine: "You may trash a Treasure card from your hand. Gain a Treasure card to your hand costing up to "
        + txf.coins(3, plain=True) + " more than it.",
    sentry: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\nLook at the top 2 cards of your deck. Trash and/or "
        "discard any number of them. Put the rest back on top in any order.",
    witch: txf.bold("+2 Cards") + "\nEach other player gains a Curse.",
    adventurer: "Reveal cards from your deck until you reveal 2 Treasure cards. Put those Treasure cards into your "
        "hand and discard the other revealed cards.",
    artisan: "Gain a card to your hand costing up to " + txf.coins(5, plain=True) + "\nPut a card from your hand onto "
        "your deck.",
    copper: txf.coins(1, plain=True),
    silver: txf.coins(2, plain=True),
    gold: txf.coins(3, plain=True),
    estate: txf.vp(1, plain=True),
    duchy: txf.vp(3, plain=True),
    province: txf.vp(6, plain=True),
    curse: txf.curse(-1),
    # Prosperity cards
    loan: txf.coins(1, plain=True) + "\nWhen you play this, reveal cards from your deck until you reveal a Treasure. "
        "Discard it or trash it. Discard the other cards.",
    trade_route: txf.bold("+1 Buy") + "\nTrash a card from your hand. " + txf.coins(1) + " per Coin token on the Trade "
        "Route mat.\n" + hl + "\nSetup: Add a Coin token to each Victory Supply pile; move that token to the Trade "
        "Route mat when a card is gained from that pile.",
    watchtower: "Draw until you have 6 cards in hand.\n" + hl + "\nWhen you gain a card, you may reveal this from your "
        "hand, to either trash that card or put it onto your deck.",
    bishop: txf.coins(1) + "\n" + txf.vt(1) + "\nTrash a card from your hand. " + txf.vt(1) + " per "
        + txf.coins(2, plain=True) + " it costs (round down). Each other player may trash a card from their hand.",
    monument: txf.coins(2) + "\n" + txf.vt(1),
    quarry: txf.coins(1, plain=True) + "\n" + hl + "\nWhile this is in play, Action cards cost "
        + txf.coins(2, plain=True) + " less, but not less than " + txf.coins(0, plain=True) + ".",
    talisman: txf.coins(1, plain=True) + "\n" + hl + "\nWhile this is in play, when you buy a non-Victory card costing "
        + txf.coins(4, plain=True) + " or less, gain a copy of it.",
    workers_village: txf.bold("+1 Card") + "\n" + txf.bold("+2 Actions") + "\n" + txf.bold("+1 Buy"),
    city: txf.bold("+1 Card") + "\n" + txf.bold("+2 Actions") + "\nIf there are one or more empty Supply piles, "
        + txf.bold("+1 Card") + ". If there are two or more, " + txf.bold("+1 Buy") + " and " + txf.coins(1),
    contraband: txf.coins(3, plain=True) + "\n" + txf.bold("+1 Buy") + "\nWhen you play this, the player to your left "
        "names a card. You can’t buy that card this turn.",
    counting_house: " Look through your discard pile, reveal any number of Coppers from it, and put them into your "
        "hand.",
    mint: "You may reveal a Treasure card from your hand. Gain a copy of it.\n" + hl + "\nWhen you buy this, trash all "
        "Treasures you have in play.",
    mountebank: txf.coins(2) + "\nEach other player may discard a Curse. If they don’t, they gain a Curse and a "
        "Copper.",
    rabble: txf.bold("+3 Cards") + "\nEach other player reveals the top 3 cards of their deck, discards the revealed "
        "Actions and Treasures, and puts the rest back in any order they choose.",
    royal_seal: txf.coins(2, plain=True) + "\n" + hl + "\nWhile this is in play, when you gain a card, you may put "
        "that card onto your deck.",
    vault: txf.bold("+2 Cards") + "\nDiscard any number of cards for " + txf.coins(1) + " each. Each other player may "
        "discard 2 cards, to draw a card.",
    venture: txf.coins(1, plain=True) + "\nWhen you play this, reveal cards from your deck until you reveal a "
        "Treasure. Discard the other cards. Play that Treasure.",
    goons: txf.bold("+1 Buy") + "\n" + txf.coins(2) + "\nEach other player discards down to 3 cards in hand.\n" + hl
        + "\nWhile this is in play, when you buy a card, " + txf.vt(1) + ".",
    grand_market: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\n" + txf.bold("+1 Buy") + "\n" + txf.coins(2)
        + "\n" + hl + "\nYou can’t buy this if you have any Coppers in play.",
    hoard: txf.coins(2, plain=True) + "\n" + hl + "\nWhile this is in play, when you buy a Victory card, gain a Gold.",
    bank: "When you play this, it’s worth " + txf.coins(1, plain=True) + " per Treasure card you have in play "
        "(counting this).",
    expand: "Trash a card from your hand. Gain a card costing up to " + txf.coins(3, plain=True) + " more than it.",
    forge: "Trash any number of cards from your hand. Gain a card with cost exactly equal to the total cost in "
        + txf.money() + " of the trashed cards.",
    kings_court: "You may play an Action card from your hand three times.",
    peddler: txf.bold("+1 Card") + "\n" + txf.bold("+1 Action") + "\n" + txf.coins(1) + "\nDuring your Buy phase, this "
        "costs " + txf.coins(2, plain=True) + " less per Action card you have in play, but not less than "
        + txf.coins(0, plain=True) + ".",
    platinum: txf.coins(5, plain=True),
    colony: txf.vp(10, plain=True)
}

card_list = {
    # Base game cards
    cellar: {name: cellar, set: base, types: [action], cost: 2, text: card_text[cellar], pile_size: 10},
    chapel: {name: chapel, set: base, types: [action], cost: 2, text: card_text[chapel], pile_size: 10},
    moat: {name: moat, set: base, types: [action, reaction], cost: 2, text: card_text[moat], pile_size: 10},
    chancellor: {name: chancellor, set: base_1e, types: [action], cost: 3, text: card_text[chancellor], pile_size: 10},
    harbinger: {name: harbinger, set: base_2e, types: [action], cost: 3, text: card_text[harbinger], pile_size: 10},
    merchant: {name: merchant, set: base_2e, types: [action], cost: 3, text: card_text[merchant], pile_size: 10},
    vassal: {name: vassal, set: base_2e, types: [action], cost: 3, text: card_text[vassal], pile_size: 10},
    village: {name: village, set: base, types: [action], cost: 3, text: card_text[village], pile_size: 10},
    woodcutter: {name: woodcutter, set: base_1e, types: [action], cost: 3, text: card_text[woodcutter], pile_size: 10},
    workshop: {name: workshop, set: base, types: [action], cost: 3, text: card_text[workshop], pile_size: 10},
    bureaucrat: {name: bureaucrat, set: base, types: [action, attack], cost: 4, text: card_text[bureaucrat],
                 pile_size: 10},
    feast: {name: feast, set: base_1e, types: [action], cost: 4, text: card_text[feast], pile_size: 10},
    gardens: {name: gardens, set: base, types: [victory], cost: 4, text: card_text[gardens], pile_size: 12},
    militia: {name: militia, set: base, types: [action, attack], cost: 4, text: card_text[militia], pile_size: 10},
    moneylender: {name: moneylender, set: base, types: [action], cost: 4, text: card_text[moneylender], pile_size: 10},
    poacher: {name: poacher, set: base_2e, types: [action], cost: 4, text: card_text[poacher], pile_size: 10},
    remodel: {name: remodel, set: base, types: [action], cost: 4, text: card_text[remodel], pile_size: 10},
    smithy: {name: smithy, set: base, types: [action], cost: 4, text: card_text[smithy], pile_size: 10},
    spy: {name: spy, set: base_1e, types: [action, attack], cost: 4, text: card_text[spy], pile_size: 10},
    thief: {name: thief, set: base_1e, types: [action, attack], cost: 4, text: card_text[thief], pile_size: 10},
    throne_room: {name: throne_room, set: base, types: [action], cost: 4, text: card_text[throne_room], pile_size: 10},
    bandit: {name: bandit, set: base_2e, types: [action, attack], cost: 5, text: card_text[bandit], pile_size: 10},
    council_room: {name: council_room, set: base, types: [action], cost: 5, text: card_text[council_room],
                   pile_size: 10},
    festival: {name: festival, set: base, types: [action], cost: 5, text: card_text[festival], pile_size: 10},
    laboratory: {name: laboratory, set: base, types: [action], cost: 5, text: card_text[laboratory], pile_size: 10},
    library: {name: library, set: base, types: [action], cost: 5, text: card_text[library], pile_size: 10},
    market: {name: market, set: base, types: [action], cost: 5, text: card_text[market], pile_size: 10},
    mine: {name: mine, set: base, types: [action], cost: 5, text: card_text[mine], pile_size: 10},
    sentry: {name: sentry, set: base_2e, types: [action], cost: 5, text: card_text[sentry], pile_size: 10},
    witch: {name: witch, set: base, types: [action, attack], cost: 5, text: card_text[witch], pile_size: 10},
    adventurer: {name: adventurer, set: base_1e, types: [action], cost: 6, text: card_text[adventurer], pile_size: 10},
    artisan: {name: artisan, set: base_2e, types: [action], cost: 6, text: card_text[artisan], pile_size: 10},
    copper: {name: copper, set: base, types: [treasure], cost: 0, text: card_text[copper], pile_size: [46, 39, 32]},
    silver: {name: silver, set: base, types: [treasure], cost: 3, text: card_text[silver], pile_size: 40},
    gold: {name: gold, set: base, types: [treasure], cost: 6, text: card_text[gold], pile_size: 30},
    estate: {name: estate, set: base, types: [victory], cost: 2, text: card_text[estate], pile_size: [8, 12]},
    duchy: {name: duchy, set: base, types: [victory], cost: 5, text: card_text[duchy], pile_size: [8, 12]},
    province: {name: province, set: base, types: [victory], cost: 8, text: card_text[province], pile_size: [8, 12]},
    curse: {name: curse, set: base, types: [curse], cost: 0, text: card_text[curse], pile_size: [10, 20, 30]},
    # Prosperity cards
    loan: {name: loan, set: prosperity, types: [treasure], cost: 3, text: card_text[loan], pile_size: 10},
    trade_route: {name: trade_route, set: prosperity, types: [action], cost: 3, text: card_text[trade_route],
                  pile_size: 10},
    watchtower: {name: watchtower, set: prosperity, types: [action, reaction], cost: 3, text: card_text[watchtower],
                 pile_size: 10},
    bishop: {name: bishop, set: prosperity, types: [action], cost: 4, text: card_text[bishop], pile_size: 10},
    monument: {name: monument, set: prosperity, types: [action], cost: 4, text: card_text[monument], pile_size: 10},
    quarry: {name: quarry, set: prosperity, types: [treasure], cost: 4, text: card_text[quarry], pile_size: 10},
    talisman: {name: talisman, set: prosperity, types: [treasure], cost: 4, text: card_text[talisman], pile_size: 10},
    workers_village: {name: workers_village, set: prosperity, types: [action], cost: 4,
                      text: card_text[workers_village], pile_size: 10},
    city: {name: city, set: prosperity, types: [action], cost: 5, text: card_text[city], pile_size: 10},
    contraband: {name: contraband, set: prosperity, types: [treasure], cost: 5, text: card_text[contraband],
                 pile_size: 10},
    counting_house: {name: counting_house, set: prosperity, types: [action], cost: 5, text: card_text[counting_house],
                     pile_size: 10},
    mint: {name: mint, set: prosperity, types: [action], cost: 5, text: card_text[mint], pile_size: 10},
    mountebank: {name: mountebank, set: prosperity, types: [action, attack], cost: 5, text: card_text[mountebank],
                 pile_size: 10},
    rabble: {name: rabble, set: prosperity, types: [action, attack], cost: 5, text: card_text[rabble], pile_size: 10},
    royal_seal: {name: royal_seal, set: prosperity, types: [treasure], cost: 5, text: card_text[royal_seal],
                 pile_size: 10},
    vault: {name: vault, set: prosperity, types: [action], cost: 5, text: card_text[vault], pile_size: 10},
    venture: {name: venture, set: prosperity, types: [treasure], cost: 5, text: card_text[venture], pile_size: 10},
    goons: {name: goons, set: prosperity, types: [action, attack], cost: 6, text: card_text[goons], pile_size: 10},
    grand_market: {name: grand_market, set: prosperity, types: [action], cost: grand_market,
                   text: card_text[grand_market], pile_size: 10},
    hoard: {name: hoard, set: prosperity, types: [treasure], cost: 6, text: card_text[hoard], pile_size: 10},
    bank: {name: bank, set: prosperity, types: [treasure], cost: 7, text: card_text[bank], pile_size: 10},
    expand: {name: expand, set: prosperity, types: [action], cost: 7, text: card_text[expand], pile_size: 10},
    forge: {name: forge, set: prosperity, types: [action], cost: 7, text: card_text[forge], pile_size: 10},
    kings_court: {name: kings_court, set: prosperity, types: [action], cost: 7, text: card_text[kings_court],
                  pile_size: 10},
    peddler: {name: peddler, set: prosperity, types: [action], cost: peddler, text: card_text[peddler], pile_size: 10},
    platinum: {name: platinum, set: prosperity, types: [treasure], cost: 9, text: card_text[platinum], pile_size: 12},
    colony: {name: colony, set: prosperity, types: [victory], cost: 11, text: card_text[colony], pile_size: [8, 12]},
}

reaction_triggers = {
    moat: attack,
    watchtower: gain
}
