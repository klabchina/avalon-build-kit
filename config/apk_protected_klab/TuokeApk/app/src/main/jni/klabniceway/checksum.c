//
// Created by li-j on 2020-11-04.
//
#include "checksum.h"
#include <elf.h>
#include <stdbool.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <android/log.h>
#include <string.h>
#include "kclibs.h"
#include <ctype.h>
#include "mylibc.h"

#include <asm/unistd.h>
#include "syscall_arch.h"
#include "syscalls.h"

static textSection* elfSectionArr[NUM_LIBS] = {NULL};

unsigned long checksum(void *buffer, size_t len)
{
    unsigned long seed = 0;
    uint8_t* buf = (uint8_t*)buffer;
    size_t i;
    for (i = 0; i < len; ++i)
        seed += (unsigned long)(*buf++);
    return seed;
}

ssize_t read_one_line(int fd, char *buf, unsigned int max_len) {
    char b;
    ssize_t ret;
    ssize_t bytes_read = 0;

    my_memset(buf, 0, max_len);

    do {
        ret = read(fd, &b, 1);

        if (ret != 1) {
            if (bytes_read == 0) {
                // error or EOF
                return -1;
            } else {
                return bytes_read;
            }
        }

        if (b == '\n') {
            return bytes_read;
        }

        *(buf++) = b;
        bytes_read += 1;

    } while (bytes_read < max_len - 1);

    return bytes_read;
}


__attribute__((section (".kcniceway")))
void parse_proc_maps_to_fetch_path(char** filepaths){
    int fd = 0;
    char map[MAX_LINE];
    int counter = 0;
    if ((fd = my_openat(AT_FDCWD, "/proc/self/maps", O_RDONLY | O_CLOEXEC, 0)) != 0) {

        char libstocheck[NUM_LIBS][MAX_LIB_NAME_SIZE] = LIBS_TO_CHECK;
        while ((read_one_line(fd, map, MAX_LINE)) > 0) {
            for(int i = 0; i < NUM_LIBS;i++) {
                char* char_pt1 = libstocheck[i];
                char lib_names[51];
                lib_names[0] = '\0';
                strncat(lib_names, char_pt1, strlen(char_pt1));
                ObfuscateChar(LIBS_MASK, lib_names, strlen(lib_names));

                if (my_strstr(map, lib_names) != NULL) {
                    char tmp[MAX_LENGTH]="";
                    char path[MAX_LENGTH]="";
                    char buf[5]="";
                    sscanf(map, "%s %s %s %s %s %s", tmp, buf, tmp, tmp, tmp, path);
                    if(buf[2] == 'x' && filepaths[i] == "") {
                        size_t size = strlen(path)+1;
                        filepaths[i] = malloc(size);
                        strlcpy(filepaths[i], path, size);
                        counter++;
                    }
                }
            }
            if(counter == NUM_LIBS)
                break;
        }
        my_close(fd);
    }
}

__attribute__((section (".kcniceway")))
bool fetch_checksum_of_library_signal_file(const char* filePath, textSection* pTextSection){
    extern int global_api_level;
    if (filePath == "" || global_api_level >= ANDROID_10)
    {
        return false;
    }

    int fd;

    fd = my_openat(AT_FDCWD, filePath, O_RDONLY | O_CLOEXEC, 0);
    if(fd < 0){
        return NULL;
    }

    unsigned long memsize = 0;
#ifdef _64_BIT
    Elf64_Ehdr ehdr;
    Elf64_Shdr sectHdr;
    size_t ehdr_size = sizeof(Elf64_Ehdr);
    size_t shdr_size = sizeof(Elf64_Shdr);
#else
    Elf32_Ehdr ehdr;
    Elf32_Shdr sectHdr;
    size_t ehdr_size = sizeof(Elf32_Ehdr);
    size_t shdr_size = sizeof(Elf32_Shdr);
#endif

    my_read(fd, &ehdr, ehdr_size);
    my_lseek(fd, (off_t)ehdr.e_shoff, SEEK_SET);

    for(int i = 0; i < ehdr.e_shnum; i++){
        my_memset(&sectHdr,0,shdr_size);
        my_read(fd, &sectHdr, shdr_size);

        //__android_log_print(ANDROID_LOG_VERBOSE, APPNAME, "SectionHeader[%d][%ld]", sectHdr.sh_name, sectHdr.sh_flags);

        //Typically PLT and Text Sections are executable sections which are protected
        if(sectHdr.sh_flags & SHF_ALLOC && sectHdr.sh_flags & SHF_EXECINSTR){
            if(sectHdr.sh_offset+sectHdr.sh_size > memsize){
                memsize = sectHdr.sh_offset + sectHdr.sh_size;
            }
        }
    }

    if(memsize == 0){
        __android_log_print(ANDROID_LOG_WARN, "CHECKSUM", "No executable section found. Suspicious");
        my_close(fd);
        return false;
    }
    //This memory is not released as the checksum is checked in a thread
    my_lseek(fd, 0, SEEK_SET);
    uint8_t* buffer = malloc( memsize * sizeof(uint8_t));
    my_read(fd, buffer, memsize);
    pTextSection->memsize = memsize;
    pTextSection->checksum = checksum(buffer, memsize);
    pTextSection->isset = true;

    free(buffer);
    my_close(fd);
    return true;
}


__attribute__((section (".kcniceway")))
bool fetch_checksum_of_library(const char* filePath, textSection** pTextSection){
    extern int global_api_level;
    if (filePath == "" || global_api_level >= ANDROID_10)
    {
        //not exist
        *pTextSection = malloc(sizeof(textSection));
        (*pTextSection)->memsize = 0;
        (*pTextSection)->checksum = 0;
        (*pTextSection)->isset = false;
        return false;
    }

    int fd;

    fd = my_openat(AT_FDCWD, filePath, O_RDONLY | O_CLOEXEC, 0);
    if(fd < 0){
        return NULL;
    }

    unsigned long memsize = 0;

#ifdef _64_BIT
    Elf64_Ehdr ehdr;
    Elf64_Shdr sectHdr;
    size_t ehdr_size = sizeof(Elf64_Ehdr);
    size_t shdr_size = sizeof(Elf64_Shdr);
#else
    Elf32_Ehdr ehdr;
    Elf32_Shdr sectHdr;
    size_t ehdr_size = sizeof(Elf32_Ehdr);
    size_t shdr_size = sizeof(Elf32_Shdr);
#endif

    my_read(fd, &ehdr, ehdr_size);
    my_lseek(fd, (off_t)ehdr.e_shoff, SEEK_SET);

    for(int i = 0; i < ehdr.e_shnum; i++){
        my_memset(&sectHdr,0,shdr_size);
        my_read(fd, &sectHdr, shdr_size);

        //__android_log_print(ANDROID_LOG_VERBOSE, APPNAME, "SectionHeader[%d][%ld]", sectHdr.sh_name, sectHdr.sh_flags);

        //Typically PLT and Text Sections are executable sections which are protected
        if(sectHdr.sh_flags & SHF_ALLOC && sectHdr.sh_flags & SHF_EXECINSTR){
            if(sectHdr.sh_offset+sectHdr.sh_size > memsize){
                memsize = sectHdr.sh_offset + sectHdr.sh_size;
            }
        }
    }

    if(memsize == 0){
        __android_log_print(ANDROID_LOG_WARN, "CHECKSUM", "No executable section found. Suspicious");
        my_close(fd);
        return false;
    }
    //This memory is not released as the checksum is checked in a thread
    *pTextSection = malloc(sizeof(textSection));
    my_lseek(fd, 0, SEEK_SET);
    uint8_t* buffer = malloc( memsize * sizeof(uint8_t));
    my_read(fd, buffer, memsize);
    (*pTextSection)->memsize = memsize;
    (*pTextSection)->checksum = checksum(buffer, memsize);
    (*pTextSection)->isset = true;

    free(buffer);
    my_close(fd);
    return true;
}


//sum loop check
__attribute__((section (".kcniceway")))
void scan_sum_exec_segments(char* map, textSection* pElfSectArr){
    unsigned long start, end;
    char buf[MAX_LINE]="";
    char path[MAX_LENGTH]="";
    char tmp[100]="";

    sscanf(map, "%lx-%lx %s %s %s %s %s", &start, &end, buf, tmp, tmp, tmp, path );

    if (!pElfSectArr->isset)
    {
        size_t size = strlen(path)+1;
        char* file_path = malloc(size);
        strlcpy(file_path, path, size);
        fetch_checksum_of_library_signal_file(file_path, pElfSectArr);
        free(file_path);
    }

    if (buf[2] == 'x' && buf[0] == 'r') {
        uint8_t *buffer = (uint8_t *) start;
        unsigned long memsize = end - start;
        extern int global_api_level;
        if (memsize >= pElfSectArr->memsize && global_api_level < ANDROID_10)
            memsize = pElfSectArr->memsize;
        unsigned long output = checksum(buffer, memsize);

        pElfSectArr->memsum += output;
    }
}

__attribute__((section (".kcniceway")))
void loop_check(){
    int fd = 0;
    char map[MAX_LINE];

    if ((fd = my_openat(AT_FDCWD, "/proc/self/maps", O_RDONLY | O_CLOEXEC, 0 )) != 0) {
        for(int i = 0; i < NUM_LIBS; i++) {
            elfSectionArr[i]->memsum = 0;
        }

        char libstocheck[NUM_LIBS][MAX_LIB_NAME_SIZE] = LIBS_TO_CHECK;
        while ((read_one_line(fd, map, MAX_LINE)) > 0) {
            for(int i = 0; i < NUM_LIBS; i++) {
                char* char_pt1 = libstocheck[i];
                char lib_names[51];
                lib_names[0] = '\0';
                strncat(lib_names, char_pt1, strlen(char_pt1));
                ObfuscateChar(LIBS_MASK, lib_names, strlen(lib_names));

                if (my_strstr(map, lib_names) != NULL) {
                    scan_sum_exec_segments(map, elfSectionArr[i]);
                }
            }
        }

        //check sum is correct
        for(int i = 0; i < NUM_LIBS; i++)
        {
            // add memsum less than 0  android 10+ protected
            if (elfSectionArr[i]->isset && elfSectionArr[i]->memsum > 0 && elfSectionArr[i]->checksum != elfSectionArr[i]->memsum)
            {
                kill(getpid(), SIGKILL);
            }
            else if (!elfSectionArr[i]->isset && elfSectionArr[i]->memsum != 0)
            {
                //record from memory
                elfSectionArr[i]->checksum = elfSectionArr[i]->memsum;
                elfSectionArr[i]->isset = true;
            }
        }

    } else {
        __android_log_print(ANDROID_LOG_WARN, "error", "Error opening /proc/self/maps. That's usually a bad sign.");
    }
    my_close(fd);

}


void record_sum()
{
    char* filePaths[NUM_LIBS];
    for(int i = 0; i < NUM_LIBS; i++) {
        filePaths[i] = "";
    }

    parse_proc_maps_to_fetch_path(filePaths);
    for(int i = 0; i < NUM_LIBS; i++)
    {
        fetch_checksum_of_library(filePaths[i], &elfSectionArr[i]);
        if (filePaths[i] != "")
        {
            free(filePaths[i]);
        }
    }

}