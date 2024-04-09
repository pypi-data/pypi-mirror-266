def default_key_func(e):
    return get_message_size(e)


def unique_messages(messages, key_func=default_key_func):
    added_key_set = set()

    def check_unique(elem):
        key = key_func(elem)
        if key in added_key_set:
            return False
        else:
            added_key_set.add(key)
            return True

    unique_list = []
    for message in messages:
        if check_unique(message):
            unique_list.append(message)
    return unique_list


def get_message_size(message):
    if message_is_video_or_photo(message):
        if message.video is not None:
            return message.video.size
        elif message.photo is not None:
            return message.photo.sizes[1].size
    else:
        raise Exception(message)


def message_is_video_or_photo(message) -> bool:
    return message.video is not None or message.photo is not None


def sort_messages(messages):
    copy_list = messages.copy()
    copy_list.sort(key=lambda m: get_message_size(m), reverse=True)
    return copy_list


async def print_dialogs(dialogs):
    pass
    # for dialog in dialogs:
    #     print(dialog.id, dialog.title)


def get_video_or_photo_message(messages):
    ret = []
    for message in messages:
        if message_is_video_or_photo(message):
            ret.append(message)
    return ret


def get_config(parser, option, fallback, section='default'):
    if parser.has_section(section):
        if parser.has_option(section, option):
            if fallback is None:
                return parser.get(section, option)
            elif isinstance(fallback, bool):
                return parser.getboolean(section, option)
            elif isinstance(fallback, str):
                return parser.get(section, option)
            elif isinstance(fallback, int):
                return parser.getint(section, option)
            elif isinstance(fallback, list):
                return list(map(lambda x: int(x), parser.get(section, option).split(',')))
    return fallback


async def split_message(part, _iter_val, messages):
    end = part * _iter_val
    start = end - _iter_val
    messages = messages[start: end]
    return messages


async def filter_messages(messages):
    start = len(messages)
    messages = get_video_or_photo_message(messages)
    messages = unique_messages(messages)
    messages = sort_messages(messages)
    end = len(messages)
    print('\nbefore filter: ', start, 'after filter: ', end)
    return messages
