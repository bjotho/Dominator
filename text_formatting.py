import re

# ANSI text formatting
END = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
WHITE_BG = "\033[47m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_GREEN_BG = "\033[102m"
BRIGHT_YELLOW_BG = "\033[103m"
BRIGHT_BLUE_BG = "\033[104m"
BRIGHT_MAGENTA_BG = "\033[105m"
COIN = BOLD + BLACK + BRIGHT_YELLOW_BG
VP = BOLD + BLACK + BRIGHT_GREEN_BG
CURSE = BOLD + BLACK + BRIGHT_MAGENTA_BG

placeholder_list = ["\0", "\1", "\2", "\3", "\4", "\5", "\6", "\7"]
help_message = "List of commands:\n"\
               "  b:\tInitiate buying phase\n"\
               "  h:\tView hand\n"\
               "  hh:\tPrint all cards in hand\n"\
               "  v:\tView a card from the supply\n"\
               "  vv:\tPrint all cards in the supply\n"\
               "  a:\tToggle autoplay treasure cards\n"\
               "  p:\tPlay additional treasure cards during buy phase\n"\
               "  e:\tEnd turn\n"\
               "  x:\tEnd game\n"


def bold(text:str):
    return BOLD + text + END


def italic(text:str):
    return ITALIC + text + END


def money(plain=True):
    if plain:
        return COIN + "  " + END
    else:
        return "+" + COIN + "  " + END


def coins(num, plain=False):
    if plain:
        return COIN + " " + str(num) + " " + END
    else:
        return COIN + " +" + str(num) + " " + END


def vp(num:int, plain=False):
    if num < 0 or plain:
        return VP + " " + str(num) + " VP " + END
    elif num >= 0:
        return VP + " +" + str(num) + " VP " + END


def vt(num:int, plain=False):
    if num < 0 or plain:
        return VP + " " + str(num) + " VT " + END
    elif num >= 0:
        return VP + " +" + str(num) + " VT " + END


def curse(num:int):
    return CURSE + " " + str(num) + " VP " + END


def title(text:str):
    return ITALIC + UNDERLINE + text + END


def action(text:str):
    return BLACK + WHITE_BG + " " + text + " " + END


def reaction(text:str):
    return BLACK + BRIGHT_BLUE_BG + " " + text + " " + END


def treasure(text:str):
    return BLACK + BRIGHT_YELLOW_BG + " " + text + " " + END


def victory(text:str):
    return BLACK + BRIGHT_GREEN_BG + " " + text + " " + END


def curse_card(text:str):
    return BLACK + BRIGHT_MAGENTA_BG + " " + text + " " + END


card_width = 30
text_width = card_width - 4


def center_recursive(text, format_groups=None):
    line = ""
    line_len = 0
    words = 0
    if format_groups is not None:
        for i in range(len(format_groups)):
            placeholder = placeholder_list[i] * len(format_groups[i][1])
            text = text.replace(format_groups[i][0], placeholder)

    line_list = text.split()
    while line_len < text_width:
        try:
            line_len += len(line_list[words]) + 1
            words += 1
        except IndexError:
            break

    line_len -= 1
    if line_len > text_width and words > 0:
        words -= 1

    for word in line_list[:words]:
        line += word + " "

    line = line[:-1].center(text_width)
    if format_groups:
        for i in range(len(format_groups)):
            placeholder = placeholder_list[i] * len(format_groups[i][1])
            line = line.replace(placeholder, format_groups[i][0])
            for j in range(len(line_list)):
                line_list[j] = line_list[j].replace(placeholder, format_groups[i][0])

    output = "| " + line + " |"
    rest = ""
    for word in line_list[words:]:
        rest += word + " "

    if rest == "":
        return output

    return output + "\n" + center_recursive(rest, format_groups)


def center(text):
    output = ""
    text = text.split("\n")
    for line in text:
        match_bold = re.findall(r"(\033\[1m(.+?)\033\[0m)+", line)
        match_italic = re.findall(r"(\033\[3m(.+?)\033\[0m)+", line)
        match_coin_vp_curse = re.findall(r"(\033\[1m\033\[30m\033\[10[0-9]m(.+?)\033\[0m)+", line)
        match_title = re.findall(r"(\033\[3m\033\[4m(.+?)\033\[0m)+", line)
        if match_bold or match_italic or match_coin_vp_curse or match_title:
            groups = []
            if match_coin_vp_curse:
                for match in match_coin_vp_curse:
                    groups.append(match)
            if match_title:
                for match in match_title:
                    groups.append(match)
            if match_bold:
                for match in match_bold:
                    groups.append(match)
            if match_italic:
                for match in match_italic:
                    groups.append(match)

            output += center_recursive(line, format_groups=groups)

        else:
            if len(line) <= text_width:
                output += "| " + line.center(text_width) + " |"
            else:
                output += center_recursive(line)

        output += "\n"

    return output


def formatted_str_len(text):
    match_bold = re.findall(r"(\033\[1m(.+?)\033\[0m)+", text)
    match_italic = re.findall(r"(\033\[3m(.+?)\033\[0m)+", text)
    match_coin_vp_curse = re.findall(r"(\033\[1m\033\[30m\033\[10[0-9]m(.+?)\033\[0m)+", text)
    match_title = re.findall(r"(\033\[3m\033\[4m(.+?)\033\[0m)+", text)
    if match_bold or match_italic or match_coin_vp_curse or match_title:
        if match_coin_vp_curse:
            groups = match_coin_vp_curse
        elif match_title:
            groups = match_title
        else:
            if match_bold:
                groups = match_bold
            else:
                groups = match_italic

        total_len = 0
        for group in groups:
            total_len += len(group[1])
        
        return total_len

    return len(text)


def visible_str_len(text):
    match_bold = re.findall(r"(\033\[1m(.+?)\033\[0m)+", text)
    match_italic = re.findall(r"(\033\[3m(.+?)\033\[0m)+", text)
    match_coin_vp_curse = re.findall(r"(\033\[1m\033\[30m\033\[10[0-9]m(.+?)\033\[0m)+", text)
    match_action = re.findall(r"(\033\[47m(.+?)\033\[0m)+", text)
    match_r_t_v_c = re.findall(r"(\033\[10[0-9]m(.+?)\033\[0m)+", text)
    match_title = re.findall(r"(\033\[3m\033\[4m(.+?)\033\[0m)+", text)
    matches = [match_bold, match_italic, match_coin_vp_curse, match_action, match_r_t_v_c, match_title]
    groups = []
    for match in matches:
        if match:
            groups.append(match)

    total_len = len(text)
    for group in groups:
        total_len += (len(group[0][1]) - len(group[0][0]))

    return total_len


def get_card(input_str, from_pile, return_index=False):
    card_str = ""
    out_card = None
    words = input_str.split()
    for word in words:
        card_str += word[0].upper() + word[1:].lower() + " "
    card_str = card_str[:-1]

    for card in from_pile:
        if card.name == card_str:
            out_card = card
            break

    if not out_card:
        for card in from_pile:
            if card.name == input_str:
                out_card = card
                break

    if return_index:
        if out_card:
            out_card = (out_card, from_pile.index(out_card))
        else:
            out_card = (None, None)

    return out_card


def get_cards(input_str, from_pile):
    tmp_pile = from_pile.copy()
    out_cards = []
    for card_str in input_str.split(","):
        card, i = get_card(card_str, tmp_pile, return_index=True)
        if card:
            out_cards.append(card)
            del tmp_pile[i]
        else:
            return None

    return out_cards
