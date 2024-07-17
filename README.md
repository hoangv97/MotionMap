# Body gesture to keyboard control

Convert real-time body gestures such as walking, squat, swing hands, tilt head,... to keyboard input using Mediapipe Pose solution.

## Demo

RPG game

[![Watch the video](https://img.youtube.com/vi/nMx1VlgjfBw/default.jpg)](https://youtu.be/nMx1VlgjfBw)

Racing game

[![Watch the video](https://img.youtube.com/vi/gAEEKOdsAxs/default.jpg)](https://youtu.be/gAEEKOdsAxs)

## Installation

Create an virtual environment (optional)

```sh
python -m venv venv
.\venv\Scripts\activate
```

Install packages

```sh
pip install -r requirements.txt
```

## Run the application

```sh
python app.py
```

## Build

### Windows

```sh
python -m nuitka app.py
```

Run the exe file

## Configuration

In `src/config.py` edit these objects:

- `mp_config`: Edit mediapipe pose configuration
- `command_key_mappings_list`: Edit input controller
- `events_config`: Edit keyboard events configuration

## Supported body gestures

See details in file `src/movements.py`

### Head

Tilt head in left/right

### Hands

- Swing hands
  - Left: swing hand from left to right
  - Full swing: swing left hand from head to bottom
- Raise both hands up
- Hands crossed: Cross 2 hands in Wakanda style

### Legs

- Walking:
  - Up: walking with 2 hands down
  - Left: walking with only left hand up 90 degree
  - Right: walking with only right hand up 90 degree
  - Backwards: : walking with both hands up 90 degree
- Squat
- Left/right leg raised

#### Driving mode (in development)

- Move 2 hands close to enable steering wheel, tilt left or right to control
- Move 2 hands inside the green box to enable driving up control

## Improvements

- Edit mediapipe configuration in app
- Allow edit input controller in app
- Edit gesture detection thresholds
- Edit pressing keyboard interval for each gesture
