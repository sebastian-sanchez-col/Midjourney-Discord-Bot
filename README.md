# Midjourney-Discord-Bot
Bot that allows you to download an image and show it in a Python screen with the prompt

## Setup & Usage Steps

Follow these steps to get the bot running locally on a Windows machine:

1. **Create a virtual environment** (recommended for dependency isolation):
   ```powershell
   python -m venv mj_env
   ```

2. **Activate the environment**:
   ```powershell
   mj_env\Scripts\activate
   ```

3. **Install required packages**:
   ```powershell
   pip install discord.py requests
   pip install pillow
   ```
   *`discord.py`* provides the Discord client, *`requests`* is used for
   HTTP interactions with Midjourney or other APIs, and *`Pillow`* (PIL) is
   used to display images in a simple Python GUI.

4. **Run the bot script**:
   ```powershell
   python midjourney-bot.py
   ```

Once the bot is connected, you can trigger commands in a Discord server that
it has been added to (typically something like `/imagine prompt`). When an image
is retrieved, a window will open locally showing the image alongside its
prompt.
