#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <syslog.h>

int main()
{
    // printf("hello world!\n");
    int a, b;
    // sleep(5);
    for (int i = 0; i < 1000; i++) {
        for (int j = 0; j < 100000; j ++) {
            a = 1;
        }
    }
    while(scanf("%d %d", &a, &b) != EOF) {
        printf("%d\n", a + b);
    }
    return 0;
}