import ctypes
import ctypes.wintypes

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

# Use it directly
minimize_all_programs_builtin()