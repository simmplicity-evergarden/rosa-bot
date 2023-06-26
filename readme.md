# Rosa Bot

## Install
1. Install the required packages: `pip install -r requirements.txt`

## Configuration
1. Place your discord bot token in `authentication.ini`
2. Add the associated role IDs to `config.ini`
	- Role IDs can be found by enabling developer options in "Discord Settings > Advanced" and right-clicking on a role.
	- Ensure the bot's role is higher in the roles list than either the speak or name perm roles.
3. (Optional) Use the integrations menu in the server to hide the command from non-mods.

## Running
Run `main.py` using Python 3.8 or higher. Lower versions may or may not work.

## Bot Perms
- Manage Roles
- Read message history
- Use Slash Commands
