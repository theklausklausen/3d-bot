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
2. Create a copy of the `.env.sample` file and name it `.env`.
3. Edit the `.env` file and add your Telegram API token.
4. Build the Docker image by running `docker-compose build`.
5. Start the container by running `docker-compose up -d`.

The bot should now be up and running. You can interact with it by searching for its name in Telegram and sending it commands.

## Usage

Here are some of the commands that you can use with 3D-Bot:

- `/start` - Start the bot.
- `/help` - Get a list of available commands.
- `/status` - Get the current status of your 3D printer.
- `/printinfo` - Get information about the current print, including the estimated time remaining and the amount of filament used.
- `/pause` - Pause the current print.
- `/resume` - Resume the current print.
- `/cancel` - Cancel the current print.
- `/filament` - Get the current amount of filament remaining.

### Custom Scripts

You can also integrate custom scripts to execute before and after print updates, and after your print has finished. To do this, you will need to create a folder called `scripts` in the root of the project and add your scripts to this folder.

Following commands will be called:

```python
# executed before state message is send
def preMessageCommand(telegram_client, job, octopi):
    print('pre message command')

# executed after state message is send
def postMessageCommand(telegram_client, job, octopi):
    print('post message command')

# executed after print has finished
def postFinishCommand(telegram_client, job, octopi):
    print('post finish command')

# executed when printer run out of filament
def onFilamentEmptyCommand(telegram_client, job, octopi):
    def postFiishCommand(telegram_client, job, octopi):
    print('on filament empty command')
```

You can then call this script by adding the following line to your .env file:

```bash
CUSTOM_SCRIPT_PATH=/app/custom_script-py
```

### Contributing

Contributions are welcome! Please submit a pull request if you would like to make any changes.

### License

This project is licensed under the MIT License. See the LICENSE file for details.
