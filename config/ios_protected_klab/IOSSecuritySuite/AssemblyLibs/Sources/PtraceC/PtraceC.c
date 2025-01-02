#include <stdio.h>
#import <dlfcn.h>
#import <sys/types.h>
#include "PtraceC.h"
#include <stdlib.h>
//disable attach by ptrace
inline int set_pgdb(int x) {
    const char * v1;
    
    time_t t;
    srand((unsigned) t);
    int y = rand();
    
#if defined (__arm64__)
    
    if (x * (x + 1) % 2 == 0) {
        v1 = "run";
        asm volatile(
            "mov x0, #26\n" // ptrace
            "mov x1, #31\n" // PT_DENY_ATTACH
            "mov x2, #0\n"
            "mov x3, #0\n"
            "mov x16, #0\n"
            "svc #128\n"// make syscall
        );
    }
    else if ( y > 10 || x * (x + 1) % 2 == 0) {
        v1 = "don't run it";
        asm volatile(
            "mov x0, #26\n" // ptrace
            "mov x1, #31\n" // PT_DENY_ATTACH
            "mov x2, #0\n"
            "mov x3, #0\n"
            "mov x16, #0\n"
            "svc #128\n"// make syscall
        );
    }
    y = rand();
    x = rand();
    if (x * (x + 1) % 2 == 0) {
        puts(v1);
    }
    else if ( y > 10 || x * (x + 1) % 2 == 0) {
        puts(v1);
    }
#else
#endif
    puts(v1);
    return 1;
}

