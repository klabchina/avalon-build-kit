//
// Created by li-j on 2020-08-26.
//
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include <stdlib.h>
#include <elf.h>
#include "kclibs.h"
#include <pthread.h>
#include <fcntl.h>
#include <sys/ptrace.h>
#include <sys/stat.h>
#include <dirent.h>
#include <ctype.h>
#include "checksum.h"
#include "internal_defines.h"
#include "mylibc.h"
#include <asm/unistd.h>
#include "syscall_arch.h"
#include "syscalls.h"

/*
 * KILL BY BREAK        0x01
 * kill by port         0x02
 * kill by file         0x03
 * kill by frida        0x04
 * KILL by Frida mem    0x05
 * Cann't open file frida ablity        0x06
 * Cann't open file port                0x07
 * Debug is On          0x08
 * Cann't open file status              0x09
 * Cann't open file maps                0x10
 * KILL by Frida in task status    0x0a
 * KILL by Frida in fd linjector   0x0b
 * KILL by magisk su   0x0c
 * KILL by magisk mount   0x0d
 *
 * */

void ObfuscateChar(int k, char* v, size_t len) {
    char *p = v;
    for (int i = 0; i < len; i++)
    {
        *p ^= k;
        p++;
    }
}

void ObfuscateCharv2(int k, char* v) {
    ObfuscateChar(k, v, strlen(v));
}

void kcDecodeFunc(const char* name)
{
    int successFlag = 1;
    unsigned int mySectionSize;
    unsigned int decodeRandSeed;
    unsigned int mySectionOffset;
    unsigned int nsize;
    unsigned long base;
    unsigned long text_addr;
    unsigned int i;


    //获取so的起始地址
    base = kcgetLibAddr(name);

#ifdef _64_BIT
    Elf64_Ehdr *ehdr64;
    unsigned long addNewSectionOffset64;
    ehdr64 = (Elf64_Ehdr *)base;

    //获取新加section的偏移值
    addNewSectionOffset64 = ehdr64->e_entry;

//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "addNewSectionOffset = %li", addNewSectionOffset64);
    //从内存读取加密section的offset和size
    mySectionOffset = *(unsigned int *)(base + addNewSectionOffset64);
    text_addr = mySectionOffset + base;

//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "mySectionOffset = 0x%x", mySectionOffset);

    mySectionSize = *(unsigned int *) (base + addNewSectionOffset64 + 4);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "mySectionSize = 0x%x", mySectionSize);


    decodeRandSeed = *(unsigned int *) (base + addNewSectionOffset64 + 8);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "decodeRandSeed = 0x%x", decodeRandSeed);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "addNewSectionVirtualOffset =  %li",  addNewSectionOffset64 + base);
#else
    Elf32_Ehdr *ehdr;
    unsigned int addNewSectionOffset;
    ehdr = (Elf32_Ehdr *)base;

    //获取新加section的偏移值
    addNewSectionOffset = ehdr->e_entry;

//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "addNewSectionOffset = 0x%x", addNewSectionOffset);

    //从内存读取加密section的offset和size
    mySectionOffset = *(unsigned int *)(base + addNewSectionOffset);
    text_addr = mySectionOffset + base;
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "mySectionOffset = 0x%x", mySectionOffset);

    mySectionSize = *(unsigned int *) (base + addNewSectionOffset + 4);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "mySectionSize = 0x%x", mySectionSize);


    decodeRandSeed = *(unsigned int *) (base + addNewSectionOffset + 8);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "decodeRandSeed = 0x%x", decodeRandSeed);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "addNewSectionVirtualOffset =  %li",  addNewSectionOffset + base);
#endif

    unsigned int decodeTag = decodeRandSeed % 9;


    nsize = mySectionSize/4096 + (mySectionSize%4096 == 0 ? 1 : 2);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "mySectionOffset = 0x%x, mySectionSize =  0x%x, nsize:%d", mySectionOffset, mySectionSize, nsize);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "text_started =  0x%lx", text_addr);
//    __android_log_print(ANDROID_LOG_ERROR, JNITAG, "text_ended =  0x%lx", text_addr + 4096 * nsize);
//    LOGP("mySectionSize = %d\n", mySectionSize);

    //修改内存的操作权限
    if(mprotect((void *) (text_addr / PAGE_SIZE * PAGE_SIZE), 4096 * nsize , PROT_READ | PROT_EXEC | PROT_WRITE) != 0){
//        LOGP("mem privilege change failed");
        __android_log_print(ANDROID_LOG_INFO, "JNITag", "mem privilege change failed");
        successFlag = 0;
    }
    //解密
    for(i = 0;i < mySectionSize; i++){
        if (decodeTag == 0 || i % decodeTag == 0)
        {
            char *addr = (char*)(text_addr + i);
            *addr = ~(*addr);
        }
    }

    if(mprotect((void *) (text_addr / PAGE_SIZE * PAGE_SIZE), 4096 * nsize, PROT_READ | PROT_EXEC) != 0){
//        LOGP("mem privilege change failed");
        __android_log_print(ANDROID_LOG_INFO, JNITAG, "The second mem privilege change failed");
        successFlag = 0;
    }
}

unsigned long kcgetLibAddr(const char* name){
    unsigned long ret = 0;
    char buf[4096], *temp;
    int pid;
    FILE *fp;
    pid = getpid();
    sprintf(buf, "/proc/%d/maps", pid);
    fp = fopen(buf, "r");
    if(fp == NULL)
    {
        goto _error;
    }
    while(fgets(buf, sizeof(buf), fp)){
        if(my_strstr(buf, name)){
            temp = strtok(buf, "-");
            ret = strtoul(temp, NULL, 16);
            break;
        }
    }
    _error:
    fclose(fp);
    return ret;
}


long fridaLastCheckTime = 0;
long fridaCurrCheckTime = 0;
int timeout = CHECK_TIMEOUT;
int portError = 0;
int dayTimes = 0;
int dayBadTimes = 0;

__attribute__((section (".kcniceway")))void *niceway_thread_loop() {
    while (JNI_TRUE) {
        loop_status();
        loop_namedpipe();
        loop_check();
        loop_mg();
        sleep(5);
    }
}

__attribute__((section (".kcniceway")))void *niceway_thread()
{
    while (JNI_TRUE)
    {
//        niceway_time();
        niceway_debuger();
        niceway_file();
        if (portError == 0)
        {
            niceway_port();
        }
        niceway_frida_name();
//        niceway_breakpoint();

//        if (fridaCurrCheckTime == 0 || fridaCurrCheckTime - fridaLastCheckTime >= 10)
//        {
//            niceway_frida_ablity();
//            fridaLastCheckTime = fridaCurrCheckTime;
//        }

        dayTimes++;
        sleep(timeout);
        fridaCurrCheckTime += timeout;
        timeout += 1;
        if (timeout > MAX_TIMEOUT)
        {
            timeout = MAX_TIMEOUT;
        }
        if (fridaCurrCheckTime > 900000)
        {
            fridaCurrCheckTime = 0;
        }
        if (dayTimes > 900000)
        {
            dayTimes = 1;
        }
    }
}


//breakpoint检测
//Arm：0x01，0x00，0x9f，0xef
//Thumb16：0x01，0xde
//Thumb32：0xf0，0xf7，0x00，0xa0
__attribute__((section (".kcniceway")))void niceway_breakpoint()
{
    unsigned long base = kcgetLibAddr(so_name);
    unsigned char abi_type = *(unsigned char *)(base + 4);
    size_t elfHeadSize;
    size_t elfPhHeadSize;
    unsigned long offset;
    unsigned short ret = 0;
    if (abi_type == 1)
    {
        // elf32
        Elf32_Ehdr* elfhdr = (Elf32_Ehdr*) base;
        elfHeadSize = sizeof(Elf32_Ehdr);
        elfPhHeadSize = sizeof(Elf32_Phdr);

        Elf32_Phdr* ph_t;
        for (int i = 0; i < elfhdr->e_phnum; i++) {
            ph_t = (Elf32_Phdr*)(base + elfhdr->e_phoff + i * elfPhHeadSize); // traverse program header

            if ( !(ph_t->p_flags & 1) ) continue;
            offset = base + ph_t->p_vaddr;
            offset += elfHeadSize + elfPhHeadSize * elfhdr->e_phnum;

            char *p = (char*)offset;
            for (int j = 0; j < ph_t->p_memsz; j++) {
                if(*p == 0x01 && *(p+1) == 0xde)
                {
                    ret = 1;
                    break;
                } else if (*p == 0xf0 && *(p+1) == 0xf7 && *(p+2) == 0x00 && *(p+3) == 0xa0) {
                    ret = 1;
                    break;
                } else if (*p == 0x01 && *(p+1) == 0x00 && *(p+2) == 0x9f && *(p+3) == 0xef) {
                    ret = 1;
                    break;
                }
                p++;
            }
        }

    }
    else if (abi_type == 2)
    {
        // elf64
        Elf64_Ehdr* elfhdr = (Elf64_Ehdr*) base;
        elfHeadSize = sizeof(Elf64_Ehdr);
        elfPhHeadSize = sizeof(Elf64_Phdr);

        Elf64_Phdr* ph_t;
        for (int i = 0; i < elfhdr->e_phnum; i++) {
            ph_t = (Elf64_Phdr*)(base + elfhdr->e_phoff + i * elfPhHeadSize); // traverse program header

            if ( !(ph_t->p_flags & 1) ) continue;
            offset = base + ph_t->p_vaddr;
            offset += elfHeadSize + elfPhHeadSize * elfhdr->e_phnum;

            char *p = (char*)offset;
            for (int j = 0; j < ph_t->p_memsz; j++) {
                if(*p == 0x01 && *(p+1) == 0xde) {
                    ret = 1;
                    break;
                } else if (*p == 0xf0 && *(p+1) == 0xf7 && *(p+2) == 0x00 && *(p+3) == 0xa0) {
                    ret = 1;
                    break;
                } else if (*p == 0x01 && *(p+1) == 0x00 && *(p+2) == 0x9f && *(p+3) == 0xef) {
                    ret = 1;
                    break;
                }
                p++;
            }
        }
    }

    if (ret == 1)
    {
        kcKill("0x01");
    }
}

//ida端口检测
__attribute__((section (".kcniceway")))void niceway_port()
{
    FILE *fd;
    char buf[4096];
    fd = fopen("/proc/net/tcp", "r");


    if (fd == NULL)
    {
        close(fd);
        LOGE("0x07");
        portError = 1;
        return;
    }

    char char_pt1[] = KCDEF_PORT1;
    ObfuscateChar(KCDEF_KEY, char_pt1, sizeof(char_pt1));
    char f_pt1[51];
    f_pt1[0] = '\0';
    strncat(f_pt1, char_pt1, sizeof(char_pt1));

    char char_pt2[] = KCDEF_PORT2;
    ObfuscateChar(KCDEF_KEY, char_pt2, sizeof(char_pt2));
    char f_pt2[51];
    f_pt2[0] = '\0';
    strncat(f_pt2, char_pt2, sizeof(char_pt2));

    char char_pt3[] = KCDEF_PORT3;
    ObfuscateChar(KCDEF_KEY, char_pt3, sizeof(char_pt3));
    char f_pt3[51];
    f_pt3[0] = '\0';
    strncat(f_pt3, char_pt3, sizeof(char_pt3));

    char* pt1 = f_pt1;
    char* pt2 = f_pt2;
    char* pt3 = f_pt3;
    while(fgets(buf, sizeof(buf), fd)){
        char* c1 = my_strstr(buf, pt1);
        char* c2 = my_strstr(buf, pt2);
        char* c3 = my_strstr(buf, pt3);
        if (c1 || c2 || c3)
        {
            kcKill("0x02");
            break;
        }
    }

    close(fd);
}

//jni debugconnected检测
__attribute__((section (".kcniceway")))void niceway_debuger()
{
    JNIEnv *env;
    if (jvm != NULL)
    {
        (*jvm)->AttachCurrentThread(jvm, &env, 0);


        char java_debugger[] = KCAPP_DEBUGGER_CONNECTED;
        ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_debugger);

        jclass debugCls = (*env)->FindClass(env, "android/os/Debug");
        jmethodID method = (*env)->GetStaticMethodID(env, debugCls, java_debugger,
                                                     "()Z");

        jboolean res = (*env)->CallStaticBooleanMethod(env, debugCls, method);
        if (res == JNI_TRUE)
        {
            kcKill("0x08");
        }

        (*jvm)->DetachCurrentThread(jvm);
    }
}

__attribute__((section (".kcniceway")))void kcKill(const char* reason)
{
    LOGE("%s", reason);
    dayBadTimes++;
    if (main_pid <= 0)
    {
        kill(getpid(), SIGKILL);
    }
}

//基于proc文件检测
__attribute__((section (".kcniceway")))void niceway_file()
{
    int pid = getpid();
    FILE *fd;
    char buf[4096];
    sprintf(buf, "/proc/%d/status", pid);

    fd = fopen(buf, "r");

    if (fd == NULL)
    {
        LOGE("0x09");
        return;
    }

    char char_name[] = KCDEF_PID;
    ObfuscateChar(KCDEF_KEY, char_name, sizeof(char_name));
    char path[51];
    path[0] = '\0';
    strncat(path, char_name, sizeof(char_name));

    char* tra = path;
    while(fgets(buf, sizeof(buf), fd)){
        char* c = my_strstr(buf, tra);
        if (c)
        {
            char* d = my_strstr(c,"\n");

            int length = d - c;
            char res[length - 11 + 1];
            strncpy(res, c + 11,length - 11);
            res[length - 11] = '\0';

            if (my_strcmp(res, "0") != 0)
            {
                kcKill("0x03");
            }
            break;
        }
    }

    close(fd);
}

__attribute__((section (".kcniceway")))void niceway_frida_name()
{
    char buf[4096];
    int pid;
    FILE *fp;
    pid = getpid();
    sprintf(buf, "/proc/%d/maps", pid);
    fp = fopen(buf, "r");

    if (fp == NULL)
    {
        LOGE("0x10");
        return;
    }

    char char_agent[] = KCDEF_F_AGENT;
    ObfuscateChar(KCDEF_KEY, char_agent, sizeof(char_agent));
    char agent[51];
    agent[0] = '\0';
    strncat(agent, char_agent, sizeof(char_agent));

    char char_server[] = KCDEF_F_SEREVER;
    ObfuscateChar(KCDEF_KEY, char_server, sizeof(char_server));
    char server[51];
    server[0] = '\0';
    strncat(server, char_server, sizeof(char_server));

    char char_flib[] = KCDEF_LIB_F;
    ObfuscateChar(KCDEF_KEY, char_flib, sizeof(char_flib));
    char flib[51];
    flib[0] = '\0';
    strncat(flib, char_flib, sizeof(char_flib));

    char char_ftrace[] = KCDEF_F_TRACE;
    ObfuscateChar(KCDEF_KEY, char_ftrace, sizeof(char_ftrace));
    char ftrace[51];
    ftrace[0] = '\0';
    strncat(ftrace, char_ftrace, sizeof(char_ftrace));

    while(fgets(buf, sizeof(buf), fp)){
        if(my_strstr(buf, agent) || my_strstr(buf, server) || my_strstr(buf, flib) || my_strstr(buf, ftrace)){
            kcKill("0x04");
            break;
        }
    }
    fclose(fp);
}


__attribute__((section (".kcniceway")))void niceway_entry()
{
    pthread_t id_0, id_1;
    id_0 = pthread_self();
    pid_t pid = getpid();

    ptrace(PTRACE_TRACEME, 0, 0, 0);

    //check sum first
    record_sum();

    id_0 = pthread_create(&id_0, NULL, niceway_thread, &pid);
    id_1 = pthread_create(&id_1, NULL, niceway_thread_loop, &pid);
}


int num_found;

__attribute__((section (".kcniceway")))__attribute__((always_inline))void niceway_frida_ablity()
{
    num_found = 0;

    char buf[4096];
    FILE *fp;
    int pid;
    pid = getpid();
    sprintf(buf, "/proc/%d/maps", pid);
    fp = fopen(buf, "r");


    if (fp == NULL)
    {
        LOGE("0x06");
        return;
    }

    while(fgets(buf, sizeof(buf), fp))
    {
        if (scan_executable_segments(buf) == 1) {
            num_found++;
        }

        if (num_found > 1) {
            kcKill("0x05");
            break;
        }
    }
}

__attribute__((section (".kcniceway")))__attribute__((always_inline))int scan_executable_segments(char * map) {
    char buf[512];
    unsigned long start, end;
    sscanf(map, "%lx-%lx %s", &start, &end, buf);

    char char_agent[] = KCDEF_F_AGENT2;
    ObfuscateChar(KCDEF_KEY, char_agent, sizeof(char_agent));
    char agent[51];
    agent[0] = '\0';
    strncat(agent, char_agent, sizeof(char_agent));
    if (buf[0] == 'r' && buf[2] == 'x') {
        return (find_mem_string(start, end, agent, 11, map) == 1);
    } else {
        return 0;
    }
}

__attribute__((section (".kcniceway")))__attribute__((always_inline))int find_mem_string(unsigned long start, unsigned long end, char *bytes, unsigned int len, char* maps) {

    char *pmem = (char*)start;
    int matched = 0;

    while ((unsigned long)pmem < (end - len)) {

        if(*pmem == bytes[0]) {

            matched = 1;
            char *p = pmem + 1;

            while (*p == bytes[matched] && (unsigned long)p < end) {
                matched ++;
                p ++;
            }

            if (matched >= len) {

                return 1;
            }
        }

        pmem++;

    }
    return 0;
}


__attribute__((section (".kcniceway")))__attribute__((always_inline))
jboolean loop_status()
{
    char c_proctask_char[] = PROC_TASK;
    ObfuscateCharv2(FA_KEY, c_proctask_char);
    DIR *dir = opendir(c_proctask_char);

    if (dir != NULL) {
        struct dirent *entry = NULL;
        while ((entry = readdir(dir)) != NULL) {
            char filePath[MAX_LENGTH] = "";

            if (0 == my_strcmp(entry->d_name, ".") || 0 == my_strcmp(entry->d_name, "..")) {
                continue;
            }
            char c_status_char[] = PROC_STATUS;
            ObfuscateCharv2(FA_KEY, c_status_char);

            snprintf(filePath, sizeof(filePath), c_status_char, entry->d_name);

            int fd = my_openat(AT_FDCWD, filePath, O_RDONLY | O_CLOEXEC, 0);
            if(fd != 0) {
                char buf[MAX_LENGTH] = "";
                read_one_line(fd, buf, MAX_LENGTH);
                char c_gumjsloop_char[] = FRIDA_THREAD_GUM_JS_LOOP;
                ObfuscateCharv2(FA_KEY, c_gumjsloop_char);


                char c_gmain_char[] = FRIDA_THREAD_GMAIN;
                ObfuscateCharv2(FA_KEY, c_gmain_char);
                if (my_strstr(buf, c_gumjsloop_char) || my_strstr(buf, c_gmain_char)) {
                    kcKill("0x0a");
                    return JNI_TRUE;
                }
                my_close(fd);
            }

        }
        closedir(dir);
    }
    return JNI_FALSE;
}

__attribute__((section (".kcniceway")))__attribute__((always_inline))
jboolean loop_namedpipe(){

    char c_procfd_char[] = PROC_FD;
    ObfuscateCharv2(FA_KEY, c_procfd_char);
    DIR *dir = opendir(c_procfd_char);
    if (dir != NULL) {
        struct dirent *entry = NULL;
        while ((entry = readdir(dir)) != NULL) {
            struct stat filestat;
            char buf[MAX_LENGTH] = "";
            char filePath[MAX_LENGTH] = "";
            snprintf(filePath, sizeof(filePath), "/proc/self/fd/%s", entry->d_name);

            lstat(filePath, &filestat);

            if((filestat.st_mode & S_IFMT) == S_IFLNK) {
                //TODO: Another way is to check if filepath belongs to a path not related to system or the app
                my_readlinkat(AT_FDCWD, filePath, buf, MAX_LENGTH);

                char c_linjector_char[] = FRIDA_NAMEDPIPE_LINJECTOR;
                ObfuscateCharv2(FA_KEY, c_linjector_char);
                if (NULL != my_strstr(buf, c_linjector_char)) {
                    kcKill("0x0b");
                    return JNI_TRUE;
                }
            }

        }
    }
    closedir(dir);
    return JNI_FALSE;
}

__attribute__((section (".kcniceway")))__attribute__((always_inline))
jboolean loop_mg(){
    char path_to_check[SU_PATH_CT][50] = SU_PATHS;
    char mount_blacklist[MOUNT_CT][50] = BLACK_LIST_MOUNT_PATHS;

    for (int i = 0; i < SU_PATH_CT; i++) {
        char suPath[50];
        strcpy(suPath, path_to_check[i]);
        ObfuscateCharv2(MG_KEY, suPath);
        if (my_openat(AT_FDCWD, suPath, O_RDONLY, 0) >= 0) {
            kcKill("0x0c");
            break;
        }
        if (0 == access(suPath, R_OK)) {
            kcKill("0x0c");
            break;
        }
    }

    int pid = getpid();
    char ch[100];
    memset(ch, '\0', 100 * sizeof(char));

    sprintf(ch, "/proc/%d/mounts", pid);

    FILE *fp = fopen(ch, "r");
    if (fp == NULL)
    {
        return JNI_FALSE;
    }

    fseek(fp, 0L, SEEK_END);
    long size = ftell(fp);
    /* For some reason size comes as zero */
    if (size == 0)
        size = 3000;  /*This will differ for different devices */
    char *buffer = malloc(size * sizeof(char));
    if (buffer == NULL)
    {
        if (fp != NULL)
            fclose(fp);
        return JNI_FALSE;
    }

    size_t read = fread(buffer, 1, size, fp);
    int count = 0;
    for (int i = 0; i < MOUNT_CT; i++) {
        char mountBlackPath[50];
        strcpy(mountBlackPath, mount_blacklist[i]);
        ObfuscateCharv2(MG_KEY, mountBlackPath);

        char *rem = my_strstr(buffer, mountBlackPath);
        if (rem != NULL) {
            count++;
            break;
        }
    }
    if (count > 0)
    {
        kcKill("0x0d");
        return JNI_TRUE;
    }

    if (buffer != NULL)
        free(buffer);
    if (fp != NULL)
        fclose(fp);

    return JNI_FALSE;
}