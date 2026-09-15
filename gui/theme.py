"""
SecForge Theme Configuration
Modern dark cybersecurity-themed styling for the Tkinter GUI.
"""

# Color Palette - modern dark with subtle gradients
COLORS = {
    "bg_dark": "#0b0f19",
    "bg_medium": "#111827",
    "bg_card": "#151d2e",
    "bg_card_hover": "#1c2640",
    "bg_card_border": "#1e2d4a",
    "bg_input": "#0e1525",
    "bg_sidebar": "#0d1220",
    "bg_sidebar_hover": "#141c30",
    "accent_cyan": "#00e5ff",
    "accent_green": "#34d399",
    "accent_red": "#f87171",
    "accent_orange": "#fbbf24",
    "text_primary": "#e8ecf4",
    "text_secondary": "#8896b0",
    "text_muted": "#506080",
    "border": "#1a2540",
    "border_active": "#00e5ff",
    "success": "#34d399",
    "warning": "#fbbf24",
    "error": "#f87171",
    "info": "#60a5fa",
}

# Font Configuration - clean modern fonts
FONTS = {
    "title": ("Segoe UI", 24, "bold"),
    "subtitle": ("Segoe UI", 11),
    "heading": ("Segoe UI", 13, "bold"),
    "subheading": ("Segoe UI", 11, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "mono": ("Cascadia Code", 10),
    "mono_bold": ("Cascadia Code", 10, "bold"),
    "button": ("Segoe UI", 10, "bold"),
    "sidebar": ("Segoe UI", 11),
    "sidebar_active": ("Segoe UI", 11, "bold"),
    "card_title": ("Segoe UI", 13, "bold"),
    "card_desc": ("Segoe UI", 9),
    "status": ("Cascadia Code", 9),
    "card_icon": ("Segoe UI Symbol", 28),
}


def apply_theme(root):
    """Apply the modern dark cybersecurity theme to the root Tk window."""
    import tkinter.ttk as ttk

    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(".", background=COLORS["bg_dark"], foreground=COLORS["text_primary"],
                     borderwidth=0, focuscolor=COLORS["accent_cyan"])

    # Frames
    style.configure("TFrame", background=COLORS["bg_dark"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="flat")
    style.configure("Sidebar.TFrame", background=COLORS["bg_sidebar"])
    style.configure("Input.TFrame", background=COLORS["bg_input"])

    # Labels
    style.configure("TLabel", background=COLORS["bg_dark"],
                     foreground=COLORS["text_primary"], font=FONTS["body"])
    style.configure("CardTitle.TLabel", font=FONTS["card_title"],
                     foreground=COLORS["text_primary"], background=COLORS["bg_card"])
    style.configure("CardDesc.TLabel", font=FONTS["card_desc"],
                     foreground=COLORS["text_secondary"], background=COLORS["bg_card"])
    style.configure("CardIcon.TLabel", font=FONTS["card_icon"],
                     foreground=COLORS["accent_cyan"], background=COLORS["bg_card"])
    style.configure("Status.TLabel", font=FONTS["status"],
                     foreground=COLORS["accent_green"], background=COLORS["bg_dark"])
    style.configure("StatusError.TLabel", font=FONTS["status"],
                     foreground=COLORS["error"], background=COLORS["bg_dark"])
    style.configure("StatusWarn.TLabel", font=FONTS["status"],
                     foreground=COLORS["warning"], background=COLORS["bg_dark"])

    # Buttons
    style.configure("Accent.TButton", font=FONTS["button"],
                     background=COLORS["accent_cyan"], foreground=COLORS["bg_dark"],
                     borderwidth=0, padding=(18, 9))
    style.map("Accent.TButton",
              background=[("active", "#33ebff"), ("pressed", "#00b8d4")],
              foreground=[("active", COLORS["bg_dark"])])

    style.configure("Secondary.TButton", font=FONTS["button"],
                     background=COLORS["bg_card_hover"], foreground=COLORS["text_primary"],
                     borderwidth=1, padding=(14, 7))
    style.map("Secondary.TButton",
              background=[("active", COLORS["bg_card_border"])],
              foreground=[("active", COLORS["accent_cyan"])])

    style.configure("Success.TButton", font=FONTS["button"],
                     background=COLORS["accent_green"], foreground=COLORS["bg_dark"],
                     borderwidth=0, padding=(14, 7))
    style.map("Success.TButton",
              background=[("active", "#6ee7b7")])

    style.configure("Stop.TButton", font=FONTS["button"],
                     background=COLORS["accent_orange"], foreground=COLORS["bg_dark"],
                     borderwidth=0, padding=(14, 7))
    style.map("Stop.TButton",
              background=[("active", "#fcd34d")])

    # Sidebar button
    style.configure("Sidebar.TButton", font=FONTS["sidebar"],
                     background=COLORS["bg_sidebar"], foreground=COLORS["text_secondary"],
                     borderwidth=0, padding=(18, 11), anchor="w")
    style.map("Sidebar.TButton",
              background=[("active", COLORS["bg_sidebar_hover"]),
                          ("pressed", COLORS["bg_sidebar_hover"])],
              foreground=[("active", COLORS["accent_cyan"]),
                          ("pressed", COLORS["accent_cyan"])])

    # Entry
    style.configure("TEntry", fieldbackground=COLORS["bg_input"],
                     foreground=COLORS["text_primary"], borderwidth=1,
                     insertcolor=COLORS["accent_cyan"], padding=8)
    style.map("TEntry",
              fieldbackground=[("focus", COLORS["bg_medium"])],
              bordercolor=[("focus", COLORS["accent_cyan"])])

    # Combobox
    style.configure("TCombobox", fieldbackground=COLORS["bg_input"],
                     foreground=COLORS["text_primary"], borderwidth=1,
                     padding=8)
    style.map("TCombobox",
              fieldbackground=[("readonly", COLORS["bg_input"])],
              foreground=[("readonly", COLORS["text_primary"])])
    style.configure("TCombobox.Downarrow", background=COLORS["bg_card"])

    # Treeview (tables)
    style.configure("Treeview", background=COLORS["bg_input"],
                     foreground=COLORS["text_primary"], fieldbackground=COLORS["bg_input"],
                     borderwidth=0, font=FONTS["mono"], rowheight=30)
    style.configure("Treeview.Heading", background=COLORS["bg_card"],
                     foreground=COLORS["accent_cyan"], font=FONTS["mono_bold"],
                     borderwidth=0, relief="flat")
    style.map("Treeview",
              background=[("selected", COLORS["bg_card_hover"])],
              foreground=[("selected", COLORS["accent_cyan"])])
    style.map("Treeview.Heading",
              background=[("active", COLORS["bg_card_hover"])])

    # Scrollbar
    style.configure("Vertical.TScrollbar", background=COLORS["bg_card_hover"],
                     troughcolor=COLORS["bg_dark"], borderwidth=0,
                     arrowcolor=COLORS["text_muted"])
    style.map("Vertical.TScrollbar",
              background=[("active", COLORS["bg_card_border"])])

    # Separator
    style.configure("TSeparator", background=COLORS["border"])

    # Notebook (tabs)
    style.configure("TNotebook", background=COLORS["bg_dark"], borderwidth=0)
    style.configure("TNotebook.Tab", background=COLORS["bg_card"],
                     foreground=COLORS["text_secondary"], padding=(18, 9),
                     font=FONTS["body"])
    style.map("TNotebook.Tab",
              background=[("selected", COLORS["bg_medium"])],
              foreground=[("selected", COLORS["accent_cyan"])])

    # Checkbutton
    style.configure("TCheckbutton", background=COLORS["bg_dark"],
                     foreground=COLORS["text_primary"], font=FONTS["body"])

    # Radiobutton
    style.configure("TRadiobutton", background=COLORS["bg_dark"],
                     foreground=COLORS["text_primary"], font=FONTS["body"])

    return style
