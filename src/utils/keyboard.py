from pynput.keyboard import Key

keyboard_mappings = (
    (Key.space, "space"),
    (Key.shift, "shift"),
    (Key.ctrl, "ctrl"),
    (Key.tab, "tab"),
    (Key.enter, "enter"),
    (Key.esc, "esc"),
    (Key.up, "up"),
    (Key.down, "down"),
    (Key.left, "left"),
    (Key.right, "right"),
)

keyboard_special_key_names = [v for k, v in keyboard_mappings]


def keyboard_to_str(key):
    for k, v in keyboard_mappings:
        if key == k:
            return v
    return str(key)


def str_to_keyboard(value):
    for k, v in keyboard_mappings:
        if value == v:
            return k
    return value
