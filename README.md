# WinPos

Tool for Ubuntu/Linux that positions your windows to a dedicated place defined in a configuration file. 

It identifies the windows by title or by process name and positions them according to the values defined in `conf.json`.

The following commands are used to achieve the desired functionality:
- `xrandr` to retrieve the number of screens and their sizes.
- `xdotool` to get and set the number of desktops, set window position, set window size, place the window on desired desktop, identify a window by process ID.
- `pgrep` to search for a process and retrieve its ID.


## Installation and execution

1. Clone the current repository and navigate to its folder.
    ```bash
    git clone git@github.com:cix-code/win-pos.git
    cd win-pos
    ```
2. Install `xdotool`.
    ```bash
    sudo apt install xdotool
    ```
3. Create a copy of `sample.config.json` and edit your configuration as desired.
    ```bash
    cp sample.config.json config.json
    nano config.json
    ```
4. Run the `winpos.py` and check its output.
    ```bash
    python3 winpos.py
    ```
5. Run this as a delayed startup script to automatically place the windows to their correct place. 


## Configuration

`config.json` should contain a list of all applications you want to be positioned to a dedicated screen, desktop and place.

The following properties can be configured for each window:

- `name` - A name for the application. This doesn't influence the window position, but it helps to analyze the output and identify a problem based on this name.
- `search_name` - Regular Expression that matches the window title. This can be used for windows that have a static text part of their title.
- `search_process` - Identifies the window by process name. Useful when the window title changes dinamically.
- `screen` - The numeric index of the screen counting from the most left which has the value 0.
- `desktop` - WinPos can automatically create new desktops and position your windows accordingly. However, don't configure it to position a window on desktop 2 until desktop 1 doesn't have at least one window on it.
- `width` and `height` - Allows you to set the window's size. The values can be numeric to represent the number of pixels, or percentage relative to screen's size. 
- `align` - Defines the vertical respectively horizontal position. 
  Accepted values for the vertical position: `top|center|bottom` or a percentage value for the center point of the window. 
  Accepted values for the horizontal position: `left|center|right` or a percentage value for the center point of the window.

### Examples

```json
    // Postitions the Spotify window on the most left screen, 
    // on the first desktop centerly aligned.
    {
        "name": "Spotify",
        "search_name": "^Spotify$",
        "screen": 0,
        "desktop": 0,
        "width": "50%",
        "height": "60%",
        "align": "center center"
    },

    // Positions the PyCharm window on the second screen, 
    // on the second desktop and covers the whole real estate.
    // --
    // The window is identified by part of the process' full path.
    {
        "name": "PyCharm",
        "search_process": "pycharm/jbr/bin/java",
        "screen": 1,
        "desktop": 1,
        "width": "100%",
        "height": "100%",
        "align": "top left"
    },

    // Positions Telegram window on the second screen, 
    // on the third desktop aligning it 60% from the top and fully to the right.
    // --
    // Telegram is one of the apps that changes the window title to the selected chat name. 
    // Therefore the window is identified by the process name.
    {
        "name": "Telegram",
        "search_process": "telegram-desktop",
        "screen": 1,
        "desktop": 2,
        "width": "40%",
        "height": "60%",
        "align": "60% 100%"
    }

```

