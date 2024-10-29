int main(int argc, char* argv[])
{
    address.sin_family = AF_INET;
    inet_pton(AF_INET, "127.0.0.1", &address.sin_addr);
    clientSocket = socket(AF_INET, SOCK_STREAM, 0);

    connect(clientSocket, (struct sockaddr *)&address, sizeof(address));

    FILE *file = fopen("client_text.txt", "w");
    char* buffer;
    buffer = malloc(1024);

    recv(clientSocket, buffer, 1024, 0);
    long fileSize = atol(buffer);
    memset(buffer, 0, strlen(buffer));
    sprintf(buffer, "Ready to receive");
    
    send(clientSocket, buffer, strlen(buffer), 0);
    memset(buffer, 0, strlen(buffer));

    char* recvBuffer;
    recvBuffer = malloc(1024);
    long recvSize = 0;
    while(recvSize < fileSize)
    {
        int recv(clientSocket, recvBuffer, 1024, 0);
        fwrite(recvBuffer, 1, size, file);
        recvSize += size;
        memset(recvBuffer, 0, size);
    }
    fclose(file);
}