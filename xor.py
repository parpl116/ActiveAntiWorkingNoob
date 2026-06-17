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
    
    input_text = ""  # Track typed text
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key in allowed_keys:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # Check if typed text is "bobek"
                        if input_text.lower() == "bobek":
                            print("Password correct! Exiting...")
                            running = False
                        input_text = ""  # Clear input after enter
                    else:
                        char = chr(event.key).upper() if event.mod & pygame.KMOD_SHIFT else chr(event.key)
                        input_text += char
                        print(f"Key: {char}")
                elif event.key == pygame.K_q and event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT:
                    running = False
            # Ignore all mouse events
            elif event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEWHEEL):
                pass
        
        # Disable mouse by warping it to corner (extra measure)
        pygame.mouse.set_pos(0, 0)
        
        # Draw everything
        screen.fill((0, 0, 0))
        
        # Draw title text
        title_text = font.render("RESTRICTED ACCESS", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 60))
        screen.blit(title_text, title_rect)
        
        # Draw instruction text
        instruction_text = small_font.render("Type password and press Enter to exit", True, (255, 255, 255))
        instruction_rect = instruction_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(instruction_text, instruction_rect)
        
        # Draw input text (shown as asterisks for password feel)
        masked_text = "*" * len(input_text)
        input_display = small_font.render(f"Password: {masked_text}", True, (0, 255, 0))
        input_rect = input_display.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 60))
        screen.blit(input_display, input_rect)
        
        # Draw emergency exit hint
        emergency_text = small_font.render("Emergency Exit: Ctrl+Shift+Q", True, (128, 128, 128))
        emergency_rect = emergency_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 120))
        screen.blit(emergency_text, emergency_rect)
        
        # Continuously force window to stay on top
        if sys.platform == 'win32':
            user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, 
                              SWP_NOMOVE | SWP_NOSIZE)
        
        pygame.display.flip()
    
    pygame.quit()

create_restricted_window()