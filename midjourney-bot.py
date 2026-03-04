import discord
import requests
from PIL import Image, ImageTk
import tkinter as tk
from io import BytesIO
from queue import Queue
import threading
import re
import asyncio
import os
import uuid
from datetime import datetime

TOKEN = #DEIN_DISCORD_BOT_TOKEN_HIER_EINFÜGEN
CHANNEL_ID = #DEINE_DISCORD_KANAL_ID_HIER_EINFÜGEN

intents = discord.Intents.default()
intents.message_content = True

class ImageWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Midjourney Viewer")
        self.root.geometry("900x800")

        # Status
        self.status_label = tk.Label(
            root,
            text="Warte auf Bild...",
            font=("Arial", 14)
        )
        self.status_label.pack(pady=5)

        # Prompt direkt unter Status
        self.prompt_label = tk.Label(
            root,
            text="",
            font=("Arial", 12),
            wraplength=850,
            justify="left"
        )
        self.prompt_label.pack(pady=10)

        # Bild unter dem Prompt
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.img_tk = None
        self.queue = Queue()
        self.check_queue()

    def set_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def check_queue(self):
        while not self.queue.empty():
            url, prompt = self.queue.get()
            self.set_status("Neue Nachricht!")
            self.root.after(500, lambda u=url, p=prompt: self.download_and_show(u, p))
        self.root.after(100, self.check_queue)

    def download_and_show(self, url, prompt):
        try:
            self.set_status("Bild wird heruntergeladen")

            r = requests.get(url, timeout=30)
            r.raise_for_status()

            if not os.path.exists("images"):
                os.makedirs("images")
            
            unique_id = uuid.uuid4().hex[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"{timestamp}_{unique_id}.png"
            filepath = os.path.join("images", filename)

            with open(filepath, "wb") as f:
                f.write(r.content)
            print(f"Bild gespeichert in: {filepath}")

            img_data = BytesIO(r.content)
            pil_image = Image.open(img_data)
            pil_image.thumbnail((800, 800))
            self.img_tk = ImageTk.PhotoImage(pil_image)
            self.image_label.config(image=self.img_tk)

            # Prompt anzeigen
            if prompt.strip():
                self.prompt_label.config(text=f"Prompt:\n{prompt}")
            else:
                self.prompt_label.config(text="Prompt:\nKein Prompt gefunden")

            self.set_status("Warte auf Bild...")
            
        except Exception as e:
            self.set_status("Fehler beim Herunterladen")
            print("Fehler:", e)

    def add_data(self, url, prompt):
        self.queue.put((url, prompt))


class DiscordBot(discord.Client):
    def __init__(self, image_window, **kwargs):
        super().__init__(**kwargs)
        self.image_window = image_window

    async def on_ready(self):
        print("Bot ist bereit und verbunden.")
        print("Warte auf neue Bilder im Kanal...")

    async def on_message(self, message):
        if message.channel.id != CHANNEL_ID or not message.author.bot:
            return

        prompt_text = ""

        # 1️⃣ Normaler Text
        if message.content:
            prompt_text = message.content

        # 2️⃣ Embed (Midjourney nutzt oft das!)
        for embed in message.embeds:
            if embed.description:
                prompt_text = embed.description            

        # Optional: "/imagine prompt:" entfernen
        if prompt_text.lower().startswith("/imagine"):
            prompt_text = prompt_text.replace("/imagine", "").strip()
        
        match = re.search(r"\*\*(.*?)\*\*", prompt_text)
        if match:
            prompt_text = match.group(1).strip()

        for attachment in message.attachments:
            self.image_window.add_data(attachment.url, prompt_text)

        for embed in message.embeds:
            if embed.image:
                self.image_window.add_data(embed.image.url, prompt_text)
        


def run_discord_bot(image_window):
    bot = DiscordBot(image_window, intents=intents)
    asyncio.run(bot.start(TOKEN))


if __name__ == "__main__":
    root = tk.Tk()
    image_window = ImageWindow(root)

    threading.Thread(
        target=run_discord_bot,
        args=(image_window,),
        daemon=True
    ).start()

    root.mainloop()