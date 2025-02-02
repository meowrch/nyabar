<h1 align="center"><img src="https://raw.githubusercontent.com/JaKooLit/Telegram-Animated-Emojis/refs/heads/main/Activity/Sparkles.webp"/ height=50> NyaBar</h1>
<p align="center">
 <a href="https://github.com/meowrch/nyabar/blob/master/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/meowrch/nyabar"></a>
  <a href='http://makeapullrequest.com'><img alt='PRs Welcome' src='https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=shields'/></a>
  <img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/meowrch/nyabar"/>
  <img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed/meowrch/nyabar"/>
  <img alt="discord" src="https://img.shields.io/discord/1200448076620501063" />
</p>

A semi-customizable bar written using the [Fabric Widget System](https://github.com/Fabric-Development/fabric).
The panel focuses on providing an all-in-one, fully integrated panel experience, where users don’t have to rely on separate, theme-less third-party tools to manage niche functions like bluetooth, notifications and notification panel,on screen display.

![image](https://github.com/user-attachments/assets/9f5a0e67-9b98-4615-adcf-511a05527ec2)

---

## ⚡ About the fork
Fork was created in order to integrate this project into bspwm (window manager). 
Also here will be added chips specifically for [meowrch](https://github.com/meowrch/meowrch). 

❤️ Huge thanks to the [original author](https://github.com/rubiin) of [this project](https://github.com/rubiin/HyDePanel). Without him it would have taken me a lot more time.

## Prerequisites

- [JetBrains Nerd Font](https://www.nerdfonts.com)
- [python 3+](https://www.python.org/downloads/)

---

## **Installation**

### Required

Most of these are already installed on existing working machines

```sh
# network
networkmanager

pipewire


## Bluetooth menu utilities
gnome-bluetooth-3.0 # aur
bluez
bluez-utils

## Copy/Paste utilities
wl-clipboard

## Compiler for sass/scss
dart-sass

## Brightness module for OSD
brightnessctl
```

### Optional

```sh

## To check for pacman updates in the default script used in the updates module
pacman-contrib

## To switch between power profiles in the battery module
power-profiles-daemon

## To record screen through the dashboard record shortcut
wf-recorder

## To enable the eyedropper color picker with the default snapshot shortcut in the dashboard
hyprpicker

## To enable hyprland's very own blue light filter
hyprsunset

## To enable hyprland's very own idle inhibitor
hypridle

```

- Clone this repository:

```sh
git clone https://github.com/meowrch/nyabar.git bar
cd bar
```

- Run the following command to install the required packages for particular os, few of them are already installed if you have a working system:

## Installation

You can choose one of two installation methods: **Automated Setup** or **Manual Setup**.

### Option 1: Automated Setup Using `init.sh -install`

1.  **Run the `init.sh -install` script** to automatically install all the required packages and dependencies (both `pacman` and AUR packages):

```sh
./init.sh -install
```

This script will:

- Install all required `pacman` and AUR packages.
- Set up the virtual environment and any required configurations.

1.  **Start the environment or bar** once the installation is complete:

```sh
./init.sh -start
```

This will launch the environment or bar as defined in your project.

### Option 2: Manual Setup (Install Dependencies First)

If you prefer to have more control over the installation process, you can install the required dependencies manually and then run the `init.sh -start` script.

#### Step 1: Install `pacman` Packages

Run the following command to install the required system packages:

```sh
	sudo pacman -S --noconfirm pipewire playerctl dart-sass power-profiles-daemon networkmanager wl-clipboard brightnessctl pkgconf wf-recorder kitty python pacman-contrib gtk3 cairo gtk-layer-shell libgirepository gobject-introspection gobject-introspection-runtime python-pip python-gobject python-psutil python-dbus python-cairo python-loguru python-setproctitle
```

#### Step 2: Install AUR Packages

Using `yay` to install the required AUR packages:

```sh
yay -S gray-git python-fabric gnome-bluetooth-3.0 python-rlottie-python
```

If you have something else besides `yay`, install with the respective aur helper.

#### Step 3: Run the `init.sh -start` Script

Once the dependencies are installed, run the following command to start the bar or environment:

```sh
./init.sh -start
```

## **Usage**

Add this to your `.config/hyprland.conf`

```sh
exec = `$HOME/bar/init.sh -start`

```

> **Note**: modify the path accordingly

Check FAQs for common things you are likely to encounter

## Updating

Updating to latest commit is fairly simple, just git pull the latest changes.

> **Note**: make sure to keep the config safe just in case

## Check wiki for configuring individual widgets

## **Available Modules**

<details>
<summary>Click to expand modules</summary>
Here is the list arranged in ascending order alphabetically:

- battery
- bluetooth
- brightness
- cava
- clickcounter
- cpu
- date_menu
- divider (utility)
- hypr_idle
- hypr_sunset
- keyboard
- language
- media
- microphone
- power
- ram
- recorder
- spacer (utility)
- storage
- stop_watch
- system_tray
- taskbar
- updates
- volume
- weather
- window_title
- workspace
- workspaces

</details>

## Screenshots

<details>
<summary>Click to see screenshots</summary>

![image](https://github.com/user-attachments/assets/4bd1fd6d-6c35-43e1-ae47-f0f76089f447)

## Notification

![image](https://github.com/user-attachments/assets/6c66b11c-6a21-4dcb-ab7f-7ed586abbf65)

## Calendar with notification panel

![image](https://github.com/user-attachments/assets/6e3ef49a-64b3-4dbd-8ccd-53430ff6ecff)

## OSD

![image](https://github.com/user-attachments/assets/25e171ff-f85e-4b62-9ed3-8e3479c2e4b4)

## Logout

![image](https://github.com/user-attachments/assets/18b5c851-4d3a-4801-b4c3-dbb555cfbae9)

</details>

> [!WARNING]
> This is still in early development and will include breaking changes

## Frequently Asked Questions (FAQ)

### 1. **Cannot see system tray?**

Be sure to kill any bars that you may be running. You can kill other bar with `pkill bar-name`

### 2. **Cannot see notifications?**

Be sure to kill other notifications daemon that you may be running. You can kill other daeemons with `pkill dunst; pkill mako;`

### 3. **Cannot see bar?**

Kill the app with `pkill hydepanel`. Run `init.sh -start`. This should show some logs. If it shows like `ModuleNotFoundError`, run `pip install -r requirements.txt`. If this does not solve the issue, do report a bug with screenshot of the log.

### 4. **No Blur?**

Add this to your `hyprland.conf`

```conf
layerrule = blur , fabric
layerrule = ignorezero, fabric
layerrule = blur ,gtk-layer-shell
layerrule = ignorezero ,gtk-layer-shell

```

## Contributing

We welcome all sorts of contributions, no matter how small, to this project! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute.

## Acknowledgements

- **Waybar** - A lot of the initial inspiration, and a pretty great bar.
  [Waybar GitHub Repository](https://github.com/Alexays/Waybar)

- **Hyprpanel** - Served as inspiration for some of the panel's features and design choices, with its focus on dynamic and customizable Hyprland panels.
  [Hyprpanel GitHub Repository](https://github.com/Jas-SinghFSU/HyprPanel)

## Special Thanks

A big thank you to the following people for their amazing help with code, bug fixes, and great ideas:

- [darsh](https://github.com/its-darsh): For creating fabric without which the project wouldn't have existed. Also, your quick feedbacks and problem-solving approach were a game-changer!
- [gummy bear album](https://github.com/muhchaudhary): For providing code snippets which served as a reference to start stuffs. Your creative ideas really pushed the project forward and made it better!
- [axenide](https://github.com/Axenide): For your fresh ideas and design references. Your code improvements and insights made a significant impact
- [sankalp](https://github.com/S4NKALP): For some bug fixes and recommendations,contributions in optimizing the code and identifying subtle bugs during the development period

# ⭐ Hit that Star Button!

Like what you see? Think this project is cooler than your morning coffee? ☕✨

Give it a star! It’s like giving a virtual high-five to the code—plus, and who doesn't love high-fives? ✋

Your star helps the project get noticed, and it makes us do a little happy dance. 💃

Just click the shiny "Star" button at the top right (it’s begging for your attention). 🥳

Thanks for making this project a little bit more awesome! 🚀

## Star History

<a href="https://star-history.com/#rubiin/HyDePanel&Timeline">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=rubiin/HyDePanel&type=Timeline&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=rubiin/HyDePanel&type=Timeline" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=rubiin/HyDePanel&type=Timeline" />
 </picture>
</a>
