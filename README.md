# MotionMap: Transforming Body Movements into Keyboard Actions

Transform real-time body movements — including walking, squatting, hand swinging, and head tilting — into keyboard inputs, enabling a more interactive and intuitive way to control apps and games.

## Demo

Control a RPG game (Legend of Zelda)

[![Watch the video](https://img.youtube.com/vi/nMx1VlgjfBw/default.jpg)](https://youtu.be/nMx1VlgjfBw)

Control a racing game

[![Watch the video](https://img.youtube.com/vi/gAEEKOdsAxs/default.jpg)](https://youtu.be/gAEEKOdsAxs)

## How to install

Install python3

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

Run the `app.exe` file in the root directory

## Configuration

In `src/config.py` edit these objects:

- `mp_config`: Edit mediapipe pose configuration
- `control_list`: Edit input controller
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

#### FPS mode (in development)

## Improvements

- Edit mediapipe configuration in app
- Allow edit input controller in app
- Edit gesture detection thresholds
- Edit pressing keyboard interval for each gesture
