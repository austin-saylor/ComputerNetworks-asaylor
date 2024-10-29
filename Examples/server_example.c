int main(int argc, char* argv[])
{
    char* buffer;
    char* sendBuffer;
    buffer = malloc(1024);
    sendBuffer = malloc(1024);

    FILE *file = fopen("test.txt", "r");
    fseek(file, 0, SEEK_END);
    long fileSize = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *buffer = malloc(fileSize+1);

    fread(buffer, 1, fileSize, file);

    fclose(file);

    char* sendBuffer;
    sendBuffer = malloc(1024);

    sprintf(sendBuffer, "%ld", fileSize);
    send(clientSocket, sendBuffer, strlen(sendBuffer), 0);
    memset(sendBuffer, 0, strlen(sendBuffer));

    recv(clientSocket, sendBuffer, 1024, 0);
    printf("%s\n", sendBuffer);
    memset(sendBuffer, 0, strlen(sendBuffer));

    send(clientSocket, buffer, fileSize, 0);
}