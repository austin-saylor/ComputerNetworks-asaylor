#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <arpa/inet.h>

int main(int argc, char* argv[])
{
    int socketNum, clientSocket;
    int bindStatus, listenStatus;
    int yes = 1;
    struct sockaddr_in address;
    struct addrinfo hints, *res;
    struct sockaddr_in clientAddress;
    int addrSize = sizeof(struct sockaddr_storage);

    // address.sin_addr.s_addr = INADDR_ANY;
    // address.sin_family = AF_INET;
    // address.sin_port = htons(1234);

    memset(&hints, 0, sizeof(hints));

    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;
    getaddrinfo(NULL, "1234", &hints, &res);


    // socketNum = socket(AF_INET, SOCK_STREAM, 0);
    socketNum = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    setsockopt(socketNum, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    // bindStatus = bind(socketNum, (struct sockaddr *)&address, sizeof(address));
    bindStatus = bind(socketNum, res->ai_addr, res->ai_addrlen);
    listenStatus = listen(socketNum, 5);


    printf("Socket: %d\n", socketNum);
    printf("bindStatus: %d\n", bindStatus);
    printf("listenStatus: %d\n", listenStatus);

    clientSocket = accept(socketNum, (struct sockaddr *)&address, (socklen_t *)&addrSize);

    printf("clientSocket: %d\n", clientSocket);
    // char buffer[1024] = {0};
    // char sendBuffer[1024] = {0};
    // char* buffer;
    // char* sendBuffer;
    // buffer = malloc(1024);
    // sendBuffer = malloc(1024);

    FILE *file = fopen("client.out", "r");
    fseek(file, 0, SEEK_END);
    long fileSize = ftell(file);
    fseek(file, 0, SEEK_SET);
    // rewind(file);

    char *buffer = malloc(fileSize+1);

    fread(buffer, 1, fileSize, file);

    fclose(file);

    char* sendBuffer;
    sendBuffer = malloc(1024);
    memset(sendBuffer, 0, 1024);

    sprintf(sendBuffer, "%ld", fileSize);
    send(clientSocket, sendBuffer, strlen(sendBuffer), 0);
    memset(sendBuffer, 0, strlen(sendBuffer));
    
    recv(clientSocket, sendBuffer, 1024, 0);
    printf("%s\n", sendBuffer);
    memset(sendBuffer, 0, strlen(sendBuffer));

    send(clientSocket, buffer, fileSize, 0);

    // while(1)
    // {
    //     // char* sendBuffer;
    //     // malloc(buffer, 1024);
    //     // recv(clientSocket, buffer, 1024, 0);
    //     // printf("Received: %s\n", buffer);
    //     // // strcat(sendBuffer, "From Server: ");
    //     // // strcat(sendBuffer, buffer);
    //     // // sprintf(sendBuffer, "From Server: %s\n", buffer);
    //     // send(clientSocket, buffer, strlen(buffer), 0);
    //     // memset(buffer, 0, sizeof(buffer));
    //     // memset(sendBuffer, 0, sizeof(sendBuffer));
    // }

    // while(1)
    // {

    // }
    return 0;
}