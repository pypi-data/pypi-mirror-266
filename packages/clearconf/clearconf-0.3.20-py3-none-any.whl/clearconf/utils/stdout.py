import pprint


def print_list(config_list: list):
    formatted_list = pprint.pformat(config_list, compact=True)

    remove_chr = ['[', ']', ',', '\'']

    for c in remove_chr:
        formatted_list = formatted_list.replace(c, '')

    print(formatted_list)


def print_dict(config_list: list):
    formatted_list = pprint.pformat(config_list, compact=True)

    remove_chr = ['{', '}', ',', '\'']

    for c in remove_chr:
        formatted_list = formatted_list.replace(c, '')

    print(formatted_list)