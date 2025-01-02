//
// Created by li-j on 2020-11-14.
//

#ifndef TUOKEAPK_INTERNAL_DEFINES_H
#define TUOKEAPK_INTERNAL_DEFINES_H

#define KCDEF_KEY 88
#define KCDEF_PID {12, 42, 57, 59, 61, 42, 8, 49, 60}
#define KCDEF_F_AGENT {62, 42, 49, 60, 57, 117, 57, 63, 61, 54, 44}
#define KCDEF_F_SEREVER {62, 42, 49, 60, 57, 118, 43, 61, 42, 46, 61, 42}
#define KCDEF_PORT1 {98, 109, 28, 96, 25}
#define KCDEF_PORT2 {98, 106, 107, 97, 108, 110}
#define KCDEF_PORT3 {98, 110, 97, 25, 106}
#define KCDEF_F_AGENT2 {30, 10, 17, 28, 25, 7, 25, 31, 29, 22, 12}

#define KCDEF_DKEY 234575454
#define KCDEF_DSTEP 6

//2020.12.29
#define KCAPP_CLASS_KEY 61
#define KCAPP_JNIREG_CLASS {82, 79, 90, 18, 85, 92, 94, 86, 94, 82, 89, 88, 18, 109, 79, 82, 69, 68, 124, 77, 77, 81, 84, 94, 92, 73, 84, 82, 83, '\0'}

#define KCAPP_TARGET_KEY 60
#define KCAPP_TARGET {19, 104, 93, 78, 91, 89, 72, 125, 76, 87, 18, 70, 85, 76, '\0'}


#define KCAPP_JAVACLASS_KEY 49
#define KCAPP_JAVA_LOADER {85, 80, 93, 71, 88, 90, 30, 66, 72, 66, 69, 84, 92, 30, 117, 84, 73, 114, 93, 80, 66, 66, 125, 94, 80, 85, 84, 67, '\0'}
#define KCAPP_JAVA_REFLECT {94, 67, 86, 30, 89, 80, 82, 90, 82, 94, 85, 84, 30, 99, 84, 87, 93, 84, 82, 69, 100, 69, 88, 93, 66, '\0'}
#define KCAPP_JAVA_LOADAPK {80, 95, 85, 67, 94, 88, 85, 31, 80, 65, 65, 31, 125, 94, 80, 85, 84, 85, 112, 65, 90, '\0'}
#define KCAPP_JAVA_MCLASS {92, 114, 93, 80, 66, 66, 125, 94, 80, 85, 84, 67, '\0'}
#define KCAPP_JAVA_INIT {13, 88, 95, 88, 69, 15, '\0'}
#define KCAPP_JAVA_SETOBJECT {66, 84, 69, 119, 88, 84, 93, 85, 126, 83, 91, 84, 82, 69, '\0'}
#define KCAPP_JAVA_DEXNAME  {82, 93, 80, 66, 66, 84, 66, 31, 85, 84, 73, '\0'}
#define KCAPP_JAVA_CONTENTWRAP {80, 95, 85, 67, 94, 88, 85, 30, 82, 94, 95, 69, 84, 95, 69, 30, 114, 94, 95, 69, 84, 73, 69, 102, 67, 80, 65, 65, 84, 67, '\0'}
#define KCAPP_JAVA_GETDIR {86, 84, 69, 117, 88, 67, '\0'}
#define KCAPP_JAVA_ASSET {80, 66, 66, 84, 69, 66, '\0'}
#define KCAPP_JAVA_CONTENT {80, 95, 85, 67, 94, 88, 85, 30, 82, 94, 95, 69, 84, 95, 69, 30, 114, 94, 95, 69, 84, 73, 69, '\0'}
#define KCAPP_JAVA_PVMODE {124, 126, 117, 116, 110, 97, 99, 120, 103, 112, 101, 116, '\0'}

#define KCAPP_JAVA_GETAPPINFO {86, 84, 69, 112, 65, 65, 93, 88, 82, 80, 69, 88, 94, 95, 120, 95, 87, 94, '\0'}
#define KCAPP_JAVA_GETAPPINFO_SIG {25, 24, 125, 80, 95, 85, 67, 94, 88, 85, 30, 82, 94, 95, 69, 84, 95, 69, 30, 65, 92, 30, 112, 65, 65, 93, 88, 82, 80, 69, 88, 94, 95, 120, 95, 87, 94, 10, '\0'}
#define KCAPP_JAVA_SOURCEDIR {66, 94, 68, 67, 82, 84, 117, 88, 67, '\0'}

//java/io/ByteArrayInputStream
#define KCAPP_JAVA_BYARRIS {91, 80, 71, 80, 30, 88, 94, 30, 115, 72, 69, 84, 112, 67, 67, 80, 72, 120, 95, 65, 68, 69, 98, 69, 67, 84, 80, 92, '\0'}
//java/io/DataInputStream
#define KCAPP_JAVA_DATAIS {91, 80, 71, 80, 30, 88, 94, 30, 117, 80, 69, 80, 120, 95, 65, 68, 69, 98, 69, 67, 84, 80, 92, '\0'}
//java/io/FileOutputStream
#define KCAPP_JAVA_FOS {91, 80, 71, 80, 30, 88, 94, 30, 119, 88, 93, 84, 126, 68, 69, 65, 68, 69, 98, 69, 67, 84, 80, 92, '\0'}
//java/io/ByteArrayOutputStream
#define KCAPP_JAVA_BYARROUT {91, 80, 71, 80, 30, 88, 94, 30, 115, 72, 69, 84, 112, 67, 67, 80, 72, 126, 68, 69, 65, 68, 69, 98, 69, 67, 84, 80, 92, '\0'}
//java/io/FileInputStream
#define KCAPP_JAVA_FIS {91, 80, 71, 80, 30, 88, 94, 30, 119, 88, 93, 84, 120, 95, 65, 68, 69, 98, 69, 67, 84, 80, 92, '\0'}
//java/io/BufferedInputStream
#define KCAPP_JAVA_BIS {91, 80, 71, 80, 30, 88, 94, 30, 115, 68, 87, 87, 84, 67, 84, 85, 120, 95, 65, 68, 69, 98, 69, 67, 84, 80, 92, '\0'}
//java/util/zip/ZipInputStream
#define KCAPP_JAVA_ZIS {91, 80, 71, 80, 30, 68, 69, 88, 93, 30, 75, 88, 65, 30, 107, 88, 65, 120, 95, 65, 68, 69, 98, 69, 67, 84, 80, 92, '\0'}
//java/util/zip/ZipEntry
#define KCAPP_JAVA_ZIPE {91, 80, 71, 80, 30, 68, 69, 88, 93, 30, 75, 88, 65, 30, 107, 88, 65, 116, 95, 69, 67, 72, '\0'}
//(Ljava/io/InputStream;)V
#define KCAPP_JAVA_IS_SIG {25, 125, 91, 80, 71, 80, 30, 88, 94, 30, 120, 95, 65, 68, 69, 98, 69, 67, 84, 80, 92, 10, 24, 103, '\0'}
//()Ljava/util/zip/ZipEntry;
#define KCAPP_JAVA_ZIS_GNE_SIG {25, 24, 125, 91, 80, 71, 80, 30, 68, 69, 88, 93, 30, 75, 88, 65, 30, 107, 88, 65, 116, 95, 69, 67, 72, 10, '\0'}
//getNextEntry
#define KCAPP_JAVA_ZIS_GNE {86, 84, 69, 127, 84, 73, 69, 116, 95, 69, 67, 72, '\0'}
//isDebuggerConnected
#define KCAPP_DEBUGGER_CONNECTED {88, 66, 117, 84, 83, 68, 86, 86, 84, 67, 114, 94, 95, 95, 84, 82, 69, 84, 85, '\0'}

#define FA_KEY 41
#define PROC_STATUS {6, 89, 91, 70, 74, 6, 90, 76, 69, 79, 6, 93, 72, 90, 66, 6, 12, 90, 6, 90, 93, 72, 93, 92, 90, '\0'}
#define PROC_FD {6, 89, 91, 70, 74, 6, 90, 76, 69, 79, 6, 79, 77, '\0'}
#define PROC_TASK {6, 89, 91, 70, 74, 6, 90, 76, 69, 79, 6, 93, 72, 90, 66, '\0'}
#define FRIDA_THREAD_GUM_JS_LOOP {78, 92, 68, 4, 67, 90, 4, 69, 70, 70, 89, '\0'}
#define FRIDA_THREAD_GMAIN {78, 68, 72, 64, 71, '\0'}
#define FRIDA_NAMEDPIPE_LINJECTOR {69, 64, 71, 67, 76, 74, 93, 70, 91, '\0'}


#define MG_KEY 35
#define SU_PATH_CT 14
#define SU_PATHS {{12, 71, 66, 87, 66, 12, 79, 76, 64, 66, 79, 12, 80, 86, '\0'},{12, 71, 66, 87, 66, 12, 79, 76, 64, 66, 79, 12, 65, 74, 77, 12, 80, 86, '\0'},{12, 71, 66, 87, 66, 12, 79, 76, 64, 66, 79, 12, 91, 65, 74, 77, 12, 80, 86, '\0'},{12, 80, 65, 74, 77, 12, 80, 86, '\0'},{12, 80, 86, 12, 65, 74, 77, 12, 80, 86, '\0'},{12, 80, 90, 80, 87, 70, 78, 12, 65, 74, 77, 12, 80, 86,'\0'},{12, 80, 90, 80, 87, 70, 78, 12, 65, 74, 77, 12, 13, 70, 91, 87, 12, 80, 86,'\0'},{12, 80, 90, 80, 87, 70, 78, 12, 65, 74, 77, 12, 69, 66, 74, 79, 80, 66, 69, 70, 12, 80, 86,'\0'},{12, 80, 90, 80, 87, 70, 78, 12, 80, 71, 12, 91, 65, 74, 77, 12, 80, 86,'\0'},{12, 80, 90, 80, 87, 70, 78, 12, 86, 80, 81, 12, 84, 70, 14, 77, 70, 70, 71, 14, 81, 76, 76, 87, 12, 80, 86,'\0'}, {12, 80, 90, 80, 87, 70, 78, 12, 91, 65, 74, 77, 12, 80, 86,'\0'},{12, 64, 66, 64, 75, 70, 12, 80, 86,'\0'},{12, 71, 66, 87, 66, 12, 80, 86,'\0'},{12, 71, 70, 85, 12, 80, 86,'\0'}}
#define MOUNT_CT 4
#define BLACK_LIST_MOUNT_PATHS {{12, 80, 65, 74, 77, 12, 13, 78, 66, 68, 74, 80, 72, 12,'\0'},{12, 80, 65, 74, 77, 12, 13, 64, 76, 81, 70, 12, 78, 74, 81, 81, 76, 81,'\0'},{12, 80, 65, 74, 77, 12, 13, 64, 76, 81, 70, 12, 74, 78, 68,'\0'},{12, 80, 65, 74, 77, 12, 13, 64, 76, 81, 70, 12, 71, 65, 14, 19, 12, 78, 66, 68, 74, 80, 72, 13, 71, 65,'\0'}}


#endif //TUOKEAPK_INTERNAL_DEFINES_H



//static const char *suPaths[] = {
//        "/data/local/su",
//        "/data/local/bin/su",
//        "/data/local/xbin/su",
//        "/sbin/su",
//        "/su/bin/su",
//        "/system/bin/su",
//        "/system/bin/.ext/su",
//        "/system/bin/failsafe/su",
//        "/system/sd/xbin/su",
//        "/system/usr/we-need-root/su",
//        "/system/xbin/su",
//        "/cache/su",
//        "/data/su",
//        "/dev/su"
//};
//
//static char *blacklistedMountPaths[] = {
//        "/sbin/.magisk/",
//        "/sbin/.core/mirror",
//        "/sbin/.core/img",
//        "/sbin/.core/db-0/magisk.db"
//};

//static const char* PROC_STATUS = "/proc/self/task/%s/status";
//static const char* PROC_FD = "/proc/self/fd";
//static const char* PROC_TASK = "/proc/self/task";
//
//static const char* FRIDA_THREAD_GUM_JS_LOOP = "gum-js-loop";
//static const char* FRIDA_THREAD_GMAIN = "gmain";
//static const char* FRIDA_NAMEDPIPE_LINJECTOR = "linjector";