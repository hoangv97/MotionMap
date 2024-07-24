from datetime import datetime
from pynput.keyboard import Controller
from threading import Timer
from .utils.keyboard import str_to_keyboard


class CommandProcessor:
    def __init__(self):
        self.keyboard = Controller()
        self.commands = []
        self.pressing_key = None
        self.pressing_timer = None

    def release_previous_key(self):
        if self.pressing_key:
            previous_key = self.pressing_key.get("key", None)
            if previous_key:
                print(f"releasing {previous_key}")
                self.keyboard.release(previous_key)

            previous_key_modifier = self.pressing_key.get("modifier", None)
            if previous_key_modifier:
                print(f"releasing {previous_key_modifier}")
                self.keyboard.release(previous_key_modifier)

            self.pressing_key = None

    # Clear log commands
    def limit_commands(self):
        if len(self.commands) > 900:
            self.commands = self.commands[-10:]

    def add_command(
        self,
        command_name: str,
        keyboard_enabled: bool,
        command_key_mappings: dict,
        pressing_timer_interval: float,
    ):
        self.limit_commands()

        now = datetime.now()
        self.commands.insert(0, dict(command=command_name, time=now))

        if keyboard_enabled:
            if command_name in command_key_mappings:
                command_config = command_key_mappings[command_name]
                key = command_config.get("key", None)
                modifier = str_to_keyboard(command_config.get("modifier", None))

                if not key and not modifier:
                    return

                # get current pressing key
                previous_key = None
                previous_key_modifier = None
                if self.pressing_key:
                    previous_key = self.pressing_key.get("key", None)
                    previous_key_modifier = self.pressing_key.get("modifier", None)

                # clear old timer
                if self.pressing_timer and self.pressing_timer.is_alive():
                    # print("cancel timer")
                    self.pressing_timer.cancel()

                # new action
                if previous_key != key or previous_key_modifier != modifier:
                    self.release_previous_key()
                    if key:
                        print("pressing", key, type(key))
                        self.keyboard.press(key)
                    if modifier:
                        print("pressing", modifier, type(modifier))
                        self.keyboard.press(modifier)

                if key or modifier:
                    # create new timer
                    self.pressing_timer = Timer(
                        pressing_timer_interval,
                        self.release_previous_key,
                    )
                    self.pressing_timer.start()

                    self.pressing_key = dict(key=key, modifier=modifier, time=now)

    def __str__(self):
        commands_list = list(map(lambda c: c["command"], self.commands))
        if not commands_list:
            return ""
        return commands_list[0] + "\n" + " | ".join(commands_list[1:10])
