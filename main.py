from typing import Final
import os
import re

import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord import Intents, Client, TextChannel, Message, Embed

from responses import get_response  # Assuming you have a function to handle responses

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# Step 1: Bot Setup with correct intents
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# Dictionary to store ticket data
ticket_data = []

# List to hold id's of channels waiting on a resolution response
waiting_for_resolution = []


@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    user_message: str = message.content
    message_embedded: list = message.embeds

    # Get the channel id
    channel_id = message.channel.id


    try:
        # When the ticket is made and the form info is displayed
        if "Please wait, a Geek will contact you" in user_message:
            ticket_info = await handle_form_submission(message)
            new_info = {"id": channel_id, "info": ticket_info}
            ticket_info.append(new_info)

        for embed in message_embedded:
            embed_list = embed.to_dict()
            if "Support team ticket controls" in embed_list.get("description", ""):
                await prompt_resolution(message)

        # Check if we are waiting for resolution details in this channel
        if channel_id in waiting_for_resolution:
            # Save the message content as the resolution details
            print("1")
            resolution_details = user_message
            print(resolution_details)

            print("2")
            for item in ticket_data:
                if item["id"] == channel_id:
                    item["info"].append(resolution_details)
                    print(item)


            # TODO Seems to be grabbing the bot message as the reply and returning blank


            print("3")
            # Reset the flag
            waiting_for_resolution.remove(channel_id)

            return

    except Exception as e:
        print(e)


async def handle_form_submission(message: Message) -> list:
    try:
        embeds = message.embeds  # return list of embeds
        for embed in embeds:
            embed_as_dict = embed.to_dict()
            # If the first dict item is 'footer', then it is not the correct embed; continue
            if 'footer' in embed_as_dict:
                continue
            if "description" in embed_as_dict:
                # Get the information string from dict
                data = embed_as_dict["description"]
                # Split the string
                temp = data.split("```\n", 10)
                # Grab the data from temp and put it into info Starting from the second item
                # skip every other. This will ignore the labels and only get the entered info.
                info = temp[1::2]
                # Remove trailing ''' from last itme
                info[4] = info[4][:-3]

                # Split name into first and last name
                #temp = info[2]
                # first_name = temp.split(',')

                return info
    except Exception as e:
        print(e)
        return ["Error"]


async def prompt_resolution(message: Message) -> None:
    try:
        response: str = "Detail how you helped the customer resolve their issue:"
        await message.channel.send(response)
        # Set the flag to track the next message
        waiting_for_resolution.append(message.channel.id)
        print(waiting_for_resolution)
    except Exception as e:
        print(e)


# Step 2: Define event for channel creation
@client.event
async def on_guild_channel_create(channel):
    if isinstance(channel, TextChannel):
        category_id = 1221862228777631776  # Replace with your category ID
        category = discord.utils.get(channel.guild.categories, id=category_id)
        if category and channel.category == category:
            print(f'Channel created: {channel.name} in category {category.name}')


# Step 3: Handling bot startup
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')


# Step 5: Main entry point
def main() -> None:
    client.run(TOKEN)


if __name__ == '__main__':
    main()
