#!/usr/bin/env python3

import os
import re
import subprocess
from typing import Union
import json


def get_screen_data(screen_data: str) -> dict:
    """
    Gets a line of output from `xrandr --listactivemonitors` 
    and parses the data from it.

    Example of output:
        0: +*DP-2 3440/820x1440/346+2560+0  DP-2
        1: +DP-4 2560/345x1600/215+0+0  DP-4

    Args:
        screen_data (str): A line of output from xrandr

    Returns:
        dict: A dictionary with parsed data.
            Example: {
                'name': 'DP-2',
                'index': 0,
                'current': True,
                'x': 2560,
                'y': 0,
                'width': 3440,
                'height': 1440,
                'width_mm': 820,
                'height_mm': 346
            }
    """
    res = {}

    # 0: +*DP-2 3440/820x1440/346+2560+0  DP-2
    # 1: +DP-4 2560/345x1600/215+0+0  DP-4

    data = screen_data.strip().split('  ')
    if len(data) != 2:
        return None

    res['name'] = data[1]
    screen_data = data[0]

    data = screen_data.strip().split(' ')
    if len(data) == 3:
        res['index'] = int(data[0].strip(':'))
        res['current'] = '*' in data[1]
        screen_data = data[2]

    data = screen_data.split('+')
    if len(data) == 3:
        res['x'] = int(data[1])
        res['y'] = int(data[2])
        screen_data = data[0]

    data = screen_data.split('x')

    def _get_px_mm(_data):
        return tuple(map(int, _data.split('/')))

    if len(data) == 2:
        res['width'], res['width_mm'] = _get_px_mm(data[0])
        res['height'], res['height_mm'] = _get_px_mm(data[1])

    return res


def get_active_screens() -> list:
    """
    Gets data about the active screens. Sample output data in get_screen_data.

    Returns:
        list: Sorted list of screens from left to right
    """
    res = []
    output = subprocess.check_output(['xrandr', '--listactivemonitors'])

    monitors = output.decode().strip().split(os.linesep)

    for monitor in monitors:
        screen_data = get_screen_data(monitor)
        if not screen_data:
            continue
        res.append(screen_data)

    res.sort(key=lambda s: s.get('x', 0))
    return res


def get_config() -> list:
    """
    Opens and parses the conf.json file in the same directory.

    Returns:
        list: The list of apps defined in the conf.json
    """
    folder = os.path.dirname(__file__)

    config = []
    conf_path = os.path.join(folder, 'config.json')
    try:
        with open(conf_path, 'r', encoding='utf8') as file:
            config = json.load(file)
    except OSError:
        print(f'Error: Unable to open {conf_path}')

    assert isinstance(config, list), "Expected conf.json to contain an Array"
    assert len(config) > 0, "Expected at least one app to be defined in conf.json"

    return config


def set_desktops(count: int):
    """
    Sets the desktops count

    Args:
        count (int): Desktops count
    """
    output = subprocess.check_output(['xdotool', 'get_num_desktops'])
    desktops_count = int(output.decode().strip())
    if desktops_count >= count:
        log(f'There are already {count} or more desktops')
        return

    subprocess.check_output(['xdotool', 'set_num_desktops', str(count)])


def get_window(search_name: str, search_process: str) -> str:
    """
    Retrieves the ID of the last window that matches the search criteria

    Args:
        search_name (str): The regex serach criteria for window name
        search (str): The serach criteria for process name

    Returns:
        str: The window ID
    """
    try:
        pid = None
        if search_process:
            output = subprocess.check_output(['pgrep', '-f', search_process])
            pids = output.decode().strip().split(os.linesep)
            if len(pids) > 1:
                log(f"Multiple processes found for '{search_process}'",
                    level='error')
                return None
            pid = pids[0]

        command = ['xdotool', 'search']
        if pid:
            command.extend(['--onlyvisible', '--pid', pid])
        if search_name:
            command.extend(['--name', search_name])

        output = subprocess.check_output(command)

    except subprocess.CalledProcessError as err:
        log(err.output)
        return None

    # Use only the last widnow_id in case multiple exist.
    windows = output.decode().strip().split(os.linesep)
    return windows and windows[-1] or None


def set_window_size(window_id: str, name: str, width: int, height: int) -> None:
    """
    Sets the window size.

    Args:
        window_id (str): The ID of the window.
        name (str): The name of the window.
        width (int): The desired width or 0 to keep existing.
        height (int): The desired height or 0 to keep existing.
    """
    log(f'Setting size {width} x {height} for {name} window {window_id}')
    output = subprocess.check_output(
        ['xdotool', 'windowsize', window_id, str(width), str(height)])
    return output.decode().strip()


def set_window_pos(window_id: str, name: str, x_pos: int, y_pos: int) -> None:
    """
    Sets the window position.

    Args:
        window_id (str): The ID if the window.
        name (str): The name of the window.
        x_pos (int): The desired x position.
        y_pos (int): The desired y position.
    """
    log(f'Moving the {name} window {window_id} to position {x_pos} x {y_pos}')
    output = subprocess.check_output(
        ['xdotool', 'windowmove', window_id, str(x_pos), str(y_pos)])
    return output.decode().strip()


def set_window_desktop(window_id: str, name: str, desktop: int) -> None:
    """
    Moves the window to the relevant desktop.

    Args:
        window_id (str): The ID if the window.
        name (str): The name of the window.
        desktop (int): The desktop's index.
    """
    log(f'Moving {name} window {window_id} to desktop {desktop}')
    output = subprocess.check_output(
        ['xdotool', 'set_desktop_for_window', window_id, str(desktop)])
    return output.decode().strip()


def log(msg, level='info'):
    """
    Logs a message

    Args:
        msg (str): Message
    """
    print(f'{level.capitalize()}: {msg}')


def calc_size(source: Union[str, int], target: int) -> int:
    """
    Calculates the deired size and validate if it fits the target. 

    Args:
        source (Union[str, int]): Source can be a percentage (str) or number.
        target (int): Target.

    Returns:
        int: Computed size.
    """
    if isinstance(source, int):
        source = source if source > 0 else 0
        return min(source, target)

    source = source.strip()

    # Integer value as string
    if re.match(r'^[0-9]{1,4}$', source):
        return min(int(source), target)

    # Percentage
    if re.match(r'^[0-9]{1,3}%$', source):
        perc = int(source.replace('%', ''))
        perc = perc if 0 < perc <= 100 else 100
        return int(target * perc / 100)

    log(f'Invalid size {source}', level='error')
    return 0


def calc_pos(position: str, width: int, height: int,
             screen_width: int, screen_height: int) -> tuple:
    """
    Calculates the position.

    Args:
        position (str): String defining the position "vertical horizontal"
        width (int): width
        height (int): height
        screen_width (int): screen_width
        screen_height (int): screen_height

    Returns:
        tuple: x and y
    """
    pos = position.split(' ')

    assert len(pos) == 2, f"Invalid value for 'align' configuration {position}"

    vert, horiz = tuple(s.lower() for s in pos)

    assert vert in ('top', 'center', 'bottom') \
        or vert.endswith('%'), \
        f"Invalid value '{vert}' for vertical position."

    assert horiz in ('left', 'center', 'right') \
        or horiz.endswith('%'), \
        f"Invalid value '{horiz}' for horizontal position."

    y_pos = 0
    if vert == 'top':
        y_pos = 0
    elif vert == 'center':
        y_pos = int((screen_height - height) / 2)
    elif vert == 'bottom':
        y_pos = int(screen_height - height)
    else:
        y_pos = calc_size(vert, screen_height - height)

    x_pos = 0
    if horiz == 'left':
        x_pos = 0
    elif horiz == 'center':
        x_pos = int((screen_width - width) / 2)
    elif horiz == 'right':
        x_pos = int(screen_width - width)
    else:
        x_pos = calc_size(horiz, screen_width - width)

    return x_pos, y_pos


def arrange_window(window_config: dict, screens: list):
    """
    Moves a window to the screen and desktop defined in the config
    """
    config = {
        'name': 'Unknown',
        'search_name': '',
        'search_process': '',
        'screen': 0,
        'desktop': 2,
        'width': 0,
        'height': 0,
        'align': 'top left'
    }
    config.update(window_config)

    assert config['search_name'] or config['search_process'], \
        f"No 'search_name' or 'search_process' configured for window {config['name']}"
    assert isinstance(config['screen'], int), \
        f"The 'screen' configuration of {config['name']} must be an integer number"

    if len(screens) <= config['screen']:
        log(f"There are only {len(screens)} available. "
            f"Can't set {config['name']} on screen {config['screen']}", level='error')
        return

    screen = screens[config['screen']]

    # Get the window
    win_id = get_window(config['search_name'], config['search_process'])
    if not win_id:
        log(f'No window found for {config["name"]}', level='error')
        return

    width = calc_size(config['width'], screen['width'])
    height = calc_size(config['height'], screen['height'])

    x_pos, y_pos = calc_pos(
        config['align'], width, height, screen['width'], screen['height'])
    x_pos = x_pos + screen['x']
    y_pos = y_pos + screen['y']

    set_window_pos(win_id, config['name'], x_pos, y_pos)

    set_window_size(win_id, config['name'], width, height)

    set_window_desktop(win_id, config['name'], config['desktop'])


def arrange_windows():
    """
    Reads screens info and config and places the windows accordingly
    """
    screens = get_active_screens()
    config: list = get_config()

    max_desktop = max(c.get('desktop', 0) for c in config)
    set_desktops(count=max_desktop+1)

    for win_conf in config:
        arrange_window(win_conf, screens)


if __name__ == '__main__':
    arrange_windows()
