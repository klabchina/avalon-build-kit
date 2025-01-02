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
#define LIBS_MASK 66
//libklabniceway.so libassistant1.so
#define LIBS_TO_CHECK {{46, 43, 32, 41, 46, 35, 32, 44, 43, 33, 39, 53, 35, 59, 108, 49, 45}, {46, 43, 32, 35, 49, 49, 43, 49, 54, 35, 44, 54, 115, 108, 49, 45}}
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
