#!/usr/bin/env python3
import csv
import os
import requests
import logging
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import discord
from discord.ext import tasks, commands

# Load environment variables from the .env file
load_dotenv()

# URL for fetching badge information
BADGE_URL = "https://academy.hackthebox.com/achievement/badge/"

# Directory and file paths
INSTALL_DIR =  os.getcwd()
LOG_DIR = os.path.join(INSTALL_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'bot.log') 
DATA_DIR = os.path.join(INSTALL_DIR, 'data')
BADGE_CSV = os.path.join(DATA_DIR, 'badges.csv')


# Initial setup
# Create the log directory if it does not exist
log_dir = True
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
    log_dir = False

# Set up logging with file rotation
# The log file size limit is set to 10 MB (maxBytes=10*1024*1024).
# Up to 5 backup log files will be kept (backupCount=5).
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
logging.basicConfig(handlers=[log_handler], level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if log_dir == False:
    logging.info(f"{LOG_DIR} created.")

# Create the data directory if it does not exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logging.info(f"{DATA_DIR} created.")

# create badges.csv and write the header line
if not os.path.isfile(BADGE_CSV):
    fields = [
        'timestamp', 
        'CBBH-Path', 
        'CBBH-Exam', 
        'CPTS-Path', 
        'CPTS-Exam', 
        'CDSA-Path', 
        'CDSA-Exam', 
        'CWEE-Path', 
        'CWEE-Exam',
        'CAPE-Path', 
        'CAPE-Exam',
        'CJCA-Path',
        'CJCA-Exam',       
        ]
    with open(BADGE_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(fields)
        logging.info(f"{BADGE_CSV} created")


# Discord bot token and channel ID from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))


# Badge IDs and symbols from environment variables
BADGES = {
    'CBBH': {
        'symbol': ":spider_web:",
        'path_id': os.getenv('CBBH_PATH'),
        'exam_id': os.getenv('CBBH_EXAM')
    },
    'CPTS': {
        'symbol': ":crossed_swords:",
        'path_id': os.getenv('CPTS_PATH'),
        'exam_id': os.getenv('CPTS_EXAM')
    },
    'CDSA': {
        'symbol': ":shield:",
        'path_id': os.getenv('CDSA_PATH'),
        'exam_id': os.getenv('CDSA_EXAM')
    },
    'CWEE': {
        'symbol': ":globe_with_meridians:",
        'path_id': os.getenv('CWEE_PATH'),
        'exam_id': os.getenv('CWEE_EXAM')
    },
    'CAPE': {
        'symbol': ":woman_mage:",
        'path_id': os.getenv('CAPE_PATH'),
        'exam_id': os.getenv('CAPE_EXAM')
    },
    'CJCA': {
        'symbol': ":woman_supervillain:",
        'path_id': os.getenv('CJCA_PATH'),
        'exam_id': os.getenv('CJCA_EXAM')
    }
}


# Function to fetch the last recorded badge numbers from the CSV file
def get_last_badge_numbers():
    try:
        with open(BADGE_CSV, "r") as f:
            last_line = f.readlines()[-1].strip()
        return last_line.split(',')
    except FileNotFoundError:
        logging.error("CSV file not found.")
        return [0] * (len(BADGES) * 2 + 1)
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
        return [0] * (len(BADGES) * 2 + 1)


# Function to fetch the current badge number from the website for a given badge ID
def fetch_badge_number(badge_id):
    if not badge_id:
        return '0'
    try:
        page = requests.get(f"{BADGE_URL}{badge_id}")
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup.find('span', class_='font-size-20 text-white').get_text()
    except requests.RequestException as e:
        logging.error(f"Error fetching badge number: {e}")
        return '0'


# Function to fetch the current badge numbers for all badges
def fetch_current_badge_numbers():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    badge_numbers = [timestamp]
    for badge in BADGES.values():
        badge_numbers.append(fetch_badge_number(badge['path_id']))
        badge_numbers.append(fetch_badge_number(badge['exam_id']))
    return badge_numbers


# Function to compare the last and current badge numbers
def compare_badge_numbers(last_badges, current_badges):
    return [int(current) - int(last) for last, current in zip(last_badges[1:], current_badges[1:])]


# Function to add the current badge numbers to the CSV file
def add_badge_numbers_to_csv(new_entry):
    try:
        with open(BADGE_CSV, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(new_entry)
    except Exception as e:
        logging.error(f"Error writing to CSV file: {e}")


# Function to generate a message detailing the changes in badge numbers
def generate_update_message(differences, current_badges):
    message = ""
    for i, (name, badge) in enumerate(BADGES.items()):
        path_diff, exam_diff = differences[2 * i], differences[2 * i + 1]
        path_num, exam_num = current_badges[2 * i + 1], current_badges[2 * i + 2]

        if badge['path_id'] or badge['exam_id']:
            message += f"{badge['symbol']} **{name}** \n"
            if badge['exam_id']:
                message += f"EXAM: {exam_num} {'**(+' + str(exam_diff) + ')**' if exam_diff != 0 else ''}\n"
            if badge['path_id']:
                message += f"PATH: {path_num} {'**(+' + str(path_diff) + ')**' if path_diff != 0 else ''}\n"
            message += "\n"

    message += f"*Last update: {current_badges[0]} UTC*"
    return message

# Function to get the last update times for each exam from the CSV file
def get_last_update_times():
    last_update_times = {}
    try:
        with open(BADGE_CSV, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                timestamp = row[0]
                for i, (name, badge) in enumerate(BADGES.items()):
                    if badge['exam_id']:
                        exam_num = row[2 * i + 2]
                        if name not in last_update_times or last_update_times[name][1] != exam_num:
                            last_update_times[name] = (timestamp, exam_num)
    except Exception as e:
        logging.error(f"Error reading CSV file: {e}")
    return last_update_times

# Set up Discord bot with default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Event handler for when the bot is ready
@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')
    send_status_message.start()

# Command to display the last batch update times for exams
@bot.command(name='last_batch')
async def last_batch(ctx):
    last_update_times = get_last_update_times()
    message = "Last Batch Update Times:\n"
    for name, (timestamp, _) in last_update_times.items():
        message += f"{BADGES[name]['symbol']} **{name}**: {timestamp} UTC\n"
    await ctx.send(message)
    logging.info('Message "Last Exam Batch run" sent to Discord')

# Task loop to send status message every hour
@tasks.loop(hours=1)
async def send_status_message():
    last_badge_numbers = get_last_badge_numbers()
    current_badge_numbers = fetch_current_badge_numbers()
    if last_badge_numbers[0] == "timestamp":
        add_badge_numbers_to_csv(current_badge_numbers)
        logging.info('Current badge numbers added to CSV')
    else:
        differences = compare_badge_numbers(last_badge_numbers, current_badge_numbers)
    
        # If there are updates, save the new numbers in the csv file and send a message
        if any(differences):

            # Add current badge numbers to CSV
            add_badge_numbers_to_csv(current_badge_numbers)
            logging.info('Current badge numbers added to CSV')

            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                message = generate_update_message(differences, current_badge_numbers)
                await channel.send(message)
                logging.info('Message sent to Discord')
        else:
            logging.info('No updates')


# Ensure the bot is ready before starting the task loop
@send_status_message.before_loop
async def before_send_status_message():
    await bot.wait_until_ready()

# Run the Discord bot with the provided token
bot.run(TOKEN)
