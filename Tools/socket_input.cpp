#include "socket_input.h"
#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>
#include <stdexcept>
#include <vector>
#include <sstream>

#ifndef HOST_IP
 #define HOST_IP "0.0.0.0"
#endif
#ifndef PORT_NUM
 #define PORT_NUM 5005
#endif
#ifndef BUF_BYTES
 #define BUF_BYTES 1024
#endif

static int server_fd = -1;  // server socket
static int client_fd = -1;  // client socket
static char buf[BUF_BYTES];
static std::vector<double> last_values = {-1.0, -1.0, 0.0, -1.0, 0.0};

static void init_listener()
{
    if (client_fd >= 0) return;  // already connected

    try {
        server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd < 0) {
            std::cerr << "Server socket creation failed" << std::endl;
            return;
        }

        int reuse = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = inet_addr(HOST_IP);
        addr.sin_port = htons(PORT_NUM);

        if (bind(server_fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            std::cerr << "Bind failed" << std::endl;
            close(server_fd);
            return;
        }

        std::cout << "Server listening on " << HOST_IP << ":" << PORT_NUM << std::endl;
        listen(server_fd, 1);

        sockaddr_in client_addr{};
        socklen_t client_len = sizeof(client_addr);
        client_fd = accept(server_fd, reinterpret_cast<sockaddr*>(&client_addr), &client_len);
        
        if (client_fd < 0) {
            std::cerr << "Accept failed" << std::endl;
            return;
        }

        std::cout << "Connection established with "
                  << inet_ntoa(client_addr.sin_addr) << ":"
                  << ntohs(client_addr.sin_port) << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Server error: " << e.what() << std::endl;
        cleanup_sockets();
    }
}

double get_socket_sample(int index) {
    init_listener();
    if (client_fd < 0) return 0.0;

    // Read new data for every call to match Python behavior
    char binary_buf[BUF_BYTES];
    ssize_t n = recv(client_fd, binary_buf, BUF_BYTES - 1, 0);
    if (n <= 0) return 0.0;

    // Ensure null termination and convert to string
    binary_buf[n] = '\0';
    std::string data_str(binary_buf);
    
    // Parse space-separated values
    std::stringstream ss(data_str);
    std::vector<double> values;
    double value;
    
    while (ss >> value && values.size() < 5) {
        values.push_back(value);
    }

    if (values.size() != 5) {
        std::cerr << "Error: Expected 5 values, got " << values.size() << std::endl;
        return last_values[index]; // Return last valid value on error
    }

    // Store values for error handling
    last_values = values;

    // Print formatted output like Python version
    std::cout << "Time: " << values[0] << "s, Counter: " << values[1] << ", Amplitude: " << values[2] << ", "
              << "Position: " << values[3] << "°, Velocity: " << values[4] << "°/s" << std::endl;

    // std::cout << "Value to return at index: "<< index << " - "<< values[index] << std::endl;

    // Send acknowledgment
    const char* ack = "ACK\n";
    send(client_fd, ack, strlen(ack), 0);

    return values[index];
}

void cleanup_sockets() {
    if (client_fd >= 0) {
        close(client_fd);
        std::cout << "Client socket closed." << std::endl;
        client_fd = -1;
    }
    if (server_fd >= 0) {
        close(server_fd);
        std::cout << "Server socket closed." << std::endl;
        server_fd = -1;
    }
}
