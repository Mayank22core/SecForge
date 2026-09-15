"""
SecForge - Cybersecurity Toolkit
A desktop application with 5 practical security tools.

Usage:
    python main.py
"""

import tkinter as tk


def main():
    """Launch the SecForge application."""
    root = tk.Tk()

    # Set window icon if available
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    # Import and create the app
    from gui.app import SecForgeApp
    app = SecForgeApp(root)

    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
