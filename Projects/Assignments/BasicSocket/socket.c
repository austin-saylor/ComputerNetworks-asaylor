#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <netinet/in.h>


void lookup(const char *hostname)
{
    struct addrinfo hints, *res, *i;
    int errcode;
    char ipstr[INET6_ADDRSTRLEN];

    memset(&hints, 0, sizeof hints); // make sure that the info struct is empty
    hints.ai_socktype = SOCK_STREAM; // prevent duplicate addresses

    errcode = getaddrinfo(hostname, NULL, &hints, &res);

    // Connect to the host and get the address info
    if (errcode != 0) 
    {
        // If no connection can be made
        fprintf(stderr, "getaddrinfo error: %s\n", gai_strerror(errcode));
    }
    else
    {

        printf("IP addresses for %s:\n\n", hostname);

        // Traverse the results until each address has been identified and displayed
        for (i = res; i != NULL; i = i->ai_next)
        {
            // Initialize variables to store the ip version and the address
            char *ipver;
            void *addr;

            if (i->ai_family == AF_INET) { // IPv4
                struct sockaddr_in *ipv4 = (struct sockaddr_in *)i->ai_addr; // Get the IPv4 address of the index
                addr = &(ipv4->sin_addr); // Assign the address to 'addr'
                ipver = "IPv4";
            } else { // IPv6
                struct sockaddr_in6 *ipv6 = (struct sockaddr_in6 *)i->ai_addr; // Get the IPv6 address of the index
                addr = &(ipv6->sin6_addr); // Assign the address to 'addr'
                ipver = "IPv6";
            }

            // convert the IP to a string and print it:
            inet_ntop(i->ai_family, addr, ipstr, sizeof ipstr);
            printf("  %s: %s\n", ipver, ipstr);
        }

        freeaddrinfo(res); // free the linked list
    }
}

int main(int argc, char *argv[])
{
    if (argc != 2) {
        // If no valid argument (hostname) is provided
        fprintf(stderr,"Error! No hostname provided. Please enter a hostname as shown below:\n");
        printf("usage: ./getipaddr.out <hostname>\n");
        return 1;
    }
    else
    {
        // If a valid hostname is provided, lookup the address info
        const char *hostname = argv[1];
        lookup(hostname);
    }
}