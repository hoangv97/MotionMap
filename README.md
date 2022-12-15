# Pose Estimation to keyboard

Convert pose from running, swing hand, tilt head,... to keyboard input using Mediapipe Pose solution.

## Installation

```sh
pip install -r requirements.txt
```

## Run the application

```sh
python window.py
```

## Configuration

In `window.py` edit these objects:

- `mp_config`: Edit mediapipe pose configuration
- `command_key_mappings_list`: Edit input controller
- `events_config`: Edit keyboard events configuration
