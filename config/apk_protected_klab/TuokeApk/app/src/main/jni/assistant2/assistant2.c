//
// Created by li-j on 2020-11-16.
//

#include <jni.h>
#include <android/log.h>
#include "common.h"
#include "checksum.h"
#include <pthread.h>


__attribute__((section (".kcniceway")))void *check_thread()
{
    while (JNI_TRUE)
    {
        loop_check();
        sleep(10);
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
        if(strstr(buf, name)){
            temp = strtok(buf, "-");
            ret = strtoul(temp, NULL, 16);
            break;
        }
    }
    _error:
    fclose(fp);
    return ret;
}


void start_assistant()
{

    unsigned long base = kcgetLibAddr(SO_NAME);
    unsigned char abi_type = *(unsigned char *)(base + 4);

    global_abi_type = abi_type == 1 ? 32 : 64;

    pthread_t id_0;

    pid_t pid = getpid();
    //check sum first
    record_sum();

    id_0 = pthread_create(&id_0, NULL, check_thread, &pid);
}


JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM*vm, void* reserved)
{
    JNIEnv* env = NULL;
    jint result = -1;


    if( (*vm)->GetEnv(vm, (void**)&env, JNI_VERSION_1_4) != JNI_OK)
        return -1;

    if(env == NULL)
        return -1;


    result = JNI_VERSION_1_4;

    start_assistant();

    // __android_log_print(ANDROID_LOG_INFO, "JNITag", "pid = %d\n", getpid());
    return result;

}

JNIEXPORT void JNICALL JNI_OnUnload(JavaVM *vm, void *reserved){

}