# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text.
"""

import busio
import board
import random
import time
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
from fourwire import FourWire
from adafruit_st7789 import ST7789
import adafruit_dht

import os
import socketpool
import wifi

import adafruit_ntp

from utils import *
import asyncio

BORDER_WIDTH = 20
TEXT_SCALE = 3
wifi_ssid = os.getenv("CIRCUITPY_WIFI_SSID")
wifi_password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
font_file_big = "Minecraft-Regular-20.bdf"
font_file_small = "Minecraft-Regular-10.bdf"
fast = False # Fast mode doesn't render background

lat = -3518
long = 3984

# Release any resources currently in use for the displays
displayio.release_displays()
spi = busio.SPI(clock=board.GP18, MOSI=board.GP19)
"""
# I think this is useless
print("Setting up SPI for 24MHz")
while not spi.try_lock():
    pass
spi.configure(baudrate=24000000)  # Configure SPI for 24MHz
spi.unlock()
print("SPI setup complete")
"""
# Set up display SPI bus
tft_cs = board.GP17
tft_dc = board.GP20
tft_rst = board.GP21
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)

# Set up display
display = ST7789(display_bus, width=320, height=240, rotation=270, auto_refresh=True)
display.auto_refresh = False # Don't show bg yet
dht = adafruit_dht.DHT11(board.GP27)

# Make the display context
splash = displayio.Group()
display.root_group = splash


# Load fonts
font_big = False
font_small = False

bg_bitmap = False

async def load_fonts():
    global font_big, font_small
    font_big = bitmap_font.load_font(font_file_big)
    font_small = bitmap_font.load_font(font_file_small)

# Show background texture
async def show_bg():
    global bg_bitmap
    if bg_bitmap is False: 
        bg_bitmap = displayio.OnDiskBitmap("/dirt.bmp")
    bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_bitmap.pixel_shader, x=0, y=0)
    splash.insert(0, bg_sprite)
main_label = label.Label(
    terminalio.FONT,
    text="Loading...",
    color=0xFFFFFF,
    scale=2,
    anchor_point=(0.5, 0.5),
    anchored_position=(display.width // 2, display.height // 2),
)
splash.append(main_label)
display.refresh()
# Set up WiFi
async def setup_wifi():
    if wifi_ssid is None:
        print("WiFi credentials are kept in settings.toml, please add them there!")
        main_label.text = "No WiFi creds\nCheck log"
        display.refresh()
        return
    try:
        wifi.radio.connect(wifi_ssid, wifi_password)
    except Exception:
        print("Failed to connect to WiFi with provided credentials")
        main_label.text = "Failed to connect to WiFi"
        display.refresh()


pool = socketpool.SocketPool(wifi.radio)
ntp = adafruit_ntp.NTP(pool, tz_offset=-7, cache_seconds=3600)

# Run both tasks in parallel
async def main():
    print("Loading fonts")
    await load_fonts()
    if not fast:
        print("Loading bg")
        await show_bg()
    print("Connecting to WiFi")
    await setup_wifi()
    print("WiFi connected")
    print("Starting NTP")
    # Wait for NTP to sync
    while True:
        try:
            ntp.datetime
            break
        except OSError:
            print("NTP sync failed, retrying...")
            await asyncio.sleep(1)
    print("NTP synced")
    splash.remove(main_label)

asyncio.run(main())



color_palette = displayio.Palette(4)
color_palette[0] = 0xFFFFFF # Clock
color_palette[1] = 0xFFFFFF # Date
color_palette[2] = 0x00FF00 # Lat
color_palette[3] = 0xFF0000 # Long



def render_text(text, font, x, y, color=0xFFFFFF):
    text_area = label.Label(
        font,
        text=text,
        color=color,
        scale=TEXT_SCALE,
        anchor_point=(0.5, 0.5),
        anchored_position=(x, y),
    )
    splash.append(text_area)
    return text_area

clock_text = render_text(get_clock_text(ntp), font_big, display.width // 2, 30, color=color_palette[0])
date_text = render_text(get_date_text(ntp), font_small, display.width // 2, 70, color=color_palette[1])
lat_text = render_text(prep_loc(lat), font_big, display.width // 2, 140, color=color_palette[2])
long_text = render_text(prep_loc(long), font_big, display.width // 2, 200, color=color_palette[3])
# display.auto_refresh = True # Don't show bg yet
display.refresh()
while True:
    time.sleep(2)
    try:
        # Read DHT sensor
        temperature = dht.temperature
        humidity = dht.humidity
        if temperature is None or humidity is None:
            raise RuntimeError("Failed to read DHT sensor")
        lat = temperature
        long = humidity
        # print("Temperature: {} C".format(temperature))
        # print("Humidity: {}%".format(humidity))
    except RuntimeError as e:
        print("{}".format(e))
        continue
    # lat += random.randint(-50, 50)
    # long += random.randint(-50, 50)
    lat_text.text = str(int((lat*9/5)+32))+"F"
    long_text.text = str(long)+"%"
    # lat_text.text = prep_loc(lat)
    # long_text.text = prep_loc(long)

    # Update clock and date
    clock_txt = get_clock_text(ntp)
    date_txt = get_date_text(ntp)
    if(clock_text.text != clock_txt): clock_text.text = clock_txt
    if(date_text.text != date_txt): date_text.text = date_txt
    date_text.text = get_date_text(ntp)
    display.refresh()
