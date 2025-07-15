import socket
import time
import numpy as np

def Socket_Connection_SC():
    HOST = '0.0.0.0'  # Listen on all available interfaces
    PORT = 5005

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        return client_socket

    except Exception as e:
        print(f"Server error: {e}")
        server_socket.close()
        return None

if __name__ == "__main__":
    client_socket = Socket_Connection_SC()
    if client_socket:
        print("Socket connection established successfully.")
        try:
            while True:
                # Receive data in format: "time counter position velocity\n"
                data = client_socket.recv(1024).decode().strip()
                if not data:
                    break
                
                # Parse the received data
                try:
                    time_val, counter, position, velocity = map(float, data.split())
                    print(f"Time: {time_val:.3f}s, Counter: {counter}, " 
                          f"Position: {position:.2f}°, Velocity: {velocity:.2f}°/s")
                    
                    # Process the data here if needed
                    
                    # Send acknowledgment back
                    response = "ACK\n"
                    client_socket.sendall(response.encode())
                    
                except ValueError as e:
                    print(f"Error parsing data: {data}")
                    print(f"Error message: {e}")
                
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, closing client socket.")
        finally:
            client_socket.close()
            print("Client socket closed.")
    else:
        print("Failed to establish socket connection.")
