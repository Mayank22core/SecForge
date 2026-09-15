"""
SecForge Main Application
Desktop GUI for the cybersecurity toolkit using Tkinter.
"""

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import threading

from gui.theme import COLORS, FONTS, apply_theme
from gui.widgets import ToolCard, OutputPanel, StatusBar, ScrollableTreeview


class SecForgeApp:
    """Main application class for SecForge."""

    # Tool identifiers
    DASHBOARD = "dashboard"
    NETWORK_SCANNER = "network_scanner"
    TRACEROUTE = "traceroute"
    MAC_SPOOFER = "mac_spoofer"
    AES_TOOL = "aes_tool"
    PASSWORD_CRACKER = "password_cracker"

    def __init__(self, root):
        self.root = root
        self.root.title("SecForge - Cybersecurity Toolkit")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS["bg_dark"])

        # Apply theme
        self.style = apply_theme(self.root)

        # State
        self.current_view = self.DASHBOARD
        self.sidebar_buttons = {}
        self._stop_events = {}

        # Build the layout: header at top, status at bottom,
        # sidebar + main fill remaining space
        self._build_header()
        self._build_status_bar()
        self._build_body()

        # Show dashboard initially
        self._show_view(self.DASHBOARD)

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self):
        """Build the top header bar."""
        header = tk.Frame(self.root, bg=COLORS["bg_dark"], height=64)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Left side: Title
        title_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        title_frame.pack(side="left", padx=24, pady=0)

        tk.Label(title_frame, text="SECForge", font=FONTS["title"],
                 fg=COLORS["accent_cyan"], bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(title_frame, text="  Cybersecurity Toolkit",
                 font=FONTS["subtitle"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(side="left", padx=(6, 0),
                                             pady=(8, 0))

        # Right side: System status
        status_frame = tk.Frame(header, bg=COLORS["bg_dark"])
        status_frame.pack(side="right", padx=24)

        tk.Canvas(status_frame, width=8, height=8, bg=COLORS["accent_green"],
                  highlightthickness=0).pack(side="left", padx=(0, 6))
        tk.Label(status_frame, text="SYSTEM READY", font=FONTS["status"],
                 fg=COLORS["accent_green"], bg=COLORS["bg_dark"]).pack(side="left")

        # Separator line
        tk.Frame(self.root, height=1, bg=COLORS["border"]).pack(side="top", fill="x")

    def _build_body(self):
        """Build the body area containing sidebar and main content."""
        # Body frame fills all remaining space between header and status bar
        body = tk.Frame(self.root, bg=COLORS["bg_dark"])
        body.pack(side="top", fill="both", expand=True)

        self._build_sidebar(body)
        self._build_main_area(body)

    def _build_sidebar(self, parent):
        """Build the left sidebar with navigation buttons."""
        self.sidebar = tk.Frame(parent, bg=COLORS["bg_sidebar"], width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        logo_frame.pack(fill="x", padx=18, pady=(22, 10))

        tk.Label(logo_frame, text="\u26a0", font=("Segoe UI Symbol", 26),
                 fg=COLORS["accent_cyan"], bg=COLORS["bg_sidebar"]).pack(side="left")
        tk.Label(logo_frame, text="MENU", font=FONTS["subheading"],
                 fg=COLORS["text_muted"], bg=COLORS["bg_sidebar"]).pack(
                     side="left", padx=(10, 0))

        # Separator
        tk.Frame(self.sidebar, height=1, bg=COLORS["border"]).pack(
            fill="x", padx=18, pady=8)

        # Navigation items
        nav_items = [
            (self.DASHBOARD, "\u2302  Dashboard"),
            (self.NETWORK_SCANNER, "\u25b6  Network Scanner"),
            (self.TRACEROUTE, "\u27b8  Traceroute"),
            (self.MAC_SPOOFER, "\u25c6  MAC Spoof"),
            (self.AES_TOOL, "\u26bf  AES Tool"),
            (self.PASSWORD_CRACKER, "\u2693  Hash Cracker"),
        ]

        for view_id, label in nav_items:
            btn_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], cursor="hand2")
            btn_frame.pack(fill="x", padx=10, pady=2)

            btn_label = tk.Label(btn_frame, text=label, font=FONTS["sidebar"],
                                  fg=COLORS["text_secondary"],
                                  bg=COLORS["bg_sidebar"], anchor="w",
                                  padx=14, pady=10)
            btn_label.pack(fill="x")

            btn_frame.bind("<Button-1>", lambda e, vid=view_id: self._show_view(vid))
            btn_label.bind("<Button-1>", lambda e, vid=view_id: self._show_view(vid))

            # Hover effects
            def make_enter(fr, lb):
                def on_enter(e):
                    fr.configure(bg=COLORS["bg_sidebar_hover"])
                    lb.configure(bg=COLORS["bg_sidebar_hover"],
                                 fg=COLORS["accent_cyan"])
                return on_enter

            def make_leave(fr, lb, vid):
                def on_leave(e):
                    if self.current_view != vid:
                        fr.configure(bg=COLORS["bg_sidebar"])
                        lb.configure(bg=COLORS["bg_sidebar"],
                                     fg=COLORS["text_secondary"])
                return on_leave

            btn_frame.bind("<Enter>", make_enter(btn_frame, btn_label))
            btn_frame.bind("<Leave>", make_leave(btn_frame, btn_label, view_id))
            btn_label.bind("<Enter>", make_enter(btn_frame, btn_label))
            btn_label.bind("<Leave>", make_leave(btn_frame, btn_label, view_id))

            self.sidebar_buttons[view_id] = (btn_frame, btn_label)

        # Spacer
        tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"]).pack(
            fill="both", expand=True)

        # Version info
        tk.Label(self.sidebar, text="v1.0.0", font=FONTS["small"],
                 fg=COLORS["text_muted"], bg=COLORS["bg_sidebar"]).pack(pady=(0, 16))

    def _build_main_area(self, parent):
        """Build the main content area."""
        self.main_frame = tk.Frame(parent, bg=COLORS["bg_dark"])
        self.main_frame.pack(side="left", fill="both", expand=True)

        # Container for views
        self.view_container = tk.Frame(self.main_frame, bg=COLORS["bg_dark"])
        self.view_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Create all views
        self.views = {}
        self._create_dashboard()
        self._create_network_scanner_view()
        self._create_traceroute_view()
        self._create_mac_spoofer_view()
        self._create_aes_tool_view()
        self._create_password_cracker_view()

    def _build_status_bar(self):
        """Build the bottom status bar."""
        # Separator above status bar
        tk.Frame(self.root, height=1, bg=COLORS["border"]).pack(side="bottom", fill="x")
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side="bottom", fill="x")

    def _show_view(self, view_id):
        """Show a specific view and update sidebar selection."""
        # Stop any running operations
        for vid, stop_event in self._stop_events.items():
            if stop_event is not None:
                stop_event.set()

        self.current_view = view_id

        # Update sidebar button styles
        for vid, (fr, lb) in self.sidebar_buttons.items():
            if vid == view_id:
                fr.configure(bg=COLORS["bg_sidebar_hover"])
                lb.configure(bg=COLORS["bg_sidebar_hover"],
                             fg=COLORS["accent_cyan"])
            else:
                fr.configure(bg=COLORS["bg_sidebar"])
                lb.configure(bg=COLORS["bg_sidebar"],
                             fg=COLORS["text_secondary"])

        # Hide all views
        for widget in self.view_container.winfo_children():
            widget.pack_forget()

        # Show the selected view
        if view_id in self.views:
            self.views[view_id].pack(fill="both", expand=True)

        # Update status
        view_names = {
            self.DASHBOARD: "Dashboard",
            self.NETWORK_SCANNER: "Network Scanner",
            self.TRACEROUTE: "Traceroute",
            self.MAC_SPOOFER: "MAC Address Spoofer",
            self.AES_TOOL: "AES Encryption/Decryption",
            self.PASSWORD_CRACKER: "Password Hash Cracker",
        }
        self.status_bar.set_status(
            f"Viewing: {view_names.get(view_id, view_id)}", "ready"
        )

    # ========================
    # DASHBOARD
    # ========================

    def _create_dashboard(self):
        """Create the dashboard view with tool cards."""
        frame = tk.Frame(self.view_container, bg=COLORS["bg_dark"])

        # Scrollable canvas for cards
        canvas = tk.Canvas(frame, bg=COLORS["bg_dark"], highlightthickness=0,
                           bd=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS["bg_dark"])

        # Fix: bind canvas resize to inner frame width
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        scrollable.bind("<Configure>", _on_frame_configure)
        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Section title
        header_frame = tk.Frame(scrollable, bg=COLORS["bg_dark"])
        header_frame.pack(fill="x", padx=32, pady=(28, 6))
        tk.Label(header_frame, text="SELECT A SECURITY TOOL",
                 font=FONTS["heading"], fg=COLORS["text_primary"],
                 bg=COLORS["bg_dark"]).pack(anchor="w")
        tk.Label(header_frame, text="Choose a tool from the cards below or the sidebar",
                 font=FONTS["subtitle"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(anchor="w", pady=(2, 0))

        # Cards grid
        cards_frame = tk.Frame(scrollable, bg=COLORS["bg_dark"])
        cards_frame.pack(fill="x", padx=32, pady=(20, 0))
        cards_frame.columnconfigure((0, 1, 2), weight=1)

        tools = [
            ("\U0001f310", "Network Scanner",
             "Discover active devices on a local network using ARP requests.",
             self.NETWORK_SCANNER),
            ("\U0001f310", "Traceroute",
             "View network hops between your machine and a destination.",
             self.TRACEROUTE),
            ("\U0001f4b9", "MAC Address Spoofer",
             "Change the MAC address of a network interface for authorized testing.",
             self.MAC_SPOOFER),
            ("\U0001f510", "AES Encryption Tool",
             "Encrypt and decrypt text/files using AES-256-GCM.",
             self.AES_TOOL),
            ("\U0001f510", "Password Hash Cracker",
             "Test password hashes against an offline wordlist.",
             self.PASSWORD_CRACKER),
        ]

        for i, (icon, title, desc, view_id) in enumerate(tools):
            row = i // 3
            col = i % 3
            card = ToolCard(
                cards_frame,
                icon=icon,
                title=title,
                description=desc,
                on_open=lambda vid=view_id: self._show_view(vid),
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Disclaimer footer
        footer_frame = tk.Frame(scrollable, bg=COLORS["bg_dark"])
        footer_frame.pack(fill="x", padx=32, pady=(32, 20))
        tk.Frame(footer_frame, height=1, bg=COLORS["border"]).pack(
            fill="x", pady=(0, 10))
        tk.Label(
            footer_frame,
            text="Use SecForge only on systems, devices, and networks you own "
                 "or have explicit permission to test.",
            font=FONTS["small"], fg=COLORS["text_muted"], bg=COLORS["bg_dark"],
            wraplength=700, justify="left",
        ).pack(anchor="w")

        self.views[self.DASHBOARD] = frame

    # ========================
    # NETWORK SCANNER
    # ========================

    def _create_network_scanner_view(self):
        """Create the network scanner tool panel."""
        frame = tk.Frame(self.view_container, bg=COLORS["bg_dark"])

        # Header
        hdr = tk.Frame(frame, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(hdr, text="\u25b6  Network Scanner",
                 font=FONTS["heading"], fg=COLORS["text_primary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(hdr, text="ARP-based local network discovery",
                 font=FONTS["subtitle"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(side="left", padx=(14, 0))

        # Input row
        input_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        input_frame.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(input_frame, text="Network Range (CIDR):",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.ns_network_entry = ttk.Entry(input_frame, width=25)
        self.ns_network_entry.pack(side="left", padx=(8, 0))
        self.ns_network_entry.insert(0, "192.168.1.0/24")

        # Try to detect local network
        try:
            from tools.network_scanner import get_local_network
            detected = get_local_network()
            self.ns_network_entry.delete(0, "end")
            self.ns_network_entry.insert(0, detected)
        except Exception:
            pass

        self.ns_scan_btn = ttk.Button(input_frame, text="\u25b6  Scan",
                                       style="Accent.TButton",
                                       command=self._ns_start_scan)
        self.ns_scan_btn.pack(side="left", padx=(14, 0))

        self.ns_stop_btn = ttk.Button(input_frame, text="\u25a0  Stop",
                                       style="Stop.TButton",
                                       command=self._ns_stop_scan)
        self.ns_stop_btn.pack(side="left", padx=(8, 0))

        self.ns_clear_btn = ttk.Button(input_frame, text="Clear",
                                        style="Secondary.TButton",
                                        command=self._ns_clear)
        self.ns_clear_btn.pack(side="left", padx=(8, 0))

        # Results table
        self.ns_tree = ScrollableTreeview(
            frame,
            columns=("ip", "mac", "status"),
            headings=("IP Address", "MAC Address", "Status"),
            widths=(180, 220, 120),
        )
        self.ns_tree.pack(fill="both", expand=True, padx=24, pady=(0, 10))

        # Output panel
        tk.Label(frame, text="Output:", font=FONTS["subheading"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(
                     anchor="w", padx=24)
        self.ns_output = OutputPanel(frame, height=6)
        self.ns_output.pack(fill="x", padx=24, pady=(4, 10))

        # Status bar
        self.ns_status = StatusBar(frame)
        self.ns_status.pack(fill="x", padx=24, pady=(0, 10))

        # State
        self._ns_stop_event = threading.Event()
        self._stop_events[self.NETWORK_SCANNER] = self._ns_stop_event

        self.views[self.NETWORK_SCANNER] = frame

    def _ns_start_scan(self):
        """Start the network scan in a background thread."""
        network = self.ns_network_entry.get().strip()
        if not network:
            messagebox.showwarning("Input Required", "Please enter a network range.")
            return

        # Validate CIDR format
        from tools.network_scanner import validate_network
        net, err = validate_network(network)
        if err:
            messagebox.showerror("Invalid Input", err)
            return

        self._ns_stop_event.clear()
        self.ns_tree.clear()
        self.ns_output.clear()
        self.ns_scan_btn.configure(state="disabled")
        self.ns_status.set_status("Scanning network...", "running")
        self.status_bar.set_status("Scanning network...", "running")

        def scan_thread():
            try:
                from tools.network_scanner import scan_network, check_scapy

                ok, msg = check_scapy()
                if not ok:
                    self.root.after(0, lambda: self._ns_error(msg))
                    return

                def on_device(ip, mac, status):
                    self.root.after(0, lambda i=ip, m=mac, s=status:
                                    self._ns_add_device(i, m, s))

                results, elapsed = scan_network(
                    network, callback=on_device,
                    stop_event=self._ns_stop_event
                )

                self.root.after(0, lambda r=results, t=elapsed:
                                self._ns_complete(r, t))

            except Exception as e:
                self.root.after(0, lambda err=str(e): self._ns_error(err))

        threading.Thread(target=scan_thread, daemon=True).start()

    def _ns_add_device(self, ip, mac, status):
        """Add a device to the results table."""
        self.ns_tree.insert((ip, mac, status))
        self.ns_output.append(f"[+] {ip}  {mac}  {status}", "success")

    def _ns_complete(self, results, elapsed):
        """Handle scan completion."""
        self.ns_scan_btn.configure(state="normal")
        count = len(results)
        self.ns_status.set_status(
            f"Scan complete: {count} device(s) found in {elapsed:.1f}s", "ready"
        )
        self.status_bar.set_status("Scan complete", "ready")
        self.ns_output.append(
            f"\n--- Scan complete: {count} device(s) in {elapsed:.1f}s ---", "cyan"
        )

    def _ns_error(self, message):
        """Handle scan error."""
        self.ns_scan_btn.configure(state="normal")
        self.ns_status.set_status(f"Error: {message}", "error")
        self.status_bar.set_status("Scan error", "error")
        self.ns_output.append(f"[!] {message}", "error")

    def _ns_stop_scan(self):
        """Stop the running scan."""
        self._ns_stop_event.set()
        self.ns_scan_btn.configure(state="normal")
        self.ns_status.set_status("Scan stopped by user", "warning")
        self.status_bar.set_status("Scan stopped", "warning")

    def _ns_clear(self):
        """Clear the scanner results."""
        self.ns_tree.clear()
        self.ns_output.clear()
        self.ns_status.set_status("Ready", "ready")

    # ========================
    # TRACEROUTE
    # ========================

    def _create_traceroute_view(self):
        """Create the traceroute tool panel."""
        frame = tk.Frame(self.view_container, bg=COLORS["bg_dark"])

        # Header
        hdr = tk.Frame(frame, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(hdr, text="\u27b8  Traceroute",
                 font=FONTS["heading"], fg=COLORS["text_primary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(hdr, text="Trace network path to destination",
                 font=FONTS["subtitle"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(side="left", padx=(14, 0))

        # Input row
        input_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        input_frame.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(input_frame, text="Destination:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.tr_dest_entry = ttk.Entry(input_frame, width=30)
        self.tr_dest_entry.pack(side="left", padx=(8, 0))
        self.tr_dest_entry.insert(0, "google.com")

        self.tr_start_btn = ttk.Button(input_frame, text="\u25b6  Start",
                                        style="Accent.TButton",
                                        command=self._tr_start)
        self.tr_start_btn.pack(side="left", padx=(14, 0))

        self.tr_stop_btn = ttk.Button(input_frame, text="\u25a0  Stop",
                                       style="Stop.TButton",
                                       command=self._tr_stop)
        self.tr_stop_btn.pack(side="left", padx=(8, 0))

        self.tr_clear_btn = ttk.Button(input_frame, text="Clear",
                                        style="Secondary.TButton",
                                        command=self._tr_clear)
        self.tr_clear_btn.pack(side="left", padx=(8, 0))

        # Results table
        self.tr_tree = ScrollableTreeview(
            frame,
            columns=("hop", "ip", "hostname", "time"),
            headings=("Hop", "IP Address", "Hostname", "Time (ms)"),
            widths=(60, 180, 180, 100),
        )
        self.tr_tree.pack(fill="both", expand=True, padx=24, pady=(0, 10))

        # Output panel
        tk.Label(frame, text="Output:", font=FONTS["subheading"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(
                     anchor="w", padx=24)
        self.tr_output = OutputPanel(frame, height=6)
        self.tr_output.pack(fill="x", padx=24, pady=(4, 10))

        # Status bar
        self.tr_status = StatusBar(frame)
        self.tr_status.pack(fill="x", padx=24, pady=(0, 10))

        # State
        self._tr_stop_event = threading.Event()
        self._stop_events[self.TRACEROUTE] = self._tr_stop_event

        self.views[self.TRACEROUTE] = frame

    def _tr_start(self):
        """Start traceroute in a background thread."""
        dest = self.tr_dest_entry.get().strip()
        if not dest:
            messagebox.showwarning("Input Required", "Please enter a destination.")
            return

        from tools.traceroute import validate_destination
        valid, err = validate_destination(dest)
        if not valid:
            messagebox.showerror("Invalid Input", err)
            return

        self._tr_stop_event.clear()
        self.tr_tree.clear()
        self.tr_output.clear()
        self.tr_start_btn.configure(state="disabled")
        self.tr_status.set_status(f"Tracing route to {dest}...", "running")
        self.status_bar.set_status("Traceroute in progress...", "running")

        def trace_thread():
            try:
                from tools.traceroute import run_traceroute

                def on_hop(hop, ip, hostname, time_ms):
                    self.root.after(0, lambda h=hop, i=ip, hn=hostname, t=time_ms:
                                    self._tr_add_hop(h, i, hn, t))

                results = run_traceroute(
                    dest, callback=on_hop,
                    stop_event=self._tr_stop_event
                )

                self.root.after(0, lambda r=results: self._tr_complete(r))

            except Exception as e:
                self.root.after(0, lambda err=str(e): self._tr_error(err))

        threading.Thread(target=trace_thread, daemon=True).start()

    def _tr_add_hop(self, hop, ip, hostname, time_ms):
        """Add a hop to the results table."""
        self.tr_tree.insert((hop, ip, hostname, time_ms))
        self.tr_output.append(f"  {hop}   {ip}   {hostname}   {time_ms} ms", "info")

    def _tr_complete(self, results):
        """Handle traceroute completion."""
        self.tr_start_btn.configure(state="normal")
        count = len(results)
        self.tr_status.set_status(
            f"Traceroute complete: {count} hop(s)", "ready"
        )
        self.status_bar.set_status("Traceroute complete", "ready")
        self.tr_output.append(f"\n--- Trace complete: {count} hop(s) ---", "cyan")

    def _tr_error(self, message):
        """Handle traceroute error."""
        self.tr_start_btn.configure(state="normal")
        self.tr_status.set_status(f"Error: {message}", "error")
        self.status_bar.set_status("Traceroute error", "error")
        self.tr_output.append(f"[!] {message}", "error")

    def _tr_stop(self):
        """Stop the traceroute."""
        self._tr_stop_event.set()
        self.tr_start_btn.configure(state="normal")
        self.tr_status.set_status("Traceroute stopped", "warning")
        self.status_bar.set_status("Traceroute stopped", "warning")

    def _tr_clear(self):
        """Clear traceroute results."""
        self.tr_tree.clear()
        self.tr_output.clear()
        self.tr_status.set_status("Ready", "ready")

    # ========================
    # MAC SPOOFER
    # ========================

    def _create_mac_spoofer_view(self):
        """Create the MAC address spoofer panel."""
        frame = tk.Frame(self.view_container, bg=COLORS["bg_dark"])

        # Header
        hdr = tk.Frame(frame, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(hdr, text="\u25c6  MAC Address Spoofer",
                 font=FONTS["heading"], fg=COLORS["text_primary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(hdr, text="Change MAC address for authorized testing",
                 font=FONTS["subtitle"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(side="left", padx=(14, 0))

        # Interface selection
        iface_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        iface_frame.pack(fill="x", padx=24, pady=(8, 10))

        tk.Label(iface_frame, text="Network Interface:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.mac_iface_var = tk.StringVar()
        self.mac_iface_combo = ttk.Combobox(
            iface_frame, textvariable=self.mac_iface_var,
            state="readonly", width=35
        )
        self.mac_iface_combo.pack(side="left", padx=(8, 0))

        ttk.Button(
            iface_frame, text="\u21bb  Refresh Interfaces",
            style="Secondary.TButton", command=self._mac_refresh
        ).pack(side="left", padx=(12, 0))

        # Current MAC display
        mac_info_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        mac_info_frame.pack(fill="x", padx=24, pady=(4, 10))

        tk.Label(mac_info_frame, text="Current MAC Address:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.mac_current_label = tk.Label(
            mac_info_frame, text="--:--:--:--:--:--",
            font=FONTS["heading"], fg=COLORS["accent_cyan"],
            bg=COLORS["bg_dark"]
        )
        self.mac_current_label.pack(side="left", padx=(8, 0))

        # New MAC entry
        new_mac_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        new_mac_frame.pack(fill="x", padx=24, pady=(4, 10))

        tk.Label(new_mac_frame, text="New MAC Address:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.mac_new_entry = ttk.Entry(new_mac_frame, width=22)
        self.mac_new_entry.pack(side="left", padx=(8, 0))

        ttk.Button(
            new_mac_frame, text="\u2684  Random MAC",
            style="Secondary.TButton", command=self._mac_random
        ).pack(side="left", padx=(12, 0))

        ttk.Button(
            new_mac_frame, text="\u25b6  Change MAC",
            style="Accent.TButton", command=self._mac_change
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            new_mac_frame, text="\u21ba  Restore Original",
            style="Success.TButton", command=self._mac_restore
        ).pack(side="left", padx=(8, 0))

        # Output panel
        output_hdr = tk.Frame(frame, bg=COLORS["bg_dark"])
        output_hdr.pack(fill="x", padx=24, pady=(10, 0))
        tk.Label(output_hdr, text="Output:", font=FONTS["subheading"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(
                     side="left")
        ttk.Button(output_hdr, text="Clear", style="Secondary.TButton",
                   command=lambda: self.mac_output.clear()).pack(side="right")
        self.mac_output = OutputPanel(frame, height=10)
        self.mac_output.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        # Status bar
        self.mac_status = StatusBar(frame)
        self.mac_status.pack(fill="x", padx=24, pady=(0, 10))

        # State: store original MACs during the session
        self._mac_originals = {}
        self._mac_stop_event = threading.Event()
        self._stop_events[self.MAC_SPOOFER] = self._mac_stop_event

        # Auto-load interfaces
        self.root.after(100, self._mac_refresh)

        self.views[self.MAC_SPOOFER] = frame

    def _mac_refresh(self):
        """Refresh the list of network interfaces."""
        try:
            from tools.mac_spoofer import get_interfaces, is_admin

            self.mac_output.append("--- Refreshing interfaces ---", "muted")

            if not is_admin():
                self.mac_output.append(
                    "[!] Not running as administrator. Some operations may be limited.",
                    "warning"
                )

            interfaces = get_interfaces()

            if not interfaces:
                self.mac_output.append("[!] No network interfaces found.", "warning")
                self.mac_iface_combo['values'] = []
                return

            names = [i["name"] for i in interfaces]
            self.mac_iface_combo['values'] = names

            if names:
                self.mac_iface_combo.current(0)
                self._mac_on_interface_select()

            # Bind selection change
            self.mac_iface_combo.bind("<<ComboboxSelected>>",
                                       lambda e: self._mac_on_interface_select())

            for iface in interfaces:
                self.mac_output.append(
                    f"  {iface['name']}: {iface['mac']}", "info"
                )

            self.mac_status.set_status(
                f"Found {len(interfaces)} interface(s)", "ready"
            )

        except Exception as e:
            self.mac_output.append(f"[!] Error: {e}", "error")

    def _mac_on_interface_select(self):
        """Update current MAC display when interface selection changes."""
        name = self.mac_iface_var.get()
        if not name:
            return

        try:
            from tools.mac_spoofer import get_current_mac
            mac = get_current_mac(name)
            if mac:
                self.mac_current_label.configure(text=mac.upper())
                # Store original MAC for restore
                if name not in self._mac_originals:
                    self._mac_originals[name] = mac
            else:
                self.mac_current_label.configure(text="Could not retrieve")
        except Exception:
            self.mac_current_label.configure(text="Error")

    def _mac_random(self):
        """Generate and fill in a random MAC address."""
        from tools.mac_spoofer import generate_random_mac
        random_mac = generate_random_mac().upper()
        self.mac_new_entry.delete(0, "end")
        self.mac_new_entry.insert(0, random_mac)
        self.mac_output.append(f"Generated random MAC: {random_mac}", "cyan")

    def _mac_change(self):
        """Change the MAC address of the selected interface."""
        iface = self.mac_iface_var.get()
        new_mac = self.mac_new_entry.get().strip()

        if not iface:
            messagebox.showwarning("Input Required",
                                    "Please select a network interface.")
            return
        if not new_mac:
            messagebox.showwarning("Input Required",
                                    "Please enter or generate a new MAC address.")
            return

        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm MAC Change",
            "Changing the MAC address may temporarily disconnect "
            "your network connection. Continue?"
        )
        if not confirm:
            return

        self.mac_output.append(f"Changing MAC on {iface} to {new_mac}...", "info")
        self.mac_status.set_status("Changing MAC address...", "running")

        def change_thread():
            try:
                from tools.mac_spoofer import change_mac

                # Store original if not already stored
                if iface not in self._mac_originals:
                    from tools.mac_spoofer import get_current_mac
                    orig = get_current_mac(iface)
                    if orig:
                        self._mac_originals[iface] = orig

                success, msg = change_mac(iface, new_mac)
                tag = "success" if success else "error"
                self.root.after(0, lambda m=msg, t=tag: (
                    self.mac_output.append(
                        f"[{'+' if success else '!'}] {m}", t),
                    self.mac_status.set_status(m, "ready" if success else "error"),
                    self._mac_on_interface_select() if success else None,
                ))
            except Exception as e:
                self.root.after(0, lambda err=str(e): (
                    self.mac_output.append(f"[!] Error: {err}", "error"),
                    self.mac_status.set_status(f"Error: {err}", "error"),
                ))

        threading.Thread(target=change_thread, daemon=True).start()

    def _mac_restore(self):
        """Restore the original MAC address."""
        iface = self.mac_iface_var.get()
        if not iface:
            messagebox.showwarning("Input Required",
                                    "Please select a network interface.")
            return

        if iface not in self._mac_originals:
            messagebox.showinfo(
                "No Original MAC",
                "No original MAC address stored for this interface.\n"
                "The original MAC is recorded when you first change it."
            )
            return

        original_mac = self._mac_originals[iface]
        self.mac_output.append(
            f"Restoring MAC on {iface} to {original_mac}...", "info"
        )
        self.mac_status.set_status("Restoring MAC address...", "running")

        def restore_thread():
            try:
                from tools.mac_spoofer import change_mac
                success, msg = change_mac(iface, original_mac)
                tag = "success" if success else "error"
                self.root.after(0, lambda m=msg, t=tag: (
                    self.mac_output.append(
                        f"[{'+' if success else '!'}] {m}", t),
                    self.mac_status.set_status(
                        m, "ready" if success else "error"),
                    self._mac_on_interface_select() if success else None,
                ))
            except Exception as e:
                self.root.after(0, lambda err=str(e): (
                    self.mac_output.append(f"[!] Error: {err}", "error"),
                    self.mac_status.set_status(f"Error: {err}", "error"),
                ))

        threading.Thread(target=restore_thread, daemon=True).start()

    # ========================
    # AES TOOL
    # ========================

    def _create_aes_tool_view(self):
        """Create the AES encryption/decryption panel."""
        frame = tk.Frame(self.view_container, bg=COLORS["bg_dark"])

        # Header
        hdr = tk.Frame(frame, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(hdr, text="\u26bf  AES Encryption/Decryption",
                 font=FONTS["heading"], fg=COLORS["text_primary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(hdr, text="AES-256-GCM with Scrypt key derivation",
                 font=FONTS["subtitle"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(side="left", padx=(14, 0))

        # Mode selector
        mode_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        mode_frame.pack(fill="x", padx=24, pady=(0, 10))

        self.aes_mode_var = tk.StringVar(value="encrypt")
        ttk.Radiobutton(mode_frame, text="Encrypt",
                         variable=self.aes_mode_var,
                         value="encrypt",
                         command=self._aes_mode_changed).pack(side="left")
        ttk.Radiobutton(mode_frame, text="Decrypt",
                         variable=self.aes_mode_var,
                         value="decrypt",
                         command=self._aes_mode_changed).pack(
                             side="left", padx=(18, 0))

        # Input type selector
        type_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        type_frame.pack(fill="x", padx=24, pady=(0, 10))

        self.aes_type_var = tk.StringVar(value="text")
        ttk.Radiobutton(type_frame, text="Text",
                         variable=self.aes_type_var,
                         value="text",
                         command=self._aes_type_changed).pack(side="left")
        ttk.Radiobutton(type_frame, text="File",
                         variable=self.aes_type_var,
                         value="file",
                         command=self._aes_type_changed).pack(
                             side="left", padx=(18, 0))

        # Text input area
        self.aes_text_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        self.aes_text_frame.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(self.aes_text_frame, text="Input Text:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(anchor="w")
        self.aes_input_text = tk.Text(
            self.aes_text_frame, height=4, bg=COLORS["bg_input"],
            fg=COLORS["text_primary"], font=FONTS["mono"],
            insertbackground=COLORS["accent_cyan"],
            selectbackground=COLORS["accent_cyan"],
            borderwidth=0, highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent_cyan"],
            wrap="word", padx=10, pady=8,
        )
        self.aes_input_text.pack(fill="x")

        # File input (hidden by default)
        self.aes_file_frame = tk.Frame(frame, bg=COLORS["bg_dark"])

        tk.Label(self.aes_file_frame, text="Input File:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(anchor="w")
        file_row = tk.Frame(self.aes_file_frame, bg=COLORS["bg_dark"])
        file_row.pack(fill="x")

        self.aes_file_entry = ttk.Entry(file_row, width=50)
        self.aes_file_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(
            file_row, text="Browse...",
            style="Secondary.TButton", command=self._aes_browse
        ).pack(side="left", padx=(8, 0))

        # Password input
        pw_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        pw_frame.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(pw_frame, text="Password:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.aes_password_entry = ttk.Entry(pw_frame, width=30, show="*")
        self.aes_password_entry.pack(side="left", padx=(8, 0))

        # Action buttons
        btn_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        btn_frame.pack(fill="x", padx=24, pady=(0, 10))

        self.aes_action_btn = ttk.Button(
            btn_frame, text="\u25b6  Encrypt",
            style="Accent.TButton", command=self._aes_action
        )
        self.aes_action_btn.pack(side="left")

        # Load to Input button (for decrypt workflow)
        self.aes_load_btn = ttk.Button(
            btn_frame, text="\u21b3  Load Result to Input",
            style="Secondary.TButton", command=self._aes_load_to_input
        )
        self.aes_load_btn.pack(side="left", padx=(10, 0))

        ttk.Button(
            btn_frame, text="Save Output",
            style="Secondary.TButton", command=self._aes_save
        ).pack(side="left", padx=(10, 0))

        ttk.Button(
            btn_frame, text="Clear",
            style="Secondary.TButton", command=self._aes_clear
        ).pack(side="left", padx=(8, 0))

        # Output
        tk.Label(frame, text="Output:", font=FONTS["subheading"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(
                     anchor="w", padx=24, pady=(10, 0))
        self.aes_output = OutputPanel(frame, height=6)
        self.aes_output.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        # Status bar
        self.aes_status = StatusBar(frame)
        self.aes_status.pack(fill="x", padx=24, pady=(0, 10))

        # State
        self._aes_result = None
        self._aes_stop_event = threading.Event()
        self._stop_events[self.AES_TOOL] = self._aes_stop_event

        self.views[self.AES_TOOL] = frame

    def _aes_mode_changed(self):
        """Update button text and label when mode changes."""
        mode = self.aes_mode_var.get()
        if mode == "encrypt":
            self.aes_action_btn.configure(text="\u25b6  Encrypt")
        else:
            self.aes_action_btn.configure(text="\u25b6  Decrypt")

    def _aes_type_changed(self):
        """Toggle between text and file input."""
        aes_type = self.aes_type_var.get()
        if aes_type == "text":
            self.aes_text_frame.pack(fill="x", padx=24, pady=(0, 10))
            self.aes_file_frame.pack_forget()
        else:
            self.aes_file_frame.pack(fill="x", padx=24, pady=(0, 10))
            self.aes_text_frame.pack_forget()

    def _aes_browse(self):
        """Open file browser for input file."""
        mode = self.aes_mode_var.get()
        if mode == "encrypt":
            path = filedialog.askopenfilename(
                title="Select file to encrypt",
                filetypes=[("All files", "*.*")]
            )
        else:
            path = filedialog.askopenfilename(
                title="Select encrypted file to decrypt",
                filetypes=[("SecForge files", "*.sfenc"), ("All files", "*.*")]
            )
        if path:
            self.aes_file_entry.delete(0, "end")
            self.aes_file_entry.insert(0, path)

    def _aes_action(self):
        """Perform encrypt or decrypt operation."""
        password = self.aes_password_entry.get()
        if not password:
            messagebox.showwarning("Input Required", "Please enter a password.")
            return

        mode = self.aes_mode_var.get()
        aes_type = self.aes_type_var.get()

        self.aes_status.set_status("Processing...", "running")
        self.status_bar.set_status("AES operation in progress...", "running")

        def process():
            try:
                from tools.aes_tool import encrypt_text, decrypt_text
                from tools.aes_tool import (encrypt_file, decrypt_file,
                                             check_cryptography)

                ok, msg = check_cryptography()
                if not ok:
                    self.root.after(0, lambda: self._aes_error(msg))
                    return

                if aes_type == "text":
                    if mode == "encrypt":
                        input_text = self.aes_input_text.get(
                            "1.0", "end-1c").strip()
                        if not input_text:
                            self.root.after(
                                0, lambda: self._aes_error("Input text is empty"))
                            return
                        result = encrypt_text(input_text, password)
                        self._aes_result = ("text", result)
                        self.root.after(
                            0, lambda r=result: self._aes_encrypt_done(r))
                    else:
                        input_text = self.aes_input_text.get(
                            "1.0", "end-1c").strip()
                        if not input_text:
                            self.root.after(
                                0, lambda: self._aes_error("Input text is empty"))
                            return
                        result = decrypt_text(input_text, password)
                        self._aes_result = ("text", result)
                        self.root.after(
                            0, lambda r=result: self._aes_decrypt_done(r))
                else:
                    input_path = self.aes_file_entry.get().strip()
                    if not input_path:
                        self.root.after(
                            0, lambda: self._aes_error("Please select a file"))
                        return

                    if mode == "encrypt":
                        output_path = input_path + ".sfenc"
                        encrypt_file(input_path, output_path, password)
                        self._aes_result = ("file", output_path)
                        self.root.after(
                            0, lambda p=output_path:
                            self._aes_file_output(p, "encrypted"))
                    else:
                        if input_path.endswith(".sfenc"):
                            output_path = input_path[:-6]
                        else:
                            output_path = input_path + ".dec"
                        decrypt_file(input_path, output_path, password)
                        self._aes_result = ("file", output_path)
                        self.root.after(
                            0, lambda p=output_path:
                            self._aes_file_output(p, "decrypted"))

            except Exception as e:
                self.root.after(0, lambda err=str(e): self._aes_error(err))

        threading.Thread(target=process, daemon=True).start()

    def _aes_encrypt_done(self, ciphertext):
        """Handle encryption completion - show ciphertext in output panel."""
        self.aes_output.clear()
        self.aes_output.append(
            "[+] Encrypted successfully. Ciphertext:", "success")
        self.aes_output.append("", "cyan")
        self.aes_output.append(ciphertext, "cyan")
        self.aes_output.append("", "cyan")
        self.aes_output.append(
            "[i] Click 'Load Result to Input' then switch to Decrypt to test.",
            "muted")
        self.aes_status.set_status("Encryption complete", "ready")
        self.status_bar.set_status("AES encryption complete", "ready")

    def _aes_decrypt_done(self, plaintext):
        """Handle decryption completion - show plaintext in output panel."""
        self.aes_output.clear()
        self.aes_output.append("[+] Decrypted successfully. Plaintext:", "success")
        self.aes_output.append("", "cyan")
        self.aes_output.append(plaintext, "cyan")
        self.aes_output.append("", "cyan")
        self.aes_status.set_status("Decryption complete", "ready")
        self.status_bar.set_status("AES decryption complete", "ready")

    def _aes_load_to_input(self):
        """Load the last result into the input text box for decryption."""
        if not self._aes_result:
            messagebox.showinfo(
                "No Result",
                "No result available. Perform an encryption first."
            )
            return

        result_type, value = self._aes_result
        if result_type == "text":
            self.aes_input_text.delete("1.0", "end")
            self.aes_input_text.insert("1.0", value)
            self.aes_output.append(
                "[+] Loaded ciphertext into input. Switch to Decrypt and click Decrypt.",
                "success"
            )
        else:
            self.aes_output.append(
                f"[i] File result: {value}. Use Browse to select it for decryption.",
                "info"
            )

    def _aes_file_output(self, path, operation):
        """Display file operation result."""
        self.aes_output.clear()
        self.aes_output.append(
            f"[+] File {operation}ed successfully: {path}", "success")
        self.aes_status.set_status(
            f"File {operation}ed: {path}", "ready")
        self.status_bar.set_status("AES operation complete", "ready")

    def _aes_error(self, message):
        """Handle AES operation error."""
        self.aes_output.append(f"[!] {message}", "error")
        self.aes_status.set_status(f"Error: {message}", "error")
        self.status_bar.set_status("AES operation failed", "error")

    def _aes_save(self):
        """Save the current result to a file."""
        if not self._aes_result:
            messagebox.showinfo(
                "No Result", "No result to save. Perform an operation first.")
            return

        result_type, value = self._aes_result
        if result_type == "text":
            path = filedialog.asksaveasfilename(
                title="Save result",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if path:
                with open(path, "w") as f:
                    f.write(value)
                self.aes_output.append(f"[+] Saved to {path}", "success")
        else:
            self.aes_output.append(f"[+] Output file: {value}", "info")

    def _aes_clear(self):
        """Clear AES tool inputs and outputs."""
        self.aes_input_text.delete("1.0", "end")
        self.aes_file_entry.delete(0, "end")
        self.aes_password_entry.delete(0, "end")
        self.aes_output.clear()
        self.aes_status.set_status("Ready", "ready")
        self._aes_result = None

    # ========================
    # PASSWORD CRACKER
    # ========================

    def _create_password_cracker_view(self):
        """Create the password hash cracker panel."""
        frame = tk.Frame(self.view_container, bg=COLORS["bg_dark"])

        # Header
        hdr = tk.Frame(frame, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=24, pady=(18, 10))
        tk.Label(hdr, text="\u2693  Password Hash Cracker",
                 font=FONTS["heading"], fg=COLORS["text_primary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(hdr, text="Offline hash testing against wordlists",
                 font=FONTS["subtitle"], fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(side="left", padx=(14, 0))

        # Hash input
        hash_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        hash_frame.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(hash_frame, text="Target Hash:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.pc_hash_entry = ttk.Entry(hash_frame, width=50)
        self.pc_hash_entry.pack(side="left", padx=(8, 0))

        # Algorithm selector
        algo_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        algo_frame.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(algo_frame, text="Algorithm:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.pc_algo_var = tk.StringVar(value="MD5")
        ttk.Combobox(
            algo_frame, textvariable=self.pc_algo_var,
            values=["MD5", "SHA-1", "SHA-256", "SHA-512"],
            state="readonly", width=15
        ).pack(side="left", padx=(8, 0))

        # Wordlist selection
        wl_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        wl_frame.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(wl_frame, text="Wordlist File:",
                 font=FONTS["body"], fg=COLORS["text_secondary"],
                 bg=COLORS["bg_dark"]).pack(side="left")
        self.pc_wordlist_entry = ttk.Entry(wl_frame, width=45)
        self.pc_wordlist_entry.pack(side="left", padx=(8, 0))

        ttk.Button(
            wl_frame, text="Browse...",
            style="Secondary.TButton", command=self._pc_browse
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            wl_frame, text="Create Sample",
            style="Secondary.TButton", command=self._pc_create_sample
        ).pack(side="left", padx=(8, 0))

        # Control buttons
        btn_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        btn_frame.pack(fill="x", padx=24, pady=(0, 10))

        self.pc_start_btn = ttk.Button(
            btn_frame, text="\u25b6  Start Cracking",
            style="Accent.TButton", command=self._pc_start
        )
        self.pc_start_btn.pack(side="left")

        self.pc_stop_btn = ttk.Button(
            btn_frame, text="\u25a0  Stop",
            style="Stop.TButton", command=self._pc_stop
        )
        self.pc_stop_btn.pack(side="left", padx=(8, 0))

        ttk.Button(
            btn_frame, text="Clear",
            style="Secondary.TButton", command=self._pc_clear
        ).pack(side="left", padx=(8, 0))

        # Progress/stats area
        stats_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        stats_frame.pack(fill="x", padx=24, pady=(6, 6))

        self.pc_words_label = tk.Label(stats_frame, text="Words tested: 0",
                                        font=FONTS["status"],
                                        fg=COLORS["text_secondary"],
                                        bg=COLORS["bg_dark"])
        self.pc_words_label.pack(side="left")

        self.pc_time_label = tk.Label(stats_frame, text="Elapsed: 0.0s",
                                       font=FONTS["status"],
                                       fg=COLORS["text_secondary"],
                                       bg=COLORS["bg_dark"])
        self.pc_time_label.pack(side="left", padx=(24, 0))

        self.pc_speed_label = tk.Label(stats_frame, text="Speed: 0 words/s",
                                        font=FONTS["status"],
                                        fg=COLORS["text_secondary"],
                                        bg=COLORS["bg_dark"])
        self.pc_speed_label.pack(side="left", padx=(24, 0))

        # Result display
        tk.Label(frame, text="Result:", font=FONTS["subheading"],
                 fg=COLORS["text_secondary"], bg=COLORS["bg_dark"]).pack(
                     anchor="w", padx=24, pady=(10, 0))
        self.pc_result = OutputPanel(frame, height=8)
        self.pc_result.pack(fill="both", expand=True, padx=24, pady=(4, 10))

        # Status bar
        self.pc_status = StatusBar(frame)
        self.pc_status.pack(fill="x", padx=24, pady=(0, 10))

        # State
        self._pc_stop_event = threading.Event()
        self._stop_events[self.PASSWORD_CRACKER] = self._pc_stop_event

        self.views[self.PASSWORD_CRACKER] = frame

    def _pc_browse(self):
        """Open file browser for wordlist."""
        path = filedialog.askopenfilename(
            title="Select wordlist file",
            filetypes=[
                ("Text files", "*.txt"),
                ("Wordlist files", "*.lst *.list"),
                ("All files", "*.*"),
            ]
        )
        if path:
            self.pc_wordlist_entry.delete(0, "end")
            self.pc_wordlist_entry.insert(0, path)

    def _pc_create_sample(self):
        """Create a sample wordlist for testing."""
        path = filedialog.asksaveasfilename(
            title="Save sample wordlist",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="sample_wordlist.txt"
        )
        if path:
            try:
                from tools.password_cracker import create_sample_wordlist
                count = create_sample_wordlist(path)
                self.pc_wordlist_entry.delete(0, "end")
                self.pc_wordlist_entry.insert(0, path)
                self.pc_result.append(
                    f"[+] Created sample wordlist with {count} words: {path}",
                    "success"
                )
            except Exception as e:
                self.pc_result.append(f"[!] Error: {e}", "error")

    def _pc_start(self):
        """Start the hash cracking process."""
        target_hash = self.pc_hash_entry.get().strip()
        algorithm = self.pc_algo_var.get()
        wordlist = self.pc_wordlist_entry.get().strip()

        if not target_hash:
            messagebox.showwarning("Input Required",
                                    "Please enter a target hash.")
            return
        if not wordlist:
            messagebox.showwarning("Input Required",
                                    "Please select a wordlist file.")
            return

        # Validate hash format
        from tools.password_cracker import validate_hash
        valid, err = validate_hash(target_hash, algorithm)
        if not valid:
            messagebox.showerror("Invalid Hash", err)
            return

        self._pc_stop_event.clear()
        self.pc_result.clear()
        self.pc_start_btn.configure(state="disabled")
        self.pc_status.set_status(f"Cracking {algorithm} hash...", "running")
        self.status_bar.set_status("Hash cracking in progress...", "running")

        def crack_thread():
            try:
                from tools.password_cracker import crack_hash

                def on_progress(tested, elapsed, current_word):
                    speed = tested / elapsed if elapsed > 0 else 0
                    self.root.after(
                        0, lambda t=tested, e=elapsed, s=speed: (
                            self.pc_words_label.configure(
                                text=f"Words tested: {t}"),
                            self.pc_time_label.configure(
                                text=f"Elapsed: {e:.1f}s"),
                            self.pc_speed_label.configure(
                                text=f"Speed: {s:.0f} words/s"),
                        ))

                result = crack_hash(
                    target_hash, algorithm, wordlist,
                    callback=on_progress,
                    stop_event=self._pc_stop_event,
                )

                self.root.after(0, lambda r=result: self._pc_complete(r))

            except Exception as e:
                self.root.after(0, lambda err=str(e): self._pc_error(err))

        threading.Thread(target=crack_thread, daemon=True).start()

    def _pc_complete(self, result):
        """Handle cracking completion."""
        self.pc_start_btn.configure(state="normal")

        self.pc_words_label.configure(
            text=f"Words tested: {result['words_tested']}"
        )
        self.pc_time_label.configure(
            text=f"Elapsed: {result['elapsed_time']:.1f}s"
        )

        speed = (result['words_tested'] / result['elapsed_time']
                 if result['elapsed_time'] > 0 else 0)
        self.pc_speed_label.configure(text=f"Speed: {speed:.0f} words/s")

        if result["found"]:
            self.pc_result.append("=" * 50, "cyan")
            self.pc_result.append("", "cyan")
            self.pc_result.append("  [+] PASSWORD FOUND!", "success")
            self.pc_result.append("", "cyan")
            self.pc_result.append(
                f"  Hash:    {self.pc_hash_entry.get().strip()}", "info")
            self.pc_result.append(
                f"  Algo:    {self.pc_algo_var.get()}", "info")
            self.pc_result.append(
                f"  Word:    {result['password']}", "success")
            self.pc_result.append(
                f"  Tested:  {result['words_tested']} words", "info")
            self.pc_result.append(
                f"  Time:    {result['elapsed_time']:.2f}s", "info")
            self.pc_result.append("", "cyan")
            self.pc_result.append("=" * 50, "cyan")
            self.pc_status.set_status(
                f"Found: {result['password']}", "ready"
            )
        else:
            self.pc_result.append("=" * 50, "muted")
            self.pc_result.append("", "muted")
            self.pc_result.append(
                f"  [-] {result['status']}", "warning")
            self.pc_result.append(
                f"  Tested {result['words_tested']} words in "
                f"{result['elapsed_time']:.2f}s", "muted")
            self.pc_result.append("", "muted")
            self.pc_result.append("=" * 50, "muted")
            self.pc_status.set_status(result['status'], "warning")

        self.status_bar.set_status("Cracking complete", "ready")

    def _pc_error(self, message):
        """Handle cracking error."""
        self.pc_start_btn.configure(state="normal")
        self.pc_result.append(f"[!] Error: {message}", "error")
        self.pc_status.set_status(f"Error: {message}", "error")
        self.status_bar.set_status("Cracking error", "error")

    def _pc_stop(self):
        """Stop the cracking process."""
        self._pc_stop_event.set()
        self.pc_start_btn.configure(state="normal")
        self.pc_status.set_status("Stopped by user", "warning")
        self.status_bar.set_status("Cracking stopped", "warning")

    def _pc_clear(self):
        """Clear cracker inputs and results."""
        self.pc_hash_entry.delete(0, "end")
        self.pc_result.clear()
        self.pc_words_label.configure(text="Words tested: 0")
        self.pc_time_label.configure(text="Elapsed: 0.0s")
        self.pc_speed_label.configure(text="Speed: 0 words/s")
        self.pc_status.set_status("Ready", "ready")

    # ========================
    # COMMON
    # ========================

    def _on_close(self):
        """Handle window close event."""
        # Stop all running operations
        for stop_event in self._stop_events.values():
            if stop_event is not None:
                stop_event.set()
        self.root.destroy()
