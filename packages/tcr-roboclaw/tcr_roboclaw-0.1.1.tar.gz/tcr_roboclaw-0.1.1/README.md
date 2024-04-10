# RoboClaw Python Library - Team Chat Robotique

> An easy-to-install version of Basicmicro's RoboClaw Python library

We want to install and use this code easily on our robots for the [French Robotics Cup](https://www.coupederobotique.fr) and for [Eurobot](https://www.eurobot.org), so here is the main file that is distributed by Basicmicro.

All methods in the library have docstrings to help coding and understanding what they are used for. Most docstrings information is based on Basicmicro's [User Manual](https://downloads.basicmicro.com/docs/roboclaw_user_manual.pdf).

Most methods were not tested on a real RoboClaw, at the moment of releasing `tcr-roboclaw 0.1.0`. If you encounter a bug with the library, feel free to post [an issue](https://gitlab.com/team-chat-robotique/libraries/team-chat-robotique-roboclaw-python/-/issues) or a pull request on [our repo](https://gitlab.com/team-chat-robotique/libraries/team-chat-robotique-roboclaw-python).

## Installation

```console
pip install tcr-roboclaw
```

## Usage

Use `tcr-roboclaw` by importing the class :

```python
from tcr_roboclaw import Roboclaw

roboclaw = Roboclaw("/dev/ttyACM0", 115200)
roboclaw.open()
```

> :warning: Some method/function names were changed to comply with [PEP8](https://peps.python.org/pep-0008) or to make them more explicit ([_Explicit is better than implicit._](https://peps.python.org/pep-0020)). Double-check that you use the right methods when using this library with code that was written with the original RoboClaw Python library :warning:

## Contributing

(Recommended) [flit](https://flit.pypa.io) is used to package this module. Development packages can be installed using `flit` :

```console
python -m venv venv
source venv/bin/activate
pip install flit
flit install
```

## Acknowledgements

This package was created to install `roboclaw`'s Python library easily on any platform.
It contains code from the [official `basicmicro`' RoboClaw Python library](https://github.com/basicmicro/roboclaw_python_library).

## Related Links

* [RoboClaw Python Library](https://resources.basicmicro.com/using-the-roboclaw-python-library/)
* [User Manual](https://downloads.basicmicro.com/docs/roboclaw_user_manual.pdf)
* [Datasheet](https://downloads.basicmicro.com/docs/roboclaw_datasheet_2x15A.pdf)
