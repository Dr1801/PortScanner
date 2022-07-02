import argparse
import socket
import time
import sys
from threading import Thread, Lock
from queue import Queue

threads = 1400                                                          # Number of simultaneous threads to use, feel free to tweak
queue = Queue()                                                         
open_ports =  []                                                        # Storing all the open ports
print_lock = Lock()                                                     # Print lock (only one thread at a time can print)
socket.setdefaulttimeout(0.5)                                           

def scan_ports(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # Create socket
        s.connect((host, port))                                         # Attempt connection on specified host and port
        with print_lock:                                                # Use lock to prevent multiple threads writing at the same time
            print('Port:',port, 'is open')
            open_ports.append(port)                                     # Save open ports to print later 
        s.close()
    except (socket.timeout, ConnectionRefusedError):                    # If ConnectionRefused exception, pass
        pass

def scan_thread():
    global queue
    while True:
        worker = queue.get()                                            # Retrieve port from queue
        scan_ports(worker)                                              # Scan port using scan_ports() function
        queue.task_done()

def main(host, ports):
    global queue
    startTime = time.time()                                             # Timestamp (time taken to scan)
    for t in range(threads):
        t = Thread(target=scan_thread)
        t.daemon = True
        t.start()                                                       # Start each thread

    for worker in ports:                                                # Put each port into the queue
        queue.put(worker)

    queue.join()                                                        # Wait until all threads are finished
    runtime = float("%0.2f" % (time.time() - startTime))                # Cal time taken
    print("Run time: ", runtime, "seconds")                             
    open_ports.sort()                                                   # Sort ports number from low to high
    print("Summary of open ports ", host, open_ports)        

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Simple port scanner")
        parser.add_argument("--target", "-t", dest="host", help="Target host to scan.")
        parser.add_argument("--ports", "-p", dest="port_range", default="1-65535", help="Specify port range to scan, if left blank ports 1 - 65535 will be scanned.")
        args = parser.parse_args()
        host, port_range = args.host, args.port_range

        start_port, end_port = port_range.split("-")
        start_port, end_port = int(start_port), int(end_port)

        ports = [ p for p in range(start_port, end_port)]

        main(host, ports)
    except KeyboardInterrupt:
        print("Stop scanning...")                                        # Catch KeyboardInterrupt 
