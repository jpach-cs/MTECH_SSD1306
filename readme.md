![MTECH_SSD1306](logo.png)

---

# MTECH_SSD1306

A high-performance, educational OLED display driver for Raspberry Pi 3-5, optimized for real-time applications and teaching Embedded Systems at Montana Tech.

---

## Overview

In advanced Embedded Systems courses at **Montana Tech**, students move beyond simple LEDs to complex peripheral communication. The SSD1306 128x32 OLED display is a staple for teaching the **I2C protocol**, bitwise operations, and memory mapping.

While popular libraries like `Adafruit_CircuitPython_SSD1306` are powerful, they often hide the underlying hardware logic behind heavy abstraction layers. 

**MTECH_SSD1306** is a lightweight, "hybrid" driver built on top of `lgpio`. It bridges the gap between high-level graphics and low-level register manipulation, making it the perfect tool for high-speed projects like **Pong**, **real-time sensors**, or **custom emulators**.

---

## Key Features

- **Hybrid Update Logic** Supports both `show()` (full buffer refresh) and `draw_pixel()` (immediate hardware update). The latter allows for ultra-fast rendering necessary for real-time games by transmitting only the modified bytes.
  
- **Optimized for lgpio** Built to work seamlessly with modern Raspberry Pi environments (Pi 4 & 5), ensuring stability and low CPU overhead compared to deprecated libraries.

- **Educational Transparency** Uses globally defined hardware constants to match the official **SSD1306 datasheet**, allowing students to correlate code directly with technical documentation.

- **PIL/Pillow Integration** Includes a `load_image()` method to display PNG/BMP graphics while maintaining the ability to perform raw bitwise pixel manipulation.

- **Hardware Scrolling & Contrast** Built-in support for hardware-level scrolling (zero CPU load) and dynamic contrast adjustment via I2C commands.

---

## Installation

```bash
# Clone this repository
git clone [https://github.com/jpach-cs/MTECH_SSD1306](https://github.com/jpach-cs/MTECH_SSD1306)

# Navigate into the repository
cd MTECH_SSD1306

# Install dependencies (Pillow for image support)
sudo apt-get install python3-pil

# Install the library
sudo python3 -m pip install .