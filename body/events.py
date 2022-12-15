from datetime import datetime
from pynput.keyboard import Controller
from threading import Timer


class Events:

    keyboard = Controller()

    commands = []
    pressing_key = None
    pressing_timer = None

    walk_commands = []
    walk_pressing_key = None
    walk_pressing_timer = None

    face_commands = []
    face_pressing_key = None
    face_pressing_timer = None

    def __init__(
        self,
        keyboard_enabled,
        cross_cmd_enabled,
        pressing_timer_interval,
        walk_pressing_timer_interval,
        face_pressing_timer_interval,
        command_key_mappings,
    ):
        self.keyboard_enabled = keyboard_enabled
        self.cross_cmd_enabled = cross_cmd_enabled
        self.command_key_mappings = command_key_mappings
        self.pressing_timer_interval = pressing_timer_interval
        self.walk_pressing_timer_interval = walk_pressing_timer_interval
        self.face_pressing_timer_interval = face_pressing_timer_interval

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    # Toggle keyboard events if encounter cross hands command
    def check_cross_command(self, command):
        if self.cross_cmd_enabled and command == "cross":
            self.keyboard_enabled = not self.keyboard_enabled
            self.release_previous_key()
            self.release_previous_key()

    # Clear log commands
    def limit_commands(self):
        if len(self.commands) > 900:
            self.commands = self.commands[-10:]
        if len(self.walk_commands) > 100:
            self.walk_commands = self.walk_commands[-10:]

    # Add command to pipeline
    def add(self, command):
        self.check_cross_command(command)

        self.limit_commands()

        # Split command by type
        if "walk" in command or command in ["standing"]:
            self.add_walk_command(command)
        elif "face" in command:
            self.add_face_command(command)
        else:
            self.add_command(command)

    def release_walk_previous_key(self):
        if self.walk_pressing_key:
            previous_key = self.walk_pressing_key["key"]
            # print(f"releasing {previous_key}")
            self.keyboard.release(previous_key)
            self.walk_pressing_key = None

    def add_walk_command(self, command):
        now = datetime.now()
        self.walk_commands.insert(0, dict(command=command, time=now))

        if self.keyboard_enabled:
            if command in self.command_key_mappings:
                key = self.command_key_mappings[command]
                if key:
                    previous_key = None
                    if self.walk_pressing_key:
                        previous_key = self.walk_pressing_key["key"]

                    if self.walk_pressing_timer and self.walk_pressing_timer.is_alive():
                        # print("cancel walk timer")
                        self.walk_pressing_timer.cancel()

                    # new action
                    if previous_key != key:
                        self.release_walk_previous_key()
                        self.keyboard.press(key)

                    self.walk_pressing_timer = Timer(
                        self.walk_pressing_timer_interval,
                        self.release_walk_previous_key,
                    )
                    self.walk_pressing_timer.start()

                    self.walk_pressing_key = dict(key=key, time=now)

    def release_face_previous_key(self):
        if self.face_pressing_key:
            previous_key = self.face_pressing_key["key"]
            # print(f"releasing {previous_key}")
            self.keyboard.release(previous_key)
            self.face_pressing_key = None

    def add_face_command(self, command):
        now = datetime.now()
        self.face_commands.insert(0, dict(command=command, time=now))

        if self.keyboard_enabled:
            if command in self.command_key_mappings:
                key = self.command_key_mappings[command]
                if key:
                    previous_key = None
                    if self.face_pressing_key:
                        previous_key = self.face_pressing_key["key"]

                    if self.face_pressing_timer and self.face_pressing_timer.is_alive():
                        # print("cancel face timer")
                        self.face_pressing_timer.cancel()

                    # new action
                    if previous_key != key:
                        self.release_face_previous_key()
                        self.keyboard.press(key)

                    self.face_pressing_timer = Timer(
                        self.face_pressing_timer_interval,
                        self.release_face_previous_key,
                    )
                    self.face_pressing_timer.start()

                    self.face_pressing_key = dict(key=key, time=now)

    def release_previous_key(self):
        if self.pressing_key:
            previous_key = self.pressing_key["key"]
            # print(f"releasing {previous_key}")
            self.keyboard.release(previous_key)
            self.pressing_key = None

    def add_command(self, command):
        now = datetime.now()
        self.commands.insert(0, dict(command=command, time=now))

        if self.keyboard_enabled:
            if command in self.command_key_mappings:
                key = self.command_key_mappings[command]
                if key:
                    # get current pressing key
                    previous_key = None
                    if self.pressing_key:
                        previous_key = self.pressing_key["key"]

                    # clear old timer
                    if self.pressing_timer and self.pressing_timer.is_alive():
                        # print("cancel timer")
                        self.pressing_timer.cancel()

                    # new action
                    if previous_key != key:
                        self.release_previous_key()
                        self.keyboard.press(key)

                    # create new timer
                    self.pressing_timer = Timer(
                        self.pressing_timer_interval,
                        self.release_previous_key,
                    )
                    self.pressing_timer.start()

                    self.pressing_key = dict(key=key, time=now)

    def __str__(self):
        def log_commands(commands):
            commands_list = list(map(lambda c: c["command"], commands))
            if not commands_list:
                return ""
            return commands_list[0] + "\n" + ", ".join(commands_list[1:20])

        return f"""
Walk ({len(self.walk_commands)}): {log_commands(self.walk_commands)}

Face ({len(self.face_commands)}): {log_commands(self.face_commands)}

Events ({len(self.commands)}): {log_commands(self.commands)}"""
