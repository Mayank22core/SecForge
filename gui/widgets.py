"""
SecForge Custom Widgets
Reusable UI components for the cybersecurity toolkit.
"""

import tkinter as tk
import tkinter.ttk as ttk
from gui.theme import COLORS, FONTS


class ToolCard(ttk.Frame):
    """A card widget used on the dashboard to represent a tool."""

    def __init__(self, parent, icon, title, description, on_open=None, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)

        self.configure(padding=20)
        self.columnconfigure(0, weight=1)

        self._on_open = on_open

        # Icon
        icon_label = ttk.Label(self, text=icon, style="CardIcon.TLabel")
        icon_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Title
        title_label = ttk.Label(self, text=title, style="CardTitle.TLabel")
        title_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        # Description
        desc_label = ttk.Label(self, text=description, style="CardDesc.TLabel",
                               wraplength=220, justify="left")
        desc_label.grid(row=2, column=0, sticky="w", pady=(0, 14))

        # Open button
        open_btn = ttk.Button(self, text="Open Tool  \u2192", style="Accent.TButton",
                              command=self._click)
        open_btn.grid(row=3, column=0, sticky="w")

        self._open_btn = open_btn

        # Hover effects for the entire card
        for widget in [self, icon_label, title_label, desc_label]:
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._click)

    def _click(self, event=None):
        if self._on_open:
            self._on_open()

    def _on_enter(self, event):
        self.configure(style="Card.TFrame")
        self.configure(cursor="hand2")
        self._open_btn.configure(cursor="hand2")

    def _on_leave(self, event):
        self.configure(cursor="")
        self._open_btn.configure(cursor="")


class OutputPanel(ttk.Frame):
    """A terminal-like output panel with scrollback."""

    def __init__(self, parent, height=12, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.text = tk.Text(
            self,
            height=height,
            bg=COLORS["bg_input"],
            fg=COLORS["accent_green"],
            font=FONTS["mono"],
            insertbackground=COLORS["accent_cyan"],
            selectbackground=COLORS["accent_cyan"],
            selectforeground=COLORS["bg_dark"],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent_cyan"],
            wrap="word",
            state="disabled",
            padx=12,
            pady=10,
        )
        self.text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text.configure(yscrollcommand=scrollbar.set)

        # Tag configurations for colored output
        self.text.tag_configure("success", foreground=COLORS["success"])
        self.text.tag_configure("error", foreground=COLORS["error"])
        self.text.tag_configure("warning", foreground=COLORS["warning"])
        self.text.tag_configure("info", foreground=COLORS["info"])
        self.text.tag_configure("cyan", foreground=COLORS["accent_cyan"])
        self.text.tag_configure("muted", foreground=COLORS["text_muted"])
        self.text.tag_configure("bold", font=FONTS["mono_bold"])

    def append(self, message, tag=None):
        """Append a line of text to the output panel."""
        self.text.configure(state="normal")
        self.text.insert("end", message + "\n", tag if tag else ())
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self):
        """Clear all output text."""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")

    def set_text(self, message, tag=None):
        """Replace all text in the panel."""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", message, tag if tag else ())
        self.text.configure(state="disabled")


class StatusBar(ttk.Frame):
    """A status bar at the bottom of tool panels."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(1, weight=1)

        self.indicator = tk.Canvas(self, width=10, height=10,
                                    bg=COLORS["accent_green"], highlightthickness=0)
        self.indicator.grid(row=0, column=0, padx=(8, 6), pady=6)

        self.status_label = ttk.Label(self, text="Ready", style="Status.TLabel")
        self.status_label.grid(row=0, column=1, sticky="w", pady=6)

        self.detail_label = ttk.Label(self, text="", style="Status.TLabel")
        self.detail_label.grid(row=0, column=2, sticky="e", padx=8, pady=6)

    def set_status(self, text, state="ready"):
        """Update the status bar text and indicator color."""
        color_map = {
            "ready": COLORS["accent_green"],
            "running": COLORS["accent_cyan"],
            "error": COLORS["error"],
            "warning": COLORS["warning"],
            "info": COLORS["info"],
        }
        style_map = {
            "ready": "Status.TLabel",
            "running": "Status.TLabel",
            "error": "StatusError.TLabel",
            "warning": "StatusWarn.TLabel",
            "info": "Status.TLabel",
        }
        self.indicator.configure(bg=color_map.get(state, COLORS["accent_green"]))
        self.status_label.configure(text=text, style=style_map.get(state, "Status.TLabel"))

    def set_detail(self, text):
        self.detail_label.configure(text=text)


class ScrollableTreeview(ttk.Frame):
    """A Treeview with scrollbars."""

    def __init__(self, parent, columns, headings, widths=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self, columns=columns, show="headings",
                                  selectmode="browse", **kwargs)

        for i, col in enumerate(columns):
            self.tree.heading(col, text=headings[i] if i < len(headings) else col)
            if widths and i < len(widths):
                self.tree.column(col, width=widths[i], minwidth=60)
            else:
                self.tree.column(col, width=120, minwidth=60)

        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

    def insert(self, values, tags=()):
        """Insert a row and return the item id."""
        return self.tree.insert("", "end", values=values, tags=tags)

    def clear(self):
        """Remove all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_all_values(self):
        """Return all row values as a list of tuples."""
        return [self.tree.item(item)["values"] for item in self.tree.get_children()]
