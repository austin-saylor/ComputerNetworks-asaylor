#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <sys/wait.h>
#include <signal.h>

#define PORT "8000" // the port to be used
#define MAXDATASIZE 100 // max size for file transfers
#define BACKLOG 10

void sigchld_handler(int s) 
{
    // waitpid() might overwrite errno, so we save and restore it:
    int saved_errno = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0);
    errno = saved_errno;
}

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa) 
{
    if (sa->sa_family == AF_INET) 
    {
        return &(((struct sockaddr_in *)sa)->sin_addr);
    }
    return &(((struct sockaddr_in6 *)sa)->sin6_addr);
}

int setup_server() 
{
    struct addrinfo hints, *servinfo, *p;
    int rv, sockfd, yes = 1;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    if ((rv = getaddrinfo(NULL, PORT, &hints, &servinfo)) != 0) 
    {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return -1;
    }

    for (p = servinfo; p != NULL; p = p->ai_next) 
    {
        // Create a socket
        if ((sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) == -1) 
        {
            // If socket creation fails, throw an error
            perror("[SERVER]: socket\n");
            continue;
        }

        // Allow the socket to reuse addresses
        if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(int)) == -1) 
        {
            perror("setsockopt\n");
            exit(1);
        }

        // Bind the socket to an address
        if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) 
        {
            // If the socket fails to bind, throw an error
            close(sockfd);
            perror("[SERVER]: bind\n");
            continue;
        }

        break;
    }

    freeaddrinfo(servinfo);

    if (p == NULL) 
    {
        // If the server fails to bind to the socket, throw an error
        fprintf(stderr, "[SERVER]: failed to bind\n");
        return -1;
    }

    // Set the server to listen on the socket
    if (listen(sockfd, BACKLOG) == -1) 
    {
        // If the server cannot listen on the socket, throw an error
        perror("[SERVER]: listen\n");
        exit(1);
    }

    return sockfd;
}

void echo_mode(int new_fd) 
{
    char buf[MAXDATASIZE];
    int numbytes;

    printf("[SERVER]: Entering Echo Mode...\n");

    // While the server is receiving messages
    while ((numbytes = recv(new_fd, buf, MAXDATASIZE - 1, 0)) > 0) 
    {
        buf[numbytes] = '\0';

        printf("[SERVER]: Received message from server: '%s'\n", buf);
        if (strcmp(buf, "close") == 0) 
        {
            // If the received message is 'close', send 'goodbye'
            send(new_fd, "Goodbye", 7, 0);
            printf("[SERVER]: Sent message to client: '%s'\n", "Goodbye");
            break;
        }

        // Send the message that was received back to the client
        send(new_fd, buf, strlen(buf), 0);
        printf("[SERVER]: Sent message to client: '%s'\n", buf);
    }

    if (numbytes == -1) 
    {
        // If a message wasn't received, throw an error
        perror("[SERVER]: recv\n");
    }
}

void file_transfer(int new_fd) 
{
    FILE *file = fopen("file.txt", "r"); // Open file for reading
    char buf[MAXDATASIZE];
    size_t bytesRead;

    printf("[SERVER]: Entering File Transfer Mode...\n");

    if (file == NULL) 
    {
        // If there's no file, throw an error
        fprintf(stderr, "[SERVER]: ERROR: Cannot open file!\n");
        return;
    }

    while ((bytesRead = fread(buf, 1, MAXDATASIZE, file)) > 0) 
    {
        // Send the file to the client
        if (send(new_fd, buf, bytesRead, 0) == -1) 
        {
            // If the file fails to send, throw an error
            perror("[SERVER]: send\n");
            fclose(file);
            return;
        }
    }

    fclose(file);
    printf("[SERVER]: File transfer completed successfully!\n");
}

void handle_client(int new_fd) 
{
    char buf[MAXDATASIZE];
    int numbytes;

    // Receive the selected mode from the client
    if ((numbytes = recv(new_fd, buf, MAXDATASIZE - 1, 0)) <= 0) 
    {
        // If no valid mode was received, throw an error
        if (numbytes == -1) perror("[SERVER]: recv\n");
        close(new_fd);
        return;
    }

    buf[numbytes] = '\0';

    // Execute one of the modes
    if (strcmp(buf, "1") == 0) {
        // If the mode is 1, process echo mode
        echo_mode(new_fd);
    } else if (strcmp(buf, "2") == 0) {
        // If the mode is 2, process file transfer mode
        file_transfer(new_fd);
    } else {
        // If the mode isn't 1 or 2, throw an error
        printf("[SERVER]: Unknown mode!\n");
    }

    close(new_fd);
}

int main(void) 
{
    int sockfd = setup_server(); // Set up the server
    if (sockfd == -1)
    {
        // If the set up fails, terminate program
        exit(1);
    }

    struct sockaddr_storage their_addr;
    socklen_t sin_size;
    char ipstr[INET6_ADDRSTRLEN];
    int new_fd;

    printf("[SERVER]: Waiting for connections...\n");

    while (1) {
        sin_size = sizeof their_addr;

        // Accept the connection from the client
        new_fd = accept(sockfd, (struct sockaddr *)&their_addr, &sin_size);
        if (new_fd == -1) 
        {
            perror("[SERVER]: accept\n");
            continue;
        }

        // Get the client's IP address
        inet_ntop(their_addr.ss_family, get_in_addr((struct sockaddr *)&their_addr), ipstr, sizeof ipstr);
        printf("[SERVER]: Got connection from %s\n", ipstr);

        if (!fork()) 
        {
            close(sockfd);
            handle_client(new_fd);
            exit(0);
        }

        close(new_fd);
    }

    return 0;
}
