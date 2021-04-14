# Marshall-Python-Controller

This is a quick and dirty solution to controll a Marshall Camera with an XBox Controller or CLI.

I do not recommend using the code without going through it and check if it fullfills your usecase.

The IP address is hardcoded.

It was only tested on Windows

# Usage
The environment variable `%MARSHALL_CONTROLLER%` needs is assumed to hold the directory if the python scripts

Turn on camera
```bash
python "%MARSHALL_CONTROLLER%\cli.py" --on
```

Turn off camera
```bash
python "%MARSHALL_CONTROLLER%\cli.py" --off
```

Start XBox Controller script
```bash
python "%MARSHALL_CONTROLLER%\controller.py"
```

Call a preset (Number from 0 to 255)
```bash
python "%MARSHALL_CONTROLLER%\cli.py" --call 1
```

Set a preset (Number from 0 to 255)
```bash
python "%MARSHALL_CONTROLLER%\cli.py" --set 1
```