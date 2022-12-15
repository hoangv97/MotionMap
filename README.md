# Body gesture to keyboard control

Convert real-time body gestures such as walking, squat, swing hands, tilt head,... to keyboard input using Mediapipe Pose solution.

## Installation

Create an virtual environment (optional)

```sh
virtualenv venv
.\venv\Scripts\activate
```

Install packages

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

## Supported body gestures

### Head

`body/face.py`: Tilt head in left/right

### Hands

`body/arm.py`

- Swing hands
  - Left: swing hand from left to right
  - Left + hold: swing left hand with right hand up
  - Right
  - Right + hold
- Hands crossed: Cross 2 hands in Wakanda style

### Legs

`body/leg.py`

- Walking:
  - Up: walking with 2 hands down
  - Left: walking with only left hand up 90 degree
  - Right: walking with only right hand up 90 degree
  - Backwards: : walking with both hands up 90 degree
- Squat

## Improvements

- Edit mediapipe configuration in app
- Allow edit input controller in app
- Edit gesture detection thresholds
- Edit pressing keyboard interval for each gesture
