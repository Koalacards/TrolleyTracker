import discord
from discord.ui import Button, View

## URL buttons

invite_button = Button(
    label="Invite",
    style=discord.ButtonStyle.url,
    url="https://discord.com/api/oauth2/authorize?client_id=635586264921407522&permissions=2415995920&scope=bot%20applications.commands",
)

support_button = Button(
    label="Discord Server",
    style=discord.ButtonStyle.url,
    url="https://discord.gg/toontown",
)

github_button = Button(
    label="Github",
    style=discord.ButtonStyle.url,
    url="https://github.com/Koalacards/TrolleyTracker",
)

url_buttons = [invite_button, support_button, github_button]
url_view = View()
for button in url_buttons:
    url_view.add_item(button)