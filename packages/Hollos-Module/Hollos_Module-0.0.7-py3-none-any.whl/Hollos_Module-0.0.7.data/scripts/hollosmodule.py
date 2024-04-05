"""
The MIT License (MIT)

Copyright (c) 2023-present Hollo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

----------------

![logo](https://devhollo.github.io/!assets/dev_assets/hollosmodule/img/logo.png)
see the Github page [here](https://github.com/DevHollo/Hollos-Module)
"""
from typing import (
    Literal,
    Union,
    TypeAlias,
    NoReturn,
    Self
)

def check_for_latest_hollosmodule_version():
    """
    Checks if you have the latest version of Hollo's Module. If not, it installs the latest version.
    """
    from importlib import metadata as pypi
    import subprocess
    import requests
    import logging
    try:
        user_ver = str(pypi.version('Hollos-Module'))
        pypi_ver = str(requests.get("https://pypi.org/pypi/Hollos-Module/json").json()['info']['version'])
        if not user_ver == pypi_ver:
            subprocess.run(['pip', 'install', f'hxml=={pypi_ver}'])
        else:
            pass
    except pypi.PackageNotFoundError as e:
        logging.error(f"Package HollosModule not found: {e}")
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve version from PyPI for HollosModule: {e}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install HollosModule package: {e}")

class DiscordAPI:
    def __init__(self, *args, **kwargs) -> None:
        """
        This is for simple Discord stuff like sending webhook messages!
        """
        pass

    @staticmethod
    def webhook_send_msg(msg: str, webhook_url: str) -> None:
        """
        Send a message to a Discord webhook.

        Args:
            message (str): The message to send.
            webhook_url (str): The URL of the Discord webhook.

        Raises:
            requests.HTTPError: If there's an error sending the webhook message.
        """
        import requests as rq
        import json as j
        payload = {
            "content": msg
        }
        payload_dat = j.dumps(payload)
        hdrs = {"Content-Type": "application/json"}
        response = rq.post(webhook_url, data=payload_dat, headers=hdrs)
        if response.status_code == 204:
            pass
        else:
            raise rq.HTTPError(f"Error sending webhook message. (Status code: {response.status_code})")

class Text:
    def __init__(self, *args, **kwargs):
        """
        Custom text styling!
        """
        #from sty import fg, Style, RgbFg, rs, ef
        #from colorama import Fore, Style
        
        def redtext(txt: str | None):
            """
            Makes text red
            """
            from sty import RgbFg, Style, fg
            fg.cus = Style(RgbFg(222, 8, 11))
            return fg.cus + txt + fg.rs
        self.red = redtext

        def orangetext(txt: str | None):
            """
            Makes text orange
            """
            from sty import fg, Style, RgbFg
            fg.cus = Style(RgbFg(255, 115, 0))
            return fg.cus + txt + fg.rs
        self.orange = orangetext

        def yellowtext(txt: str | None):
            """
            Makes text yellow
            """
            from sty import fg, Style, RgbFg
            fg.cus = Style(RgbFg(255, 213, 0))
            return fg.cus + txt + fg.rs
        self.yellow = yellowtext

        def greentext(txt: str | None):
            """
            Makes text green
            """
            from sty import fg, Style, RgbFg
            fg.cus = Style(RgbFg(0, 210, 21))
            return fg.cus + txt + fg.rs
        self.green = greentext

        def bluetext(txt: str | None):
            """
            Makes text blue
            """
            from sty import fg, RgbFg, Style
            fg.cus = Style(RgbFg(53, 59, 222))
            return fg.cus + txt + fg.rs
        self.blue = bluetext

        def purpletext(txt: str | None):
            """
            Makes text purple
            """
            from sty import fg, Style, RgbFg
            fg.cus = Style(RgbFg(175, 17, 218))
            return fg.cus + txt + fg.rs
        self.purple = purpletext

        def cyantext(txt: str | None):
            """
            Makes text cyan
            """
            from sty import fg, Style, RgbFg
            fg.cus = Style(RgbFg(80, 221, 246))
            return fg.cus + txt + fg.rs
        self.cyan = cyantext

        def pinktext(txt: str | None):
            """
            Makes text pink
            """
            from sty import fg, Style, RgbFg
            fg.cus = Style(RgbFg(255, 54, 198))
            return fg.cus + txt + fg.rs
        self.pink = pinktext

        def customrgbtext(txt: str | None, rgb: tuple | list = (255,255,255)):
            """
            Makes text custom RGB
            """
            from sty import fg, Style, RgbFg
            if type(rgb) == list:
                rgb = list(rgb)
            fg.cus = Style(RgbFg(int(rgb[0]), int(rgb[1]), int(rgb[2])))
            return fg.cus + txt + fg.rs
        self.custom_rgb = customrgbtext

        def blacktext(txt: str | None):
            """
            Makes text black (looks gray in vscode console)
            """
            from sty import Style, fg, RgbFg
            fg.cus = Style(RgbFg(0, 0, 0))
            return fg.cus + txt + fg.rs
        self.black = blacktext

        def italictext(txt: str | None):
            """
            Makes text italic
            """
            from sty import ef
            return ef.italic + txt + ef.rs
        self.italic = italictext

        def boldtext(txt: str | None):
            """
            Makes text bold
            """
            from sty import ef
            return ef.bold + txt + ef.rs
        self.bold = boldtext

        def strikethroughtext(txt: str | None):
            """
            Makes text strikethrough
            """
            from sty import ef
            return ef.strike + txt + ef.rs
        self.strikethrough = strikethroughtext

        def blinktext(txt: str | None):
            """
            Makes text blink (doesn\'t currently work in the vscode console)
            """
            from sty import ef
            return ef.blink + txt + ef.rs
        self.blink = blinktext

        def underlinetext(txt: str | None):
            """
            Makes text underlined
            """
            from sty import ef
            return ef.underl + txt + ef.rs
        self.underline = underlinetext

    @staticmethod
    def reverse(txt: str | None):
        """
        Returns a reversed version of `txt`
        """
        return txt[::-1]
    
    @staticmethod
    def to_human_readable_number(number: int):
        """
        Makes a number human readable
        ### Examples:
        - 10000 would turn into 10,000
        """
        return f"{number:,}"
    
class Math:
    def __init__(self, *args, **kwargs):
        """
        A simple math class.
        """
        pass

    @staticmethod
    def factorial(n: int | float):
        """
        Get the factorial of `n`
        """
        try:
            fact = 1
            if n < 0:
                raise ValueError("Number cannot be negative.")
            for i in range(1, n+1):
                fact = fact * i
            return fact
        except (TypeError, ValueError, OverflowError, FloatingPointError):
            return None
        
    @staticmethod
    def to_the_power_of(base: int | float, exp: int | float, mod: int | float = None):
        """
        Get `base` to the power of `exp`
        """
        try:
            if mod is None:
                return base**exp
            else:
                return base**exp % mod
        except (TypeError, ValueError, OverflowError, FloatingPointError):
            return None


def inputstr(prompt) -> str:
    """
    Returns input that will return a string
    """
    return str(input(prompt))

def inputint(prompt) -> int:
    """
    Returns input that will return a integer
    """
    return int(input(prompt))

def inputfloat(prompt) -> float:
    """
    Returns input that will return a float
    """
    return float(input(prompt))

def maskedinput(prompt, maskchar: str = "*") -> str:
    """
    #### This GIF shows what this function does:
    ![Example](https://devhollo.github.io/!assets/dev_assets/hollosmodule/img/masked_input.gif)
    """
    import getpass4
    return str(getpass4.getpass(prompt, char=maskchar))

def joinstr(*values) -> str:
    """
    Returns a string of the joined values
    """
    result = ""
    for val in values:
        result += str(val)
    return result

class loop:
    """
    ### This is for a `for` loop
    -----
    ## Examples:
    ----
    ### Without
    ```py
    for i in range(3):
        print(f"Hello World! [{i}]")
    ```
    Output:
    ![without](https://devhollo.github.io/!assets/dev_assets/hollosmodule/img/without_loop_class.png)
    ----
    ### With
    ```py
    from hollosmodule import loop

    for i in loop(3):
        print(f"Hello World! [{i}]")
    ```
    Output:
    ![with](https://devhollo.github.io/!assets/dev_assets/hollosmodule/img/with_loop_class.png)
    """
    def __init__(self, number: int):
        self.number = number

    def __iter__(self):
        self.current = 1
        return self

    def __next__(self):
        if self.current > self.number:
            raise StopIteration
        else:
            self.current += 1
            return self.current - 1

def userinfo(json_indent: int = None):
    """
    Returns info in json data like this:
    ```
    {
        \'pc-name\': \'PCNAME\',
        \'user\': \'USER\'
    }
    ```
    """
    import getpass
    import socket
    import json
    data = {'pc-name': socket.gethostname(), 'user': getpass.getuser()}
    dumped_data = None
    if json_indent is None or json_indent == 0:
        dumped_data = json.dumps(data)
        return json.loads(dumped_data)
    else:
        dumped_data = json.dumps(data, indent=json_indent)
        return json.loads(dumped_data)
    
class Exceptions:
    def __init__(self, *args, **kwargs):
        """
        Some custom Exceptions!
        """
        pass

    class UnsupportedFileExtensionError(Exception):
        """
        unsupported file extension
        """
        def __init__(self, file_extension: str, error_code=None):
            self.file_extension = file_extension
            self.error_code = error_code
            self.message = f"File extension '{file_extension}' is not supported."
            super().__init__(self.message)

        def __str__(self):
            if self.error_code:
                return f"{self.message} (Error code: {self.error_code})"
            else:
                return self.message

    class ConnectionError(Exception):
        def __init__(self, message="Connection error occurred", error_code=None):
            self.message = message
            self.error_code = error_code
            super().__init__(self.message)

        def __str__(self):
            if self.error_code:
                return f"{self.message} (Error code: {self.error_code})"
            else:
                return self.message
            
    class LessThanError(Exception):
        """
        A error for if a number is less than something
        """
        def __init__(self, message: str, error_level: Literal['mini', 'small', 'medium', 'large', 'fatal'] = ''):
            super().__init__(message)
            self.message = None
            if error_level == '':
                self.message = message
            else:
                self.message = f"[{error_level.capitalize()} Error] {message}"

        def __str__(self):
            return f'{self.message}'
    
class HTTPS:
    def __init__(self, *args, **kwargs):
        """
        HTTPS related stuff!
        """
        pass

    @staticmethod
    def download_image_from_url(url: str, save_path: str):
        """
        used download a image from a url.
        ### Supported files:
        - .png
        - .jpg
        - .jpeg
        - .gif
        - .webp
        """
        import requests as rq
        import os
        response = rq.get(url)
        file_extension = os.path.splitext(url)[1]
        supported_files = [
            '.png',
            '.jpg',
            '.jpeg',
            '.gif',
            '.webp'
        ]
        if file_extension in supported_files:
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
            else:
                raise rq.HTTPError(f"Error downloading image. (Status code: {response.status_code})")
        else:
            raise Exceptions().UnsupportedFileExtensionError(file_extension)
        
class Decorators:
    def __init__(self, *args, **kwargs):
        """
        Some Useful Decorators!
        """
        pass

    @staticmethod
    def delay_execution(time_to_wait: int | float):
        """
        delays running the function by the specified seconds.
        """
        import time
        def decorator(func):
            def wrapper(*args, **kwargs):
                time.sleep(time_to_wait)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def log_execution(to_log: str | None = None, log_to: Literal['console', 'file'] = 'console', file: str = '_logs.log'):
        """
        Log after the function is run based on `log_to`.
        """
        import logging
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                log_message = None
                if to_log is None:
                    log_message = f" Function \'{func.__name__}()\' executed. ::END"
                else:
                    log_message = f' {to_log} ::END'
                if log_to == 'console':
                    print(log_message)
                elif log_to == 'file':
                    logging.basicConfig(filename=file, level=logging.INFO)
                    logging.info(log_message)
                else:
                    raise ValueError('Param log_to must be \'console\', \'file\', or None.')
                return result
            return wrapper
        return decorator

class Files:
    def __init__(self, *args, **kwargs):
        """
        File handling things!
        """
        pass

    @staticmethod
    def convert_image(old_file: str, new_file: str, delete_old_file: bool = False):
        """
        Convert `old_file` to `new_file`
        ### Supported files:
        - .png
        - .jpg
        - .jpeg
        """
        from PIL import Image
        import os
        supported_files = [
            '.png',
            '.jpg',
            '.jpeg'
        ]
        _, old_ext = os.path.splitext(old_file)
        _, new_ext = os.path.splitext(new_file)
        if old_ext.lower() not in supported_files:
            raise Exceptions().UnsupportedFileExtensionError(f"Error: Unsupported file format: {old_ext}")
        if new_ext.lower() not in supported_files:
            raise Exceptions().UnsupportedFileExtensionError(f"Error: Unsupported file format: {new_ext}")
        with Image.open(old_file) as img:
            if img.mode == 'RGBA' and new_ext.lower() in ('.jpg', '.jpeg'):
                img = img.convert('RGB')
            img.save(new_file)
        if delete_old_file:
            os.remove(os.path.abspath(old_file))

class Units:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def kilometers_to_miles(km: int | float, return_as: Literal['int', 'float', 'str'] = 'float') -> Union[list, tuple]:
        """
        Converts kilometers to miles
        """
        miles = None
        if not isinstance(km, (int, float)):
            raise TypeError("km must be a number")
        if km <= 0:
            raise ValueError("km must be greater than 0")
        miles = km / 1.609344
        if return_as.lower() == 'float':
            return miles
        elif return_as.lower() == 'int':
            if miles >= 1:
                return int(miles)
            else:
                raise Exceptions().LessThanError("miles is less than 0, please set return_as to float")
        elif return_as.lower() == 'str':
            return str()
        
def hexdecimals(return_as: Literal['list', 'tuple'] = 'list', _max: int = 255) -> Union[list, tuple]:
    """
    Returns hexdecimals and their values

    Example:
    ```py
    from hollosmodule import hexdecimals

    decimals = hexdecimals('list', 255)

    print(decimals[0]) # output: 0 = 0x00
    ```
    """
    hdecimals = None
    if return_as.lower() == 'list':
        hdecimals = []
    elif return_as.lower() == 'tuple':
        hdecimals = ()
    else:
        raise ValueError(f"return_as cannot be \'{return_as}\'")
    for i in loop(_max):
        if return_as.lower() == 'list':
            hdecimals.append(f"{i} = 0x{i:02X}")
        else:
            hdecimals += (f"{i} = 0x{i:02X}",)
    return hdecimals


class QRcode:
    def __init__(self, *args, **kwargs):
        """
        Generate QR Codes! Example:
        ```py
        from hollosmodule import QRcode

        qr = QRcode()

        qr.make_qr_code("Hello, World!")

        qr.save_qr("qr_code.png")
        ```
        """
        pass

    def make_qr_code(self, data: str | None, *, fill_color: str = "#000000", background_color: str = "#ffffff", box_size: int = 10, border: int = 4, fit: bool = True, version: int = 1):
        """
        Make a QR code.
        """
        try:
            import qrcode.main, qrcode.constants
            if not version == 1:
                version = 1
            else:
                pass
            self.__qrraw = qrcode.main.QRCode(
                version=version,
                error_correction=qrcode.constants.ERROR_CORRECT_Q,
                box_size=box_size,
                border=border,
            )
            self.__qrraw.add_data(data)
            self.__qrraw.make(fit=True)
            self.__qrimg = self.__qrraw.make_image(fill_color=fill_color, back_color=background_color)
        except Exception as e:
            raise Exception(e)

    def save_qr(self, p: str, *args, **kwargs):
        """
        Save QR code.
        """
        try:
            self.__qrimg.save(p)
            self.fp = p
        except Exception as e:
            raise Exception(e)
        
    def delete_qr(self, *args, **kwargs):
        """
        Delete the QR code.
        """
        import os
        if self.fp:
            os.remove(os.path.abspath(self.fp))
        else:
            raise FileNotFoundError("File not found")
        
    def visualize(self, *args, **kwargs):
        self.__qrimg.show()

class WinOS:
    """
    Commands for the Windows OS!
    """
    def __init__(self: Self, *args, **kwargs):
        pass

    @staticmethod
    def exit(__status: TypeAlias | str | int | None = None, /) -> NoReturn:
        """
        Exit the console/app
        """
        import sys
        sys.exit(__status)

    @staticmethod
    def pause(hide: bool = True, /) -> None:
        """
        This method pauses the script execution until the user presses a key. It optionally hides the `Press any key to continue...` message.
        """
        import os
        if hide is True:
            os.system("pause > nul")
        elif hide is False:
            os.system("pause")
        else:
            raise ValueError("Error with kw \'hide\'")
        
    @staticmethod
    def timeout(t: int | float, /, *, nobreak: bool = True, hide: bool = False) -> None:
        """
        This method waits for a specified amount of time (in seconds). It can optionally hide the countdown timer and/or prevent users from breaking out of the wait by pressing a key.
        """
        import os
        if nobreak is True:
            if hide is True:
                os.system(f"timeout /t {t} /nobreak > nul")
            elif hide is False:
                os.system(f"timeout /t {t} /nobreak")
        elif nobreak is False:
            if hide is True:
                os.system(f"timeout /t {t} > nul")
            elif hide is False:
                os.system(f"timeout /t {t}")
        else:
            raise ValueError("Error with keywords in func \'WinOS().timeout()\'")
        
    @staticmethod
    def cls() -> None:
        """
        Clear the console
        """
        import os
        os.system("cls")
    
    @staticmethod
    def cmd(command: str | None, /) -> None:
        """
        Run a command
        """
        import os
        os.system(command)