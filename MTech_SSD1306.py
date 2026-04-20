import lgpio
import time
from PIL import Image

# --- SSD1306 CONSTANTS ---
SSD1306_I2C_ADDRESS = 0x3C
SSD1306_SETCONTRAST = 0x81
SSD1306_DISPLAYALLON_RESUME = 0xA4
SSD1306_NORMALDISPLAY = 0xA6
SSD1306_INVERTDISPLAY = 0xA7
SSD1306_DISPLAYOFF = 0xAE
SSD1306_DISPLAYON = 0xAF
SSD1306_SETDISPLAYCLOCKDIV = 0xD5
SSD1306_SETMULTIPLEX = 0xA8
SSD1306_SETDISPLAYOFFSET = 0xD3
SSD1306_SETSTARTLINE = 0x40
SSD1306_CHARGEPUMP = 0x8D
SSD1306_MEMORYMODE = 0x20
SSD1306_COLUMNADDR = 0x21
SSD1306_PAGEADDR = 0x22
SSD1306_COMSCANDEC = 0xC8
SSD1306_SEGREMAP = 0xA1
SSD1306_SETCOMPINS = 0xDA

# Hardware Scrolling Constants
SSD1306_ACTIVATE_SCROLL = 0x2F
SSD1306_DEACTIVATE_SCROLL = 0x2E
SSD1306_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1306_RIGHT_HORIZONTAL_SCROLL = 0x26
SSD1306_LEFT_HORIZONTAL_SCROLL = 0x27
SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL = 0x2A

DATA_MODE = 0x40
COMMAND_MODE = 0x00

class MTech_SSD1306:
    """
    Hardware driver for SSD1306 OLED displays using lgpio.
    Developed for Montana Tech CSCI 255/361.
    """
    def __init__(self, bus=1, address=SSD1306_I2C_ADDRESS, width=128, height=32):
        self.width = width
        self.height = height
        self.address = address
        self.pages = height // 8
        self._buffer = [0] * (width * self.pages)
        
        try:
            self.handle = lgpio.i2c_open(bus, address)
            self._initialize()
        except Exception as e:
            print(f"I2C Init Error: {e}")
            self.handle = -1

    def command(self, cmd):
        """Send a single command byte to the display."""
        lgpio.i2c_write_device(self.handle, [COMMAND_MODE, cmd])

    def _initialize(self):
        """Standard sequence to initialize the 128x32 OLED panel."""
        cmds = [
            SSD1306_DISPLAYOFF,
            SSD1306_SETDISPLAYCLOCKDIV, 0x80,
            SSD1306_SETMULTIPLEX, 0x1F, # 0x1F for 32 lines
            SSD1306_SETDISPLAYOFFSET, 0x00,
            SSD1306_SETSTARTLINE | 0x00,
            SSD1306_CHARGEPUMP, 0x14,
            SSD1306_MEMORYMODE, 0x00, # Horizontal Addressing Mode
            SSD1306_SEGREMAP,
            SSD1306_COMSCANDEC,
            SSD1306_SETCOMPINS, 0x02,
            SSD1306_SETCONTRAST, 0x8F,
            0xD9, 0xF1,
            0xDB, 0x40,
            SSD1306_DISPLAYALLON_RESUME,
            SSD1306_NORMALDISPLAY,
            SSD1306_DISPLAYON
        ]
        for c in cmds:
            self.command(c)

    # --- CORE GRAPHICS ---

    def draw_pixel(self, x, y, color, transmit=True):
        """
        Updates the local buffer and optionally transmits the 
        specific byte to the hardware immediately (Partial Update).
        Ideal for high-speed games like Pong.
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        page = y // 8
        bit = y % 8
        index = (page * self.width) + x

        # Update local software buffer
        if color:
            self._buffer[index] |= (1 << bit)
        else:
            self._buffer[index] &= ~(1 << bit)

        # Transmit only the modified byte to the OLED hardware
        if transmit:
            self.command(SSD1306_COLUMNADDR)
            self.command(x)       # Set Column Start Address
            self.command(x)       # Set Column End Address
            
            self.command(SSD1306_PAGEADDR)
            self.command(page)    # Set Page Start Address
            self.command(page)    # Set Page End Address

            # Send the updated byte from the buffer
            lgpio.i2c_write_device(self.handle, [DATA_MODE, self._buffer[index]])

    def set_pixel(self, x, y, color):
        """Modifies a pixel in the local buffer only (No I2C transmission)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            page = y // 8
            bit = y % 8
            index = (page * self.width) + x
            if color:
                self._buffer[index] |= (1 << bit)
            else:
                self._buffer[index] &= ~(1 << bit)

    def show(self):
        """Transfers the entire local buffer to the display hardware (Full Refresh)."""
        self.command(SSD1306_COLUMNADDR)
        self.command(0)
        self.command(self.width - 1)
        self.command(SSD1306_PAGEADDR)
        self.command(0)
        self.command(self.pages - 1)
        
        # Split buffer into 64-byte chunks for stable I2C transmission
        for i in range(0, len(self._buffer), 64):
            lgpio.i2c_write_device(self.handle, [DATA_MODE] + self._buffer[i:i+64])

    def load_image(self, image):
        """Converts and loads a PIL.Image object into the display buffer."""
        img = image.convert('1').resize((self.width, self.height))
        pix = img.load()
        self.clear_buffer()
        for y in range(self.height):
            for x in range(self.width):
                if pix[x, y]:
                    self.set_pixel(x, y, True)

    def clear_buffer(self):
        """Clears the software buffer in RAM. Does not affect the display."""
        self._buffer = [0] * len(self._buffer)

    def clear_screen(self):
        """Clears both the software buffer and the physical display (Heavy operation)."""
        self.clear_buffer()
        self.show()

    # --- HARDWARE FEATURES ---

    def start_scroll_right(self, start=0, stop=3):
        """Enables hardware-based horizontal scrolling to the right."""
        self.command(SSD1306_RIGHT_HORIZONTAL_SCROLL)
        self.command(0x00) # Dummy
        self.command(start)
        self.command(0x00) # Interval (0x00 = 5 frames)
        self.command(stop)
        self.command(0x00) # Dummy
        self.command(0xFF) # Dummy
        self.command(SSD1306_ACTIVATE_SCROLL)

    def stop_scroll(self):
        """Disables all hardware scrolling."""
        self.command(SSD1306_DEACTIVATE_SCROLL)

    def set_contrast(self, level):
        """Adjusts display brightness (0-255)."""
        self.command(SSD1306_SETCONTRAST)
        self.command(level & 0xFF)

    def close(self):
        """Cleans up the I2C handle and turns off the display."""
        if self.handle >= 0:
            self.clear_buffer()
            self.show()
            self.command(SSD1306_DISPLAYOFF)
            lgpio.i2c_close(self.handle)

# --- QUICK TEST ---
if __name__ == "__main__":
    oled = MTech_SSD1306()
    
    
    
    try:
        # Example 1: Loading an external image
        logo = Image.open("logoB.png")
        oled.load_image(logo)
        oled.show()
        time.sleep(2)

        # Example 2: Test scrolling
        oled.start_scroll_right()
        print("Scrolling...")
        time.sleep(5)
        oled.stop_scroll()
        
        oled.clear_buffer()
        oled.show() #or  oled.clear_screen()

        # Example 3: Comparing Full Update (show) 
        for i in range(32):
            oled.set_pixel(i, i, True) 
            oled.set_pixel(127-i, i, True)
            oled.show()
            time.sleep(0.01)

        oled.clear_screen() 
        time.sleep(1)

        # Partial Update (draw_pixel)
        for i in range(32):
            oled.draw_pixel(i, i, True) 
            oled.draw_pixel(127-i, i, True)
            time.sleep(0.1)
        
        # Example 4: Dynamic Contrast Test
        oled.load_image(logo)
        oled.show()

        for i in range(0, 255, 10):
            oled.set_contrast(i)
            time.sleep(0.5)           
        
  

    except KeyboardInterrupt:
        print("\nHardware process interrupted by user.")
    finally:
        oled.close()
        print("Hardware resources released.")