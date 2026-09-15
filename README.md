# SecForge - Cybersecurity Toolkit

A desktop application built around the practical Python, Linux, and networking concepts taught in a cybersecurity course. SecForge provides five functional security tools in a single polished GUI.

## Why SecForge?

SecForge was built as a practical project to apply concepts from a cybersecurity course, including Python scripting, Linux administration, networking fundamentals (TCP/IP, ARP), cryptography, and hashing. The project was created alongside the course material, with the course content used to understand, test, and improve the implementations.

## Tools Included

| Tool | Description |
|------|-------------|
| **Network Scanner** | ARP-based local network device discovery |
| **Traceroute** | Network path tracing to a destination host |
| **MAC Address Spoofer** | Change MAC addresses on local network interfaces |
| **AES Encryption/Decryption** | Encrypt and decrypt text/files using AES-256-GCM |
| **Password Hash Cracker** | Offline hash testing against wordlists |

## Technology

- **Language:** Python 3
- **GUI:** Tkinter / ttk with a dark cybersecurity-themed interface
- **Networking:** Scapy (ARP packets), subprocess (system traceroute)
- **Cryptography:** `cryptography` package (AES-GCM, Scrypt KDF)
- **Hashing:** Python `hashlib` (MD5, SHA-1, SHA-256, SHA-512)

## Project Structure

```
SecForge/
  main.py                 # Application entry point
  requirements.txt        # Python dependencies
  README.md
  gui/
    __init__.py
    app.py                # Main application window and all tool panels
    theme.py              # Dark theme colors and font configuration
    widgets.py            # Reusable UI components
  tools/
    __init__.py
    network_scanner.py    # ARP-based network scanner
    traceroute.py         # System traceroute wrapper
    mac_spoofer.py        # MAC address changer
    aes_tool.py           # AES-256-GCM encryption/decryption
    password_cracker.py   # Offline hash cracker
```

## Installation

1. Ensure Python 3.8+ is installed.

2. (Optional) Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Linux/macOS
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running

```
python main.py
```

## Tool Usage

### Network Scanner
1. Enter a network range in CIDR format (e.g., `192.168.1.0/24`).
2. Click **Scan**.
3. Active devices will appear in the results table.
4. Requires administrator privileges for ARP scanning.

### Traceroute
1. Enter a destination hostname or IP address.
2. Click **Start**.
3. View the network hops in the results table.
4. Requires administrator privileges on most systems.

### MAC Address Spoofer
1. Click **Refresh** to list network interfaces.
2. Select an interface from the dropdown.
3. Click **Random MAC** or enter a custom MAC address.
4. Click **Change MAC** (requires administrator privileges).
5. Use **Restore Original** to revert to the original MAC.

### AES Encryption/Decryption
1. Select **Encrypt** or **Decrypt** mode.
2. Choose **Text** or **File** input type.
3. Enter text or browse for a file.
4. Enter a password.
5. Click **Encrypt** or **Decrypt**.
6. Use **Save Output** to write results to a file.

### Password Hash Cracker
1. Enter the target hash.
2. Select the hash algorithm (MD5, SHA-1, SHA-256, SHA-512).
3. Select a wordlist file (one word per line).
4. Click **Start Cracking**.
5. View progress and results in the output panel.

## Disclaimer

Use SecForge only on systems, devices, and networks you own or have explicit permission to test. Unauthorized access to computer systems is illegal. This tool is built for educational and authorized testing purposes only.
