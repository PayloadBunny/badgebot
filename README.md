# BadgeBot

BadgeBot is a Discord bot that periodically checks the number of your badges for various Hack The Box Academy job role paths and exams, and sends updates to a specific Discord channel.

## Features

- Fetches the latest badge numbers from Hack The Box Academy.
- Compares the latest badge numbers with the previous values.
- Posts an update message in a Discord channel if there are any changes in badge numbers.
- Logs badge numbers with timestamps in a CSV file.
- Shows the last batch runs.

## Installation

1. **Create a Discord Bot**

   You can find instructions here:
   https://discordpy.readthedocs.io/en/stable/discord.html

2. **Clone the repository:**

   ```bash
   git clone https://github.com/payloadbunny/badgebot.git
   cd badgebot
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ````

4. **Create a .env file in the root directory and add the following environment variables:**

   ```plaintext
   DISCORD_TOKEN=your_discord_bot_token
   DISCORD_CHANNEL_ID=your_discord_channel_id
   CBBH_PATH=cbbh_path_id
   CBBH_EXAM=cbbh_exam_id
   CPTS_PATH=cpts_path_id
   CPTS_EXAM=cpts_exam_id
   CDSA_PATH=cdsa_path_id
   CDSA_EXAM=cdsa_exam_id
   CWEE_PATH=cwee_path_id
   CWEE_EXAM=cwee_exam_id
   CAPE_PATH=cape_path_id
   CAPE_EXAM=cape_exam_id
   CJCA_EXAM=cape_exam_id
   CJCA_EXAM=cape_exam_id
   ````

5. **Run the bot:**

   ```bash
   python bot.py
   ```

6. **Bot commands**
   Commands can be sent to the bot as a message
   These commands are available to the bot:
   - `!last_batch` The bot will respond with the date and time of the last batch of each exam.


## Configuration

- DISCORD_TOKEN: Your Discord bot token.
- DISCORD_CHANNEL_ID: The ID of the Discord channel where the bot will post updates.
- CBBH_PATH, CBBH_EXAM, CPTS_PATH, CPTS_EXAM, CDSA_PATH, CDSA_EXAM, CWEE_PATH, CWEE_EXAM, CAPE_PATH, CAPE_EXAM, CJCA_PATH, CJCA_EXAM: The IDs for the respective badges. If you do not have an ID, you can simply leave the variable empty. The bot will then set the number to 0.

You can find your Badge IDs here: [Hack The Box Academy - My Badges](https://academy.hackthebox.com/my-badges)

To get the ID of the badge, you have to share the badge.
Click on the "Share" link for the corresponding badge and then on "Get a shareable link"

You will get a URL like this:
https://academy.hackthebox.com/achievement/badge/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

The ID has the format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx


## License

This project is licensed under the MIT License






