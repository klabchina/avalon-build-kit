//
// Created by li-j on 2020-11-04.
//

#ifndef TUOKEAPK_CHECKSUM_H
#define TUOKEAPK_CHECKSUM_H

#include <stdbool.h>
#include <stdlib.h>

#define MAX_LINE 512
#define MAX_LENGTH 256
#define NUM_LIBS 2
#define LIBS_MASK 77
//libklabniceway.so libassistant2.so
#define LIBS_TO_CHECK {{33, 36, 47, 38, 33, 44, 47, 35, 36, 46, 40, 58, 44, 52, 99, 62, 34}, {33, 36, 47, 44, 62, 62, 36, 62, 57, 44, 35, 57, 127, 99, 62, 34}}
#define MAX_LIB_NAME_SIZE 30

typedef struct stTextSection{
    unsigned long memsize;
    unsigned long checksum;
    unsigned long memsum;
    bool isset;
}textSection;


void parse_proc_maps_to_fetch_path(char** filepaths);
bool fetch_checksum_of_library(const char* filePath, textSection** pTextSection, int idx);
bool fetch_checksum_of_library_signal_file(const char* filePath, textSection* pTextSection);
unsigned long checksum(void *buffer, size_t len);
void record_sum();
void scan_sum_exec_segments(char* map, textSection* pElfSectArr, int idx);
void loop_check();

#endif //TUOKEAPK_CHECKSUM_H
