#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char* argv[])
{
    int clientSocket;
    struct sockaddr_in address;

    address.sin_family = AF_INET;
    address.sin_port = htons(1234);
    inet_pton(AF_INET, "127.0.0.1", &address.sin_addr);

    clientSocket = socket(AF_INET, SOCK_STREAM, 0);

    // connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen)
    connect(clientSocket, (struct sockaddr *)&address, sizeof(address));

    FILE *file = fopen("client_text.txt", "w");
    char* buffer;
    buffer = malloc(1024);
    memset(buffer, 0, 1024);

    recv(clientSocket, buffer, 1024, 0);
    long fileSize = atol(buffer);
    printf("File size is: %ld\n", fileSize);
    memset(buffer, 0, strlen(buffer));

    sprintf(buffer, "Ready to receive");
    // printf("Buffer length: %d\n", strlen(buffer));
    send(clientSocket, buffer, strlen(buffer), 0);
    memset(buffer, 0, strlen(buffer));

    char* recvBuffer;
    recvBuffer = malloc(1024);
    long recvSize = 0;
    while(recvSize < fileSize)
    {
        int size = recv(clientSocket, recvBuffer, 1024, 0);
        fwrite(recvBuffer, 1, size, file);
        recvSize += size;
        memset(recvBuffer, 0, size);
    }
    fclose(file);

    // char* sendBuffer;
    // char* recvBuffer;

    // sendBuffer = malloc(1024);
    // recvBuffer = malloc(1024);
    // while(1)
    // {
    //     read(0, sendBuffer, 1024);
    //     // strcat(sendBuffer, "Test from client");
    //     send(clientSocket, sendBuffer, strlen(sendBuffer), 0);

    //     recv(clientSocket, recvBuffer, 1024, 0);
    //     printf("Received from server: %s\n", recvBuffer);
    //     memset(sendBuffer, 0, 1024);
    //     memset(recvBuffer, 0, 1024);
    // }


    
    return 0;
}