#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <netdb.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>

#include <arpa/inet.h>

#define PORT "8000" // the port to be used
#define MAXDATASIZE 100 // max size for string transfers

// Get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa) 
{
    if (sa->sa_family == AF_INET) 
    {
        return &(((struct sockaddr_in *)sa)->sin_addr);
    }
    return &(((struct sockaddr_in6 *)sa)->sin6_addr);
}

int connect_to_server(const char *hostname) 
{
    struct addrinfo hints, *servinfo, *p;
    int rv, sockfd;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if ((rv = getaddrinfo(hostname, PORT, &hints, &servinfo)) != 0) 
    {
        fprintf(stderr, "[CLIENT]: getaddrinfo: %s\n", gai_strerror(rv));
        return -1;
    }

    for (p = servinfo; p != NULL; p = p->ai_next) 
    {
        // Create a socket
        if ((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1) 
        {
            // If socket creation fails, throw an error
            perror("[CLIENT]: socket\n");
            continue;
        }

        // Attempt connection to the server
        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) 
        {
            // If no connection was made, throw an error
            close(sockfd);
            perror("[CLIENT]: connect\n");
            continue;
        }
        break;
    }

    if (p == NULL) 
    {
        // If all connections failed, throw an error
        fprintf(stderr, "[CLIENT]: Failed to connect to server!\n");
        return -1;
    }

    // Get the server's IP address
    char ipstr[INET6_ADDRSTRLEN];
    inet_ntop(p->ai_family, get_in_addr((struct sockaddr *)p->ai_addr), ipstr, sizeof ipstr);

    // Print the connected IP
    printf("[CLIENT]: Connecting to %s\n", ipstr);

    // Free the linked list
    freeaddrinfo(servinfo);

    return sockfd;
}

void echo_mode(int sockfd) 
{
    char buf[MAXDATASIZE], msg[MAXDATASIZE]; // buffer and message declarations
    int numbytes;

    printf("[CLIENT]: Entering Echo Mode...\n");
    while (1) 
    {
        printf("[CLIENT]: Enter a message to echo: ");
        fgets(msg, MAXDATASIZE, stdin);
        msg[strcspn(msg, "\n")] = '\0';

        // Send the echo message to the server
        if (send(sockfd, msg, strlen(msg), 0) == -1) 
        {
            perror("[CLIENT]: send\n");
            break;
        }

        // Receive the echoed message from the server
        if ((numbytes = recv(sockfd, buf, MAXDATASIZE - 1, 0)) == -1)
        {
            perror("[CLIENT]: recv\n");
            break;
        }

        buf[numbytes] = '\0';
        if (strcmp(buf, "Goodbye") == 0)
        {
            // If the message from the server is "goodbye", print it and exit
            printf("[CLIENT]: %s\n", buf);
            break;
        }
        else
        {
            // Print the echoed message
            printf("[CLIENT]: Message received: '%s'\n", buf);
        }
    }
}

void file_transfer_mode(int sockfd)
{
    char buf[MAXDATASIZE];
    int numbytes;

    printf("[CLIENT]: Entering File Transfer Mode...\n");
    printf("[CLIENT]: Transferred File:\n");
    while ((numbytes = recv(sockfd, buf, MAXDATASIZE, 0)) > 0) 
    {
        // Receive the transferred file
        buf[numbytes] = '\0';
        printf("%s", buf);
    }

    if (numbytes == -1) {
        // If there's no file, handle error
        perror("[CLIENT]: recv\n");
    } else {
        // If the transfer was successful, print the confirmation
        printf("\n[CLIENT]: File transfer completed successfully!\n");
    }
}

int main(int argc, char *argv[]) 
{
    if (argc != 3) 
    {
        // If there's not the correct amount of arguments
        fprintf(stderr, "[CLIENT]: Usage: client hostname mode\n");
        printf("[CLIENT]: ./client localhost <mode | 1 for echo, 2 for file transfer>\n");
        exit(1);
    }

    
    int sockfd = connect_to_server(argv[1]); // Attempt connection to the server
    if (sockfd == -1) 
    {
        // If the connection fails, terminate program
        exit(1);
    }

    if (send(sockfd, argv[2], strlen(argv[2]), 0) == -1) 
    {
        // Send the chosen mode to the server
        perror("[CLIENT]: send\n");
        exit(1);
    }

    if (strcmp(argv[2], "1") == 0) {
        // If the mode is 1, process echo mode
        echo_mode(sockfd);
    } else if (strcmp(argv[2], "2") == 0) {
        // If the mode is 2, process file transfer mode
        file_transfer_mode(sockfd);
    } else {
        // If the mode isn't 1 or 2, throw an error
        printf("[CLIENT]: ERROR: Unknown mode!\n");
    }

    close(sockfd);
    return 0;
}
