"""
Network Scanner Tool
Network device discovery using ARP requests.
Supports Scapy (layer 2) and a ping+arp fallback for systems without winpcap.
"""

import ipaddress
import subprocess
import platform
import threading
import time
import re


def check_scapy():
    """Check if Scapy is installed."""
    try:
        import scapy  # noqa: F401
        return True, ""
    except ImportError:
        return False, "Scapy is not installed. Run: pip install scapy"


def _check_layer2_available():
    """Check if Scapy layer 2 sending is actually available on this system."""
    try:
        from scapy.all import conf, Ether, ARP
        conf.verb = 0
        # Try to create a layer 2 socket - this fails without winpcap/Npcap
        sock = conf.L2socket(iface=conf.iface)
        sock.close()
        return True
    except Exception:
        return False


def validate_network(network_str):
    """Validate and normalize a CIDR network string."""
    network_str = network_str.strip()
    if "/" not in network_str:
        network_str = network_str + "/24"
    try:
        network = ipaddress.ip_network(network_str, strict=False)
        if network.num_addresses > 1024:
            return None, "Network range too large (max /22). Use a smaller range."
        return network, None
    except ValueError as e:
        return None, f"Invalid network: {e}"


def scan_network(network_str, callback=None, stop_event=None):
    """
    Scan a network range for active devices.

    Tries Scapy ARP scan first. Falls back to ping + arp -a on systems
    where Scapy layer 2 is unavailable (e.g., Windows without winpcap).

    Args:
        network_str: CIDR notation string (e.g., "192.168.1.0/24")
        callback: Function called with (ip, mac, status) for each found device
        stop_event: threading.Event to signal scan cancellation

    Returns:
        Tuple of (results_list, elapsed_time)
    """
    network, err = validate_network(network_str)
    if err:
        raise ValueError(err)

    # Try Scapy first
    try:
        from scapy.all import ARP, Ether, srp, conf
        conf.verb = 0

        # Test if layer 2 actually works before attempting full scan
        if _check_layer2_available():
            return _scan_scapy(network, callback, stop_event)
        else:
            # Fall through to ping+arp method
            pass
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: ping sweep + arp table
    return _scan_ping_arp(network, callback, stop_event)


def _scan_scapy(network, callback, stop_event):
    """Scan using Scapy ARP requests (requires winpcap/Npcap)."""
    from scapy.all import ARP, Ether, srp, conf
    conf.verb = 0

    arp = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    results = []
    start_time = time.time()

    try:
        answered, _ = srp(packet, timeout=3, verbose=False)

        for sent, received in answered:
            if stop_event and stop_event.is_set():
                break
            ip = received.psrc
            mac = received.hwsrc
            device = (ip, mac, "Active")
            results.append(device)
            if callback:
                callback(ip, mac, "Active")

    except PermissionError:
        raise RuntimeError(
            "Permission denied. ARP scanning requires administrator privileges.\n"
            "Run SecForge as Administrator."
        )
    except Exception as e:
        raise RuntimeError(f"Scapy scan error: {e}")

    elapsed = time.time() - start_time
    return results, elapsed


def _scan_ping_arp(network, callback, stop_event):
    """
    Scan using ping sweep + arp table lookup.

    This is a fallback for Windows systems without winpcap/Npcap.
    Pings every IP in the range, then reads the ARP table to find MAC addresses.

    How it works:
    1. Read existing ARP table first (fast, no network traffic)
    2. Ping each IP in parallel batches to populate ARP cache
    3. Read ARP table again to find newly discovered hosts
    """
    system = platform.system().lower()
    results = []
    seen_ips = set()
    start_time = time.time()

    # Step 1: Read existing ARP table first (instant, no pinging needed)
    existing_arp = _read_arp_table()
    network_hosts = set(str(ip) for ip in network.hosts())

    for ip_str, mac in existing_arp.items():
        if stop_event and stop_event.is_set():
            break
        if ip_str in network_hosts and mac != "ff:ff:ff:ff:ff:ff":
            results.append((ip_str, mac, "Active"))
            seen_ips.add(ip_str)
            if callback:
                callback(ip_str, mac, "Active")

    if seen_ips:
        elapsed = time.time() - start_time
        return results, elapsed

    # Step 2: No existing entries - do a fast ping sweep
    # Use concurrent pinging for speed
    all_hosts = list(network.hosts())
    if not all_hosts:
        all_hosts = [network.network_address]

    def ping_host(ip_str):
        """Ping a single host with a short timeout."""
        try:
            if system == "windows":
                cmd = ["ping", "-n", "1", "-w", "300", ip_str]
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            else:
                cmd = ["ping", "-c", "1", "-W", "1", ip_str]
                startupinfo = None

            subprocess.run(
                cmd, capture_output=True, timeout=1.5,
                startupinfo=startupinfo,
                creationflags=(subprocess.CREATE_NO_WINDOW
                               if system == "windows" else 0),
            )
        except Exception:
            pass

    # Ping in batches of 20 for speed
    batch_size = 20
    for i in range(0, len(all_hosts), batch_size):
        if stop_event and stop_event.is_set():
            break
        batch = all_hosts[i:i + batch_size]
        threads = []
        for ip in batch:
            t = threading.Thread(target=ping_host, args=(str(ip),), daemon=True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join(timeout=3)

    # Step 3: Read ARP table again
    arp_table = _read_arp_table()
    for ip_str, mac in arp_table.items():
        if ip_str in network_hosts and mac != "ff:ff:ff:ff:ff:ff":
            results.append((ip_str, mac, "Active"))
            if callback:
                callback(ip_str, mac, "Active")

    elapsed = time.time() - start_time
    return results, elapsed


def _read_arp_table():
    """
    Read the system ARP table and return a dict of IP -> MAC.

    Parses output of 'arp -a' command.
    """
    system = platform.system().lower()

    try:
        startupinfo = None
        if system == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

        result = subprocess.run(
            ["arp", "-a"],
            capture_output=True, text=True, timeout=5,
            startupinfo=startupinfo,
            creationflags=(subprocess.CREATE_NO_WINDOW
                           if system == "windows" else 0),
        )

        arp_table = {}

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                # Windows arp -a format:
                # "  192.168.1.1      aa-bb-cc-dd-ee-ff     dynamic"
                # Linux arp -a format:
                # " ? (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0"

                # Try Windows format first
                win_match = re.match(
                    r'\s+(\d+\.\d+\.\d+\.\d+)\s+'
                    r'([0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:]'
                    r'[0-9a-fA-F]{2}[-:][0-9a-fA-F]{2}[-:]'
                    r'[0-9a-fA-F]{2}[-:][0-9a-fA-F]{2})',
                    line
                )
                if win_match:
                    ip = win_match.group(1)
                    mac = win_match.group(2).replace("-", ":").lower()
                    arp_table[ip] = mac
                    continue

                # Try Linux format
                lin_match = re.search(
                    r'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+'
                    r'([0-9a-fA-F:]{17})',
                    line
                )
                if lin_match:
                    ip = lin_match.group(1)
                    mac = lin_match.group(2).lower()
                    arp_table[ip] = mac

        return arp_table

    except Exception:
        return {}


def get_local_network():
    """Attempt to detect the local network range automatically."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        finally:
            s.close()

        parts = local_ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        return "192.168.1.0/24"
