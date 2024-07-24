from .command import CommandProcessor
from .movements import get_separated_movements_by_name


class Events:
    def __init__(
        self,
        keyboard_enabled: bool,
        pressing_timer_interval: dict,
        command_key_mappings: dict,
    ):
        self.keyboard_enabled = keyboard_enabled
        self.command_key_mappings = command_key_mappings
        self.pressing_timer_interval = pressing_timer_interval

        self.history = []

        self.commands_map: dict[str, CommandProcessor] = dict()
        for key in self.pressing_timer_interval.keys():
            self.commands_map[key] = CommandProcessor()

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    # Add command to pipeline
    def add(self, command_name, command_type, timestamp):
        # check in history and ignore if related movements are already added during the configured duration
        ignored_movements = get_separated_movements_by_name(command_name)
        if ignored_movements:
            for event in self.history:
                event_name = event["name"]
                if event_name in ignored_movements["group"] and timestamp - event[
                    "timestamp"
                ] < ignored_movements.get("duration", 0):
                    # print("ignore", command_name, command_type)
                    return

        # only keeps latest events in history from 10 seconds
        self.history = [
            event for event in self.history if timestamp - event["timestamp"] < 10000
        ]
        self.history.append(
            {"name": command_name, "timestamp": timestamp, "type": command_type}
        )

        # print("add command", command_name, command_type)

        pressing_timer_interval = self.pressing_timer_interval[command_type]

        self.commands_map[command_type].add_command(
            command_name,
            self.keyboard_enabled,
            self.command_key_mappings,
            pressing_timer_interval,
        )

    def __str__(self):
        result = ""
        for k, v in self.commands_map.items():
            result += f"{k} ({len(v.commands)}): {v}\n"

        return result
