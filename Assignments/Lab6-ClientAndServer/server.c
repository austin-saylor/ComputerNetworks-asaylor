/*
** server.c -- a stream socket server demo
*/

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

#define PORT "8000"  // the port users will be connecting to

#define MAXDATASIZE 100 // max number of bytes we can get at once 
#define BACKLOG 10   // how many pending connections queue will hold

void sigchld_handler(int s)
{
    // waitpid() might overwrite errno, so we save and restore it:
    int saved_errno = errno;

    while(waitpid(-1, NULL, WNOHANG) > 0);

    errno = saved_errno;
}


// get sockaddr, IPv4 or IPv6:
void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

void string_split(char *s, int index, char *first, char *second);

int main(void)
{
    int sockfd, new_fd, numbytes;  // listen on sock_fd, new connection on new_fd
    char buf[MAXDATASIZE];
    char msg[MAXDATASIZE];
    struct addrinfo hints, *servinfo, *p;
    struct sockaddr_storage their_addr; // connector's address information
    socklen_t sin_size;
    struct sigaction sa;
    int yes=1;
    char s[INET6_ADDRSTRLEN];
    int rv;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE; // use my IP

    if ((rv = getaddrinfo(NULL, PORT, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return 1;
    }

    // loop through all the results and bind to the first we can
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("[SERVER]: socket");
            continue;
        }

        if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &yes,
                sizeof(int)) == -1) {
            perror("setsockopt");
            exit(1);
        }

        if (bind(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            close(sockfd);
            perror("[SERVER]: bind");
            continue;
        }

        break;
    }

    freeaddrinfo(servinfo); // all done with this structure

    if (p == NULL)  {
        fprintf(stderr, "[SERVER]: failed to bind\n");
        exit(1);
    }

    if (listen(sockfd, BACKLOG) == -1) {
        perror("listen");
        exit(1);
    }

    sa.sa_handler = sigchld_handler; // reap all dead processes
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    if (sigaction(SIGCHLD, &sa, NULL) == -1) {
        perror("sigaction");
        exit(1);
    }

    printf("[SERVER]: waiting for connections... \n");

    while(1) {  // main accept() loop
        sin_size = sizeof their_addr;
        new_fd = accept(sockfd, (struct sockaddr *)&their_addr, &sin_size);
        if (new_fd == -1) {
            perror("accept");
            continue;
        }

        inet_ntop(their_addr.ss_family,
            get_in_addr((struct sockaddr *)&their_addr),
            s, sizeof s);
        printf("[SERVER]: got connection from %s\n", s);

        if (!fork()) { // this is the child process
            close(sockfd); // child doesn't need the listener

            // Receive the mode from the client
            if ((numbytes = recv(new_fd, buf, MAXDATASIZE-1, 0)) == -1) {
                perror("recv");
                close(new_fd);
                exit(1);
            }
            buf[numbytes] = '\0'; // Null-terminate the received string

            // Parse the mode
            if (strcmp(buf, "1") == 0) { // Echo mode
                char *mode_init = "[SERVER]: Entered Echo Mode!";
                char echo[MAXDATASIZE];

                printf("%s\n", mode_init);

                // Send acknowledgment to the client
                if (send(new_fd, mode_init, strlen(mode_init), 0) == -1) {
                    perror("[SERVER]: send");
                    close(new_fd);
                    exit(1);
                }

                while (1) { // Echo loop
                    if ((numbytes = recv(new_fd, echo, MAXDATASIZE-1, 0)) == -1) {
                        perror("[SERVER]: recv");
                        break;
                    }

                    echo[numbytes] = '\0'; // Null-terminate received message

                    if (strcmp(echo, "close") == 0) { // Client wants to end the connection
                        // Send a goodbye message before closing
                        if (send(new_fd, "Goodbye", 7, 0) == -1) {
                            perror("[SERVER] send");
                        }

                        printf("[SERVER]: Closed client connection");
                        break;
                    }

                    // Echo the message back to the client
                    if (send(new_fd, echo, strlen(echo), 0) == -1) {
                        perror("send");
                        break;
                    }

                    printf("[SERVER]: echoed: '%s'\n", echo);
                }
            } else if (strcmp(buf, "2") == 0) { // File Transfer mode
                char *mode_init = "[SERVER]: Entered File Transfer Mode!";
                FILE* file = fopen("file.txt", "r");
                char line[MAXDATASIZE];

                printf("%s\n", mode_init);

                // Send acknowledgment to the client
                if (send(new_fd, mode_init, strlen(mode_init), 0) == -1) {
                    perror("send");
                    close(new_fd);
                    exit(1);
                }

                if (file != NULL)
                {
                    while(fgets(line, 1000, file))
                    {
                        //printf("%s", line);
                        if (send(new_fd, line, strlen(line), 0) == -1) {
                            perror("send");
                            exit(1);
                        }
                    }
                    fclose(file);
                }
                else
                {
                    fprintf(stderr, "ERROR: Cannot open file!\n");
                }
            } else {
                printf("ERROR: Unknown mode\n");
            }

            close(new_fd); // Close the connection
            exit(0);
        }

        close(new_fd);  // parent doesn't need this
    }

    return 0;
}

void string_split(char *s, int index, char *first, char *second)
{
  int length = strlen(s);
  
  // we can't do anything if the index is greater than the length of the string
  if (index < length)
  {
    // copy the characters from 0-(index-1) to the first character array
    for (int i = 0; i < index; i++)
      first[i] = s[i];
    first[index] = '\0';
    
    // copy the characters from index-strlen(s) to the second character array
    for (int i = index; i <= length; i++)
      second[i - index] = s[i];
  }
}
