import re

# ANSI text formatting
END = "\033[0m"
BOLD = "\033[1m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLACK = "\033[30m"
YELLOW_BG = "\033[103m"
GREEN_BG = "\033[102m"
MAGENTA_BG = "\033[105m"
COIN = BOLD + BLACK + YELLOW_BG
VP = BOLD + BLACK + GREEN_BG
CURSE = BOLD + BLACK + MAGENTA_BG

placeholder_list = ["\0", "\1", "\2", "\3", "\4", "\5", "\6", "\7"]


def bold(text:str):
    return BOLD + text + END


def italic(text:str):
    return ITALIC + text + END


def coins(num:int, plain=False):
    if plain:
        return COIN + " " + str(num) + " " + END
    else:
        return COIN + " +" + str(num) + " " + END


def vp(num:int, plain=False):
    if num < 0 or plain:
        return VP + " " + str(num) + " VP " + END
    elif num >= 0:
        return VP + " +" + str(num) + " VP " + END


def curse(num:int):
    return CURSE + " " + str(num) + " VP " + END


def title(text:str):
    return ITALIC + UNDERLINE + text + END


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
            if match_coin_vp_curse:
                groups = match_coin_vp_curse
            elif match_title:
                groups = match_title
            else:
                if match_bold:
                    groups = match_bold
                else:
                    groups = match_italic

            # print(groups)
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
            total_len += len(group)

        return total_len

    return len(text)
