//
// Created by li-j on 2020-11-04.
//

#ifndef TUOKEAPK_CHECKSUM_H
#define TUOKEAPK_CHECKSUM_H

#include <stdbool.h>
#include <stdlib.h>

#define MAX_LINE 512
#define MAX_LENGTH 256
#define NUM_LIBS 4
#define LIBS_MASK 55
//libil2cpp.so  libc.so   libart.so libklbsqlite3.so
#define LIBS_TO_CHECK {{91, 94, 85, 94, 91, 5, 84, 71, 71, 25, 68, 88}, {91, 94, 85, 84, 25, 68, 88}, {91, 94, 85, 86, 69, 67, 25, 68, 88}, {91, 94, 85, 92, 91, 85, 68, 70, 91, 94, 67, 82, 4, 25, 68, 88}}
#define MAX_LIB_NAME_SIZE 30

typedef struct stTextSection{
    unsigned long memsize;
    unsigned long checksum;
    unsigned long memsum;
    bool isset;
}textSection;

void parse_proc_maps_to_fetch_path(char** filepaths);
bool fetch_checksum_of_library(const char* filePath, textSection** pTextSection);
bool fetch_checksum_of_library_signal_file(const char* filePath, textSection* pTextSection);
unsigned long checksum(void *buffer, size_t len);
void record_sum();
void scan_sum_exec_segments(char* map, textSection* pElfSectArr);
void loop_check();
ssize_t read_one_line(int fd, char *buf, unsigned int max_len);

#endif //TUOKEAPK_CHECKSUM_H
