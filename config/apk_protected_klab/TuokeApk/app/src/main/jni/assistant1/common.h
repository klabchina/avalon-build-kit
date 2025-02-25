//
// Created by li-j on 2020-11-16.
//

#ifndef ANTI_DEBUG_COMMON_H
#define ANTI_DEBUG_COMMON_H

#include <android/log.h>
#include <sys/mman.h>
#include <jni.h>

#define JNITAG  "ASSISTANT1"
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR,JNITAG, __VA_ARGS__)
#define SO_NAME "libassistant1.so"


extern int global_abi_type;
#endif //ANTI_DEBUG_COMMON_H
