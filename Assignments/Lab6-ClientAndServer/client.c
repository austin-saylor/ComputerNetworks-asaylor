/*
** client.c -- a stream socket client demo
*/

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

#define PORT "8000" // the port client will be connecting to 

#define MAXDATASIZE 100 // max number of bytes we can get at once 

// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

int main(int argc, char *argv[])
{
    int sockfd, numbytes;  
    char buf[MAXDATASIZE];
    char msg[MAXDATASIZE];
    struct addrinfo hints, *servinfo, *p;
    int rv;
    char s[INET6_ADDRSTRLEN];

    if (argc != 3) {
        fprintf(stderr,"usage: client hostname\n");
        exit(1);
    }

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if ((rv = getaddrinfo(argv[1], PORT, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    // loop through all the results and connect to the first we can
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("client: socket");
            continue;
        }

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            close(sockfd);
            perror("client: connect");
            continue;
        }

        break;
    }

    if (p == NULL) {
        fprintf(stderr, "client: failed to connect\n");
        return 2;
    }

    inet_ntop(p->ai_family, get_in_addr((struct sockaddr *)p->ai_addr),
            s, sizeof s);
    printf("[CLIENT]: connecting to %s\n", s);

    freeaddrinfo(servinfo); // all done with this structure

    // Get message from user
    /*
    printf("Enter a message to send: ");
    fgets(message, MAXDATASIZE, stdin);
    message[strcspn(message, "\n")] = '\0'; // Remove newline character
    */

    // Send the message to the server
    if (send(sockfd, argv[2], strlen(argv[2]), 0) == -1) {
        perror("send");
        exit(1);
    }
    printf("[CLIENT]: message sent\n");

    // Receive response from the server
    if ((numbytes = recv(sockfd, buf, MAXDATASIZE-1, 0)) == -1) {
        perror("recv");
        exit(1);
    }

    buf[numbytes] = '\0';
    printf("[CLIENT]: message received: '%s'\n",buf);

    if (strcmp(argv[2], "1") == 0) {
        while (strcmp(buf, "Goodbye") != 0) {
            // Get message from user
            printf("[CLIENT]: Enter a message to send: ");
            fgets(msg, MAXDATASIZE, stdin);
            msg[strcspn(msg, "\n")] = '\0'; // Remove newline character

            // Send the message to the server
            if (send(sockfd, msg, strlen(msg), 0) == -1) {
                perror("send");
                exit(1);
            }
            printf("[CLIENT]: message sent!\n");

            // Receive response from the server
            if ((numbytes = recv(sockfd, buf, MAXDATASIZE-1, 0)) == -1) {
                perror("recv");
                exit(1);
            }

            buf[numbytes] = '\0';

            if (strcmp(buf, "Goodbye") == 0) {
                printf("[CLIENT]: %s!\n", buf);
            } else {
                printf("[CLIENT]: message received: '%s'\n", buf);
            }
        }
    } 
    else if  (strcmp(argv[2], "2") == 0) 
    {
        printf("Transferred File:\n");

        while ((numbytes = recv(sockfd, buf, MAXDATASIZE, 0)) > 0) {
            buf[numbytes] = '\0'; // Null-terminate the buffer
            printf("%s", buf);    // Print the received chunk
        }

        if (numbytes == -1) {
            perror("recv");
            exit(1);
        }

        printf("\n[CLIENT]: File transfer completed successfully.\n");
    }

    close(sockfd);
    return 0;
}
