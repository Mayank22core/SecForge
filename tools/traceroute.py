"""
Traceroute Tool
Network path tracing using the system traceroute/tracert command.
Shows each hop (router) between the local machine and a destination.
"""

import platform
import subprocess
import re
import socket


def resolve_destination(dest):
    """Resolve a hostname to an IP address for validation."""
    dest = dest.strip()
    # Check if it's already an IP address
    try:
        socket.inet_aton(dest)
        return dest, None
    except socket.error:
        pass

    # Try DNS resolution
    try:
        ip = socket.gethostbyname(dest)
        return ip, None
    except socket.gaierror:
        return None, f"Could not resolve hostname: {dest}"


def get_traceroute_command(dest, max_hops=30):
    """Build the traceroute/tracert command based on the OS."""
    system = platform.system().lower()

    if system == "windows":
        # tracert is the Windows traceroute utility
        # /d prevents DNS resolution for faster output
        # /w 1000 sets a 1-second timeout per hop
        return ["tracert", "-d", "-w", "1000", "-h", str(max_hops), dest]
    else:
        # On Linux/macOS, use traceroute
        # -n: don't resolve hostnames (faster)
        # -m: max hops
        # -w: wait time in seconds
        return ["traceroute", "-n", "-m", str(max_hops), "-w", "2", dest]


def parse_traceroute_line(line, system):
    """Parse a single line of traceroute output into structured data.

    Returns:
        tuple: (hop_number, ip_address, hostname, response_time_ms) or None
    """
    line = line.strip()
    if not line:
        return None

    if system == "windows":
        # Windows tracert output format:
        # "  1     1 ms     1 ms     1 ms  192.168.1.1"
        # or  "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
        # or  "  3     *        *        *     Request timed out."
        match = re.match(
            r'^\s*(\d+)\s+'
            r'(?:[\d<>\s*]+ms\s+){1,3}'  # at least one valid time
            r'(\S+)',
            line
        )
        if match:
            hop = int(match.group(1))
            ip = match.group(2)
            # Extract the first time value
            time_match = re.search(r'(\d+|<\d+)\s*ms', line)
            time_ms = time_match.group(1).replace('<', '') if time_match else "*"
            return (hop, ip, "", time_ms)

        # Check for timeout line
        timeout_match = re.match(r'^\s*(\d+)\s+', line)
        if timeout_match and ('*' in line or 'Request timed out' in line):
            return (int(timeout_match.group(1)), "*", "", "*")

    else:
        # Linux/macOS traceroute output format:
        # " 1  192.168.1.1  1.234 ms  1.567 ms  1.890 ms"
        # or " 1  * * *"
        parts = line.split()
        if len(parts) >= 2:
            try:
                hop = int(parts[0])
            except ValueError:
                return None

            ip = parts[1]
            if ip == "*":
                return (hop, "*", "", "*")

            # Find the first time value (format: X.XXX ms)
            for i, part in enumerate(parts):
                if part == "ms" and i > 0:
                    try:
                        time_val = float(parts[i - 1])
                        return (hop, ip, "", f"{time_val:.1f}")
                    except ValueError:
                        pass

            return (hop, ip, "", "*")

    return None


def run_traceroute(dest, callback=None, stop_event=None, max_hops=30):
    """
    Execute a traceroute to the given destination.

    Uses the operating system's built-in traceroute/tracert utility
    and parses the output line by line.

    Args:
        dest: Destination hostname or IP address
        callback: Function called with (hop, ip, hostname, time_ms) for each hop
        stop_event: threading.Event to signal cancellation
        max_hops: Maximum number of hops to trace

    Returns:
        List of tuples: [(hop, ip, hostname, time_ms), ...]
    """
    dest = dest.strip()
    if not dest:
        raise ValueError("Destination cannot be empty")

    # Validate the destination
    resolved_ip, err = resolve_destination(dest)
    if err:
        raise ValueError(err)

    system = platform.system().lower()
    cmd = get_traceroute_command(dest, max_hops)

    results = []

    try:
        # Start the traceroute process
        # Using CREATE_NO_WINDOW on Windows to avoid console popup
        startupinfo = None
        if system == "windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if system == "windows" else 0,
        )

        for line in iter(process.stdout.readline, ""):
            if stop_event and stop_event.is_set():
                process.terminate()
                break

            parsed = parse_traceroute_line(line, system)
            if parsed:
                hop, ip, hostname, time_ms = parsed
                results.append(parsed)
                if callback:
                    callback(hop, ip, hostname, time_ms)

        process.wait()

        if process.returncode != 0 and not results:
            stderr_output = process.stderr.read()
            if "Permission denied" in stderr_output or "requires root" in stderr_output.lower():
                raise RuntimeError(
                    "Permission denied. Traceroute requires administrator/root privileges.\n"
                    "On Windows: Run as Administrator\n"
                    "On Linux: Run with sudo"
                )
            elif stderr_output.strip():
                raise RuntimeError(f"Traceroute error: {stderr_output.strip()}")

    except FileNotFoundError:
        raise RuntimeError(
            f"Traceroute command not found. Ensure {'tracert' if system == 'windows' else 'traceroute'} "
            f"is available on your system."
        )
    except subprocess.SubprocessError as e:
        if "Permission denied" in str(e):
            raise RuntimeError(
                "Permission denied. Traceroute requires administrator/root privileges."
            )
        raise RuntimeError(f"Process error: {e}")

    return results


def validate_destination(dest):
    """Quick validation of a destination string."""
    dest = dest.strip()
    if not dest:
        return False, "Destination cannot be empty"
    if len(dest) > 255:
        return False, "Destination is too long"
    return True, None
