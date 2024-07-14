from .command import CommandProcessor
from .movements import SEPARATED_MOVEMENTS_DURATION, get_separated_movements_by_name


class Events:
    def __init__(
        self,
        keyboard_enabled,
        pressing_timer_interval,
        command_key_mappings,
    ):
        self.keyboard_enabled = keyboard_enabled
        self.command_key_mappings = command_key_mappings
        self.pressing_timer_interval = pressing_timer_interval

        self.history = []

        # process all commands
        self.one_click_cmd_process = CommandProcessor()
        # process cmd related to direction (left, right)
        self.hold_cmd_process = CommandProcessor()  # walk
        self.hold_2_cmd_process = CommandProcessor()  # face

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    # Add command to pipeline
    def add(self, command_name, command_type, timestamp):
        # check in history and ignore if related movements are already added during the configured duration
        ignored_movements = get_separated_movements_by_name(command_name)
        for event in self.history:
            event_name = event["name"]
            if (
                event_name in ignored_movements
                and timestamp - event["timestamp"] < SEPARATED_MOVEMENTS_DURATION
            ):
                print("ignore", command_name, command_type)
                return

        # only keeps latest events in history from 10 seconds
        self.history = [
            event for event in self.history if timestamp - event["timestamp"] < 10000
        ]
        self.history.append(
            {"name": command_name, "timestamp": timestamp, "type": command_type}
        )

        print("add command", command_name, command_type)

        # Split command by type
        if command_type == "1_click":
            self.one_click_cmd_process.add_command(
                command_name,
                self.keyboard_enabled,
                self.command_key_mappings,
                self.pressing_timer_interval[command_type],
            )
        elif command_type == "hold":
            self.hold_cmd_process.add_command(
                command_name,
                self.keyboard_enabled,
                self.command_key_mappings,
                self.pressing_timer_interval[command_type],
            )
        elif command_type == "hold_2":
            self.hold_2_cmd_process.add_command(
                command_name,
                self.keyboard_enabled,
                self.command_key_mappings,
                self.pressing_timer_interval[command_type],
            )

    def __str__(self):
        return f"""
Hold ({len(self.hold_cmd_process.commands)}): {self.hold_cmd_process}

Hold2 ({len(self.hold_2_cmd_process.commands)}): {self.hold_2_cmd_process}

1 click ({len(self.one_click_cmd_process.commands)}): {self.one_click_cmd_process}"""
