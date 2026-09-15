"""
MAC Address Spoofer Tool
Utility for changing MAC addresses on local network interfaces.
Supports Windows. On Linux/WSL, reports limitations with physical adapters.
"""

import platform
import subprocess
import re
import secrets


def is_admin():
    """Check if the current process has administrator/root privileges."""
    system = platform.system().lower()
    try:
        if system == "windows":
            # Attempt to access a protected system resource
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # On Unix-like systems, check effective UID
            return __import__("os").geteuid() == 0
    except Exception:
        return False


def generate_random_mac():
    """Generate a random valid MAC address.

    The second hex digit of the first byte is set to 2, 6, A, or E
    to ensure it is a locally administered unicast address
    (not a globally unique/broadcast address).
    """
    # Locally administered, unicast mask: xx:2x/6x/Ax/Ex
    first_byte = secrets.choice(["02", "06", "0A", "0E"])
    remaining = ":".join(f"{secrets.randbelow(256):02x}" for _ in range(5))
    return f"{first_byte}:{remaining}"


def validate_mac(mac_str):
    """Validate a MAC address format (XX:XX:XX:XX:XX:XX)."""
    pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
    if re.match(pattern, mac_str.strip()):
        return True, None
    return False, "Invalid MAC address format. Expected: XX:XX:XX:XX:XX:XX"


def get_interfaces_windows():
    """Get network interfaces on Windows using getmac and ipconfig."""
    interfaces = []

    try:
        # getmac /v gives verbose output with connection names
        result = subprocess.run(
            ["getmac", "/v", "/fo", "csv"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                for line in lines[1:]:
                    # Parse CSV output
                    parts = line.strip().strip('"').split('","')
                    if len(parts) >= 3:
                        name = parts[0].strip('"')
                        mac = parts[2].strip('"').replace("-", ":")
                        if mac and mac != "N/A" and mac != "":
                            interfaces.append({
                                "name": name,
                                "mac": mac,
                                "adapter": name,
                            })
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Also try netsh to find interface names
    try:
        result = subprocess.run(
            ["netsh", "interface", "show", "interface"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                line = line.strip()
                # Lines look like: "Enabled    Connected    Ethernet" or similar
                parts = line.split()
                if len(parts) >= 3 and parts[0] in ("Enabled", "Disabled"):
                    iface_name = " ".join(parts[2:])
                    # Check if this interface already exists
                    existing_names = [i["name"] for i in interfaces]
                    if iface_name not in existing_names:
                        interfaces.append({
                            "name": iface_name,
                            "mac": "Unknown",
                            "adapter": iface_name,
                        })
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return interfaces


def get_interfaces_linux():
    """Get network interfaces on Linux using ip link."""
    interfaces = []

    try:
        result = subprocess.run(
            ["ip", "-o", "link", "show"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                # Format: "2: eth0: <BROADCAST,...> ..."
                match = re.match(r'^\d+:\s+(\S+?):\s', line)
                if match:
                    name = match.group(1)
                    if name == "lo":
                        continue  # Skip loopback
                    # Try to get the MAC
                    mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]{17})', line)
                    mac = mac_match.group(1) if mac_match else "Unknown"
                    interfaces.append({
                        "name": name,
                        "mac": mac,
                        "adapter": name,
                    })
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return interfaces


def get_interfaces():
    """Get network interfaces for the current platform."""
    system = platform.system().lower()
    if system == "windows":
        return get_interfaces_windows()
    else:
        return get_interfaces_linux()


def get_current_mac(interface_name):
    """Get the current MAC address for a specific interface."""
    system = platform.system().lower()

    if system == "windows":
        try:
            # Use getmac filtered by interface name
            result = subprocess.run(
                ["getmac", "/v", "/fo", "csv"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n")[1:]:
                    parts = line.strip().strip('"').split('","')
                    if len(parts) >= 3:
                        name = parts[0].strip('"')
                        mac = parts[2].strip('"').replace("-", ":")
                        if name == interface_name and mac and mac != "N/A":
                            return mac
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    else:
        try:
            result = subprocess.run(
                ["ip", "-o", "link", "show", interface_name],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                match = re.search(r'link/ether\s+([0-9a-fA-F:]{17})', result.stdout)
                if match:
                    return match.group(1)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    return None


def change_mac_windows(interface_name, new_mac):
    """Change MAC address on Windows using netsh.

    Windows uses the registry to store the MAC address override.
    The network adapter is disabled and re-enabled to apply the change.
    """
    # Remove colons for the registry format
    mac_no_colons = new_mac.replace(":", "").replace("-", "").upper()

    # Use netsh to set the MAC (disabled MAC address for the adapter)
    # Windows netsh doesn't directly support MAC changes on all adapters
    # We use the registry approach via PowerShell
    try:
        # Find the registry path for the network adapter
        ps_script = f'''
        $adapter = Get-NetAdapter -Name "{interface_name}" -ErrorAction Stop
        $adapterId = $adapter.InterfaceGuid
        $regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4D36E972-E325-11CE-BFC1-08002BE10318}}"

        # Find the matching adapter subkey
        $subKeys = Get-ChildItem -Path $regPath -ErrorAction Stop
        foreach ($subKey in $subKeys) {{
            $id = Get-ItemProperty -Path $subKey.PSPath -Name "NetCfgInstanceId" -ErrorAction SilentlyContinue
            if ($id -and $id.NetCfgInstanceId -eq $adapterId) {{
                Set-ItemProperty -Path $subKey.PSPath -Name "NetworkAddress" -Value "{mac_no_colons}" -ErrorAction Stop

                # Disable and re-enable the adapter to apply
                Disable-NetAdapter -Name "{interface_name}" -Confirm:$false -ErrorAction Stop
                Start-Sleep -Seconds 2
                Enable-NetAdapter -Name "{interface_name}" -Confirm:$false -ErrorAction Stop
                exit 0
            }}
        }}
        Write-Error "Could not find adapter registry key"
        exit 1
        '''

        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True, text=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            return True, f"MAC address changed to {new_mac}"
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return False, f"Failed to change MAC: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, "Operation timed out"
    except Exception as e:
        return False, f"Error: {e}"


def change_mac_linux(interface_name, new_mac):
    """Change MAC address on Linux using ip link.

    On Linux, we can directly set the MAC address using ip link commands.
    The interface must be down before changing the MAC.
    """
    try:
        # Bring the interface down
        subprocess.run(
            ["sudo", "ip", "link", "set", interface_name, "down"],
            capture_output=True, text=True, timeout=10,
        )

        # Set the new MAC address
        result = subprocess.run(
            ["sudo", "ip", "link", "set", interface_name, "address", new_mac],
            capture_output=True, text=True, timeout=10,
        )

        if result.returncode != 0:
            # Bring it back up before returning error
            subprocess.run(
                ["sudo", "ip", "link", "set", interface_name, "up"],
                capture_output=True, text=True, timeout=10,
            )
            return False, f"Failed to set MAC: {result.stderr.strip()}"

        # Bring the interface back up
        subprocess.run(
            ["sudo", "ip", "link", "set", interface_name, "up"],
            capture_output=True, text=True, timeout=10,
        )

        return True, f"MAC address changed to {new_mac}"

    except subprocess.TimeoutExpired:
        return False, "Operation timed out"
    except Exception as e:
        return False, f"Error: {e}"


def change_mac(interface_name, new_mac):
    """Change MAC address for the given interface.

    Returns:
        (success: bool, message: str)
    """
    valid, err = validate_mac(new_mac)
    if not valid:
        return False, err

    system = platform.system().lower()

    if system == "windows":
        if not is_admin():
            return False, (
                "Administrator privileges required to change MAC address.\n"
                "Please run SecForge as Administrator."
            )
        return change_mac_windows(interface_name, new_mac)
    else:
        if not is_admin():
            return False, (
                "Root privileges required to change MAC address.\n"
                "Please run with sudo."
            )
        return change_mac_linux(interface_name, new_mac)
