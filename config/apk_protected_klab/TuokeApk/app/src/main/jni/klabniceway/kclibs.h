//
// Created by li-j on 2020-08-26.
//

#include <android/log.h>
#include <sys/mman.h>
#include <jni.h>

#define JNITAG  "JNI_TAG"
#define JNI_PROGRESS  "JNI_PROGRESS"
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR,JNITAG, __VA_ARGS__)
#define LOGP(...) __android_log_print(ANDROID_LOG_ERROR,JNI_PROGRESS, __VA_ARGS__)
#define CHECK_TIMEOUT 3
#define MAX_TIMEOUT 100
#define ANDROID_10 29

void ObfuscateChar(int k, char* v, size_t len);
void ObfuscateCharv2(int k, char* v);
unsigned long kcgetLibAddr(const char* name);
void kcDecodeFunc(const char* name);


void niceway_entry();
void niceway_debuger();
void niceway_file();
void niceway_port();
void niceway_breakpoint();
void niceway_frida_name();
void niceway_frida_ablity();
void kcKill(const char* reason);

jboolean loop_status();
jboolean loop_namedpipe();
jboolean loop_mg();


extern JavaVM* jvm;
extern const char* so_name;
extern int global_api_level;
extern int main_pid;