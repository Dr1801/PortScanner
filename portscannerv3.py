 import argparse
import socket
import time
import sys
from threading import Thread, Lock
from queue import Queue

threads = 1400                                                         
queue = Queue()                                                         
open_ports =  []                                                       
print_lock = Lock()                                                    
socket.setdefaulttimeout(0.15)                                    

def scan_ports(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
        s.connect((host, port))                                        
        with print_lock:                                                
            print('Port:',port, 'is open')
            open_ports.append(port)                                    
        s.close()
    except (socket.timeout, ConnectionRefusedError):                   
        pass

def scan_thread():
    global queue
    while True:
        worker = queue.get()                                           
        scan_ports(worker)                                             
        queue.task_done()

def main(host, ports):
    global queue
    startTime = time.time()                                            
    for t in range(threads):
        t = Thread(target=scan_thread)
        t.daemon = True
        t.start()                                                       

    for worker in ports:                                                
        queue.put(worker)

    queue.join()                                                       
    runtime = float("%0.2f" % (time.time() - startTime))               
    print("Run time: ", runtime, "seconds")
    lenth = len(open_ports)                                            
    for i in range(0, lenth - 1):
        for j in range(i + 1, lenth):
            if (open_ports[i] > open_ports[j]):            
                tmp = open_ports[i]
                open_ports[i] = open_ports[j]
                open_ports[j] = tmp
    print("Summary of open ports at the host", host, open_ports)       

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
        print("Interrupt received, scanning will stop...")              # Ctrl - c
