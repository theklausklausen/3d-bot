# 3D-Bot

3D-Bot is a dockerized Python Telegram bot that connects to OctoPrint and sends you real-time updates on your 3D prints. You can also integrate scripts to execute before and after print updates, and after your print has finished. Additionally, the bot sends notifications when your filament runs out.

## Getting Started

### Prerequisites

To run 3D-Bot, you will need:

- [Docker](https://www.docker.com/)
- [OctoPrint](https://octoprint.org/)
- [Telegram API token](https://core.telegram.org/bots#3-how-do-i-create-a-bot)

### Installation

1. Clone this repository to your local machine.
2. Create a copy of the `workspace.env.example` file and name it `workspace.env`.
3. Edit the `workspace.env` file and add your Telegram API token.
4. Build the Docker image by running `docker-compose build`.
5. Start the container by running `docker-compose up -d`.

The bot should now be up and running. You can interact with it by searching for its name in Telegram and sending it commands.

## Usage

Here are some of the commands that you can use with 3D-Bot:

- `/help` - Get a list of available commands. (not implemented yet)
- `/status` - Get the current status of your 3D printer. (not implemented yet)
- `/printinfo` - Get information about the current print, including the estimated time remaining and the amount of filament used. (not implemented yet)
- `/pause` - Pause the current print. (not implemented yet)
- `/resume` - Resume the current print. (not implemented yet)
- `/cancel` - Cancel the current print. (not implemented yet)
- `/filament` - Get the current amount of filament remaining. (not implemented yet)

### Custom Scripts

You can also integrate custom scripts to execute before and after print updates, and after your print has finished. To do this, you will need to create a Python script with following function definitions, mount it to the container and set the path of the script in the `CUSTOM_SCRIPT_PATH` environment variable.

Following commands will be called:

```python
from octopi import OctoPi
from job import Job
from telegram_client import Telegram

# executed before state message is send
def preMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
    print('pre message command')

# executed after state message is send
def postMessageCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
    print('post message command')

# executed after print has finished
def postFinishCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
    print('post finish command')

# executed when printer run out of filament
def onFilamentEmptyCommand(self, telegram_client: Telegram, job: Job, octopi: OctoPi) -> None:
    print('on filament empty command')
```

You can then call this script by adding the following line to your .env file:

```bash
CUSTOM_SCRIPT_PATH=/app/custom_script-py
```

If you need to add additional packages, then mount your own `requirements.txt` to `app/requirements.txt` and rebuild the image. Following packages have to be in the `requirements.txt` for the bot itself:

```bash
# Bot packages
anyio==3.6.2
certifi==2022.12.7
charset-normalizer==3.1.0
debugpy==1.6.7
h11==0.14.0
httpcore==0.16.3
httpx==0.23.3
idna==3.4
Pillow==9.5.0
python-dotenv==1.0.0
python-telegram-bot==20.0
requests==2.29.0
rfc3986==1.5.0
sniffio==1.3.0
urllib3==1.26.15

# User Packages
```

### Contributing

Contributions are welcome! Please submit a pull request if you would like to make any changes.

### License

This project is licensed under the MIT License. See the LICENSE file for details.
