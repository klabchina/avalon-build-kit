#include <jni.h>
#include <android/log.h>
#include <stdio.h>
#include <stdlib.h>
#include <elf.h>
#include <sys/mman.h>
#include <sys/system_properties.h>
#include <string.h>
#include <unistd.h>
#include <math.h>
#include "kclibs.h"
#include "internal_defines.h"
#include "mylibc.h"

#include <asm/unistd.h>

#define LOG_TAG "KC-JIAGU"
#define LOGI(...)  __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
JavaVM* jvm;
const char* so_name;
int global_api_level;
int main_pid;

void init_func() __attribute__((constructor (2)));
void init_func(){
    kcDecodeFunc("libklabniceway.so");
}


__attribute__((section (".kcniceway")))jbyteArray readNiceWay_03(JNIEnv *env, jbyteArray srcdata){

	jbyte* byteArray = (*env)->GetByteArrayElements(env, srcdata, JNI_FALSE);
	jsize len = (*env)->GetArrayLength(env, srcdata);

    LOGI("bytes total length is %d", len);

    jbyte* buffer = (jbyte*)malloc(len * sizeof(jbyte));
    if (!buffer) {
        LOGE("Memory allocation failed");
        return NULL;
    }


	jsize i;

	for (i = 0; i < len / 2; i++) {
		jbyte temp = byteArray[i];
		buffer[i] = byteArray[len - 1 - i];
		buffer[len - 1 - i] = temp;
	}
	if (len % 2 == 1)
	{
		int center = (int)ceil(len / 2);
		buffer[center] = byteArray[center];
	}

	for(i = 0; i < len; i++){
		int oKey = (KCDEF_DKEY >> (i % KCDEF_DSTEP)) & 0xFF;
		buffer[i] = ~(buffer[i] ^ oKey);
	}

    LOGI("======== DecodeArray Create End  ==========");
    jbyteArray decodedArray = (*env)->NewByteArray(env, len);
    (*env)->ReleaseByteArrayElements(env, srcdata, byteArray, 0);
	(*env)->SetByteArrayRegion(env, decodedArray, 0, len, buffer);

    free(buffer);

	return decodedArray;
}


__attribute__((section (".kcniceway")))jbyteArray readNiceWay_01(JNIEnv *env, jobject obj){
	LOGI("===============readClassesDexFromApk start===============");
	//////////////////ByteArrayOutputStream dexByteArrayOutputStream = new ByteArrayOutputStream();
	//classes.dex
	char java_dex[] = KCAPP_JAVA_DEXNAME;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_dex);

	char java_init[] = KCAPP_JAVA_INIT;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_init);
	//getApplicationInfo
	char java_getappinfo[] = KCAPP_JAVA_GETAPPINFO;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_getappinfo);
	//()Landroid/content/pm/ApplicationInfo;
	char java_getappinfo_sgi[] = KCAPP_JAVA_GETAPPINFO_SIG;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_getappinfo_sgi);

	char java_sourcedir[] = KCAPP_JAVA_SOURCEDIR;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_sourcedir);
	char java_barrofs[] = KCAPP_JAVA_BYARROUT;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_barrofs);
	char java_fis[] = KCAPP_JAVA_FIS;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_fis);
	char java_bis[] = KCAPP_JAVA_BIS;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_bis);
	char java_zis[] = KCAPP_JAVA_ZIS;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_zis);
	char java_zipe[] = KCAPP_JAVA_ZIPE;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_zipe);
	char java_is_sig[] = KCAPP_JAVA_IS_SIG;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_is_sig);
	char java_zis_gne[] = KCAPP_JAVA_ZIS_GNE;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_zis_gne);
	char java_zis_gne_sig[] = KCAPP_JAVA_ZIS_GNE_SIG;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_zis_gne_sig);


	jclass byteArrayOutputStreamClass = (*env)->FindClass(env, java_barrofs);
	jmethodID byteArrayOutputStreamMethodID = (*env)->GetMethodID(env, byteArrayOutputStreamClass, java_init, "()V");
	jmethodID writeMethodID = (*env)->GetMethodID(env, byteArrayOutputStreamClass, "write", "([BII)V"); //ByteArrayOutputStream.write(byte[] buffer, int offset, int len)
	jmethodID toByteArrayMethodID = (*env)->GetMethodID(env, byteArrayOutputStreamClass, "toByteArray", "()[B"); //ByteArrayOutputStream.toByteArray()
	jobject byteArrayOutputStreamObj = (*env)->NewObject(env, byteArrayOutputStreamClass, byteArrayOutputStreamMethodID);

	//////////////////ZipInputStream localZipInputStream = new ZipInputStream(new BufferedInputStream(new FileInputStream( this.getApplicationInfo().sourceDir)));
	jclass applicationClass = (*env)->GetObjectClass(env, obj);
	jmethodID getApplicationInfoMethodID = (*env)->GetMethodID(env, applicationClass, java_getappinfo, java_getappinfo_sgi);
	jobject applicationInfoObj = (*env)->CallObjectMethod(env, obj, getApplicationInfoMethodID); //获取ApplicationInfo对象

	jclass applicationInfoClass =(*env)->GetObjectClass(env, applicationInfoObj);
	jfieldID sourceDirFieldID = (*env)->GetFieldID(env, applicationInfoClass, java_sourcedir, "Ljava/lang/String;");
	jstring sourceDirString = (jstring)(*env)->GetObjectField(env, applicationInfoObj, sourceDirFieldID);
	const char* str = (*env)->GetStringUTFChars(env, sourceDirString, 0);

	jclass fileInputStreamClass = (*env)->FindClass(env, java_fis);
	jmethodID fileInputStreamMethodID = (*env)->GetMethodID(env, fileInputStreamClass, java_init, "(Ljava/lang/String;)V");
	jobject fileInputStreamObj = (*env)->NewObject(env, fileInputStreamClass, fileInputStreamMethodID, sourceDirString);

	jclass bufferedInputStreamClass = (*env)->FindClass(env, java_bis);
	jmethodID bufferedInputStreamMethodId = (*env)->GetMethodID(env, bufferedInputStreamClass, java_init, java_is_sig);
	jobject bufferedInputStreamObj = (*env)->NewObject(env, bufferedInputStreamClass, bufferedInputStreamMethodId, fileInputStreamObj);

	jclass zipInputStreamClass = (*env)->FindClass(env, java_zis);
	jmethodID zipInputStreamMethodID = (*env)->GetMethodID(env, zipInputStreamClass, java_init, java_is_sig);
	jobject zipInputStreamObj = (*env)->NewObject(env, zipInputStreamClass, zipInputStreamMethodID, bufferedInputStreamObj);

	jmethodID closeMethodID = (*env)->GetMethodID(env, zipInputStreamClass, "close", "()V"); //InputStream.close()
	jmethodID readMethodID = (*env)->GetMethodID(env, zipInputStreamClass, "read", "([B)I"); //InputStream.read(byte[] buffer)
	jmethodID getNextEntryMethodID = (*env)->GetMethodID(env, zipInputStreamClass, java_zis_gne, java_zis_gne_sig);//ZipInputStream.getNextEntry()
	jmethodID closeEntryMethodID = (*env)->GetMethodID(env, zipInputStreamClass, "closeEntry", "()V");//ZipInputStream.closeEntry()

	jclass zipEntryClass = (*env)->FindClass(env, java_zipe);
	jmethodID getNameMethodID = (*env)->GetMethodID(env, zipEntryClass, "getName", "()Ljava/lang/String;");
	while(1){
		jobject zipEntryObj = (*env)->CallObjectMethod(env, zipInputStreamObj, getNextEntryMethodID);

		if(zipEntryObj == NULL){
			(*env)->CallVoidMethod(env, zipInputStreamObj, closeMethodID);
			break;
		}

		jstring entryName = (jstring)(*env)->CallObjectMethod(env, zipEntryObj, getNameMethodID);
		const char* entryNameStr = (*env)->GetStringUTFChars(env, entryName, 0);
		if(my_strcmp(entryNameStr, java_dex) == 0){
			LOGI("Find classes.dex!!!!!!!!!");
			jbyteArray buffer = (*env)->NewByteArray(env, 1024);
			while(1){
				int ret = (*env)->CallIntMethod(env, zipInputStreamObj, readMethodID, buffer);
				if(-1 == ret){
					break;
				}
				(*env)->CallVoidMethod(env, byteArrayOutputStreamObj, writeMethodID, buffer, 0, ret);
			}
			(*env)->ReleaseStringUTFChars(env, entryName, entryNameStr);
			(*env)->CallVoidMethod(env, zipInputStreamObj, closeEntryMethodID);
			break;
		}
		(*env)->ReleaseStringUTFChars(env, entryName, entryNameStr);
		(*env)->DeleteLocalRef(env, entryName); //GetStringUTFChars需要ReleaseStringUTFChars，DeleteLocalRef释放局部引用计数
		(*env)->DeleteLocalRef(env, zipEntryObj);
		(*env)->CallVoidMethod(env, zipInputStreamObj, closeEntryMethodID);
	}
	(*env)->CallVoidMethod(env, zipInputStreamObj, closeMethodID);
	(*env)->ReleaseStringUTFChars(env, sourceDirString, str);

	jbyteArray retArray = (jbyteArray)(*env)->CallObjectMethod(env, byteArrayOutputStreamObj, toByteArrayMethodID);
	//LOGI("===============readClassesDexFromApk end===============");

	return retArray;
}


__attribute__((section (".kcniceway")))void readNiceWay_02(JNIEnv *env, jobject obj, jbyteArray classesDexData, jstring targetFilename){

	LOGI("===============extractTargetZipFileFromDex start===============");

	char java_init[] = KCAPP_JAVA_INIT;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_init);

	char java_bistream[] = KCAPP_JAVA_BYARRIS;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_bistream);
	char java_distream[] = KCAPP_JAVA_DATAIS;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_distream);
	char java_fos[] = KCAPP_JAVA_FOS;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_fos);
	char java_is_sig[] = KCAPP_JAVA_IS_SIG;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_is_sig);

	jsize dexLen = (*env)->GetArrayLength(env, classesDexData);
	jbyteArray targetZipLenArray = (*env)->NewByteArray(env, 4);

	jclass systemClass = (*env)->FindClass(env, "java/lang/System");
	jmethodID arrayCopyMethodID = (*env)->GetStaticMethodID(env, systemClass, "arraycopy", "(Ljava/lang/Object;ILjava/lang/Object;II)V");//arraycopy(Object src, int srcPos, Object dst, int dstPos, int length)
	(*env)->CallStaticVoidMethod(env, systemClass, arrayCopyMethodID, classesDexData, dexLen-4, targetZipLenArray, 0, 4);

	jclass baisClass = (*env)->FindClass(env, java_bistream);
	jmethodID baisMethodID = (*env)->GetMethodID(env, baisClass, java_init, "([B)V"); //ByteArrayInputStream(byte[] buf)
	jobject baisObj = (*env)->NewObject(env, baisClass, baisMethodID, targetZipLenArray);

	jclass dataInputStreamClass = (*env)->FindClass(env, java_distream);
	jmethodID dataInputStreamMethodID = (*env)->GetMethodID(env, dataInputStreamClass, java_init, java_is_sig);
	jmethodID readIntMethodID = (*env)->GetMethodID(env, dataInputStreamClass, "readInt", "()I");
	jobject dataInputStreamObj =(*env)->NewObject(env, dataInputStreamClass, dataInputStreamMethodID, baisObj);

	int targetZipLen = (*env)->CallIntMethod(env, dataInputStreamObj, readIntMethodID);

	jbyteArray targetZipData = (*env)->NewByteArray(env, targetZipLen);
	(*env)->CallStaticVoidMethod(env, systemClass, arrayCopyMethodID, classesDexData, dexLen-targetZipLen-4, targetZipData, 0, targetZipLen);
    (*env)->DeleteLocalRef(env, classesDexData);

	//解密
	jbyteArray decodedTargetZipData = readNiceWay_03(env, targetZipData);

    LOGI("===============Descrypt  end===============");

	jclass fileClass = (*env)->FindClass(env, "java/io/File");
	jmethodID fileMethodID = (*env)->GetMethodID(env, fileClass, java_init, "(Ljava/lang/String;)V");
	jobject fileObj = (*env)->NewObject(env, fileClass, fileMethodID, targetFilename);

	//保存解密后的文件
	jclass fileOutputStreamClass = (*env)->FindClass(env, java_fos);
	jmethodID fileOutputStreamMethodID = (*env)->GetMethodID(env, fileOutputStreamClass, java_init, "(Ljava/io/File;)V");
	jmethodID fos_write_methodID =(*env)->GetMethodID(env, fileOutputStreamClass, "write", "([B)V");
	jmethodID fos_flush_methodID =(*env)->GetMethodID(env, fileOutputStreamClass, "flush", "()V");
	jmethodID fos_close_methodID =(*env)->GetMethodID(env, fileOutputStreamClass, "close", "()V");

	jobject fileOutputStreamObj = (*env)->NewObject(env, fileOutputStreamClass, fileOutputStreamMethodID, fileObj);
	(*env)->CallVoidMethod(env, fileOutputStreamObj, fos_write_methodID, decodedTargetZipData);
	(*env)->CallVoidMethod(env, fileOutputStreamObj, fos_flush_methodID);
	(*env)->CallVoidMethod(env, fileOutputStreamObj, fos_close_methodID);

	//LOGI("===============extractTargetZipFileFromDex start end===============");

}


extern int dayTimes;
extern int dayBadTimes;

__attribute__((section (".kcniceway")))void run(JNIEnv *env, jobject obj, jstring dexPath, jstring optimizedDirectory, jstring libraryPath, jobject parent, jobject loadedApk){

	while (dayTimes < 1)
	{
        usleep(100000);
	}
	if (dayBadTimes > 0)
    {
	    return;
    }

	char java_loader[] = KCAPP_JAVA_LOADER;
	//dalvik/system/DexClassLoader
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_loader);
	char java_reflec[] = KCAPP_JAVA_REFLECT;
	//org/hackcode/ReflectUtils
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_reflec);
	char java_loade_apk[] = KCAPP_JAVA_LOADAPK;
	//android.app.LoadedApk
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_loade_apk);
	char java_mclass[] = KCAPP_JAVA_MCLASS;
	//android.app.LoadedApk
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_mclass);
	char java_init[] = KCAPP_JAVA_INIT;
	//<init>
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_init);
	//setFieldObject
	char java_setobject[] = KCAPP_JAVA_SETOBJECT;
	//<init>
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_setobject);

    LOGI("load dex path %s", (*env)->GetStringUTFChars(env, dexPath, NULL));

	jclass dexClassLoaderClass =(*env)->FindClass(env, java_loader);
	jmethodID dexClassLoaderMethodID = (*env)->GetMethodID(env, dexClassLoaderClass, java_init,"(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/ClassLoader;)V");
	jobject dlLoaderObj = (*env)->NewObject(env, dexClassLoaderClass, dexClassLoaderMethodID, dexPath, optimizedDirectory, libraryPath, parent);

	jclass reflectUtilsClass = (*env)->FindClass(env, java_reflec);
	jmethodID setFieldObjectMethodId = (*env)->GetStaticMethodID(env, reflectUtilsClass, java_setobject, "(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;)V");

	jstring para1 = (*env)->NewStringUTF(env, java_loade_apk);
	jstring para2 = (*env)->NewStringUTF(env, java_mclass);
	(*env)->CallStaticVoidMethod(env, reflectUtilsClass, setFieldObjectMethodId, para1, para2, loadedApk, dlLoaderObj);
}

__attribute__((section (".kcniceway")))jstring get_target
    (JNIEnv *env, jobject obj, jobject application){
    char target[] = KCAPP_TARGET;
    ObfuscateCharv2(KCAPP_TARGET_KEY, target);
    //android/content/ContextWrapper
    char contentWrap[] = KCAPP_JAVA_CONTENTWRAP;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, contentWrap);
    //getDir
    char java_getdir[] = KCAPP_JAVA_GETDIR;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_getdir);
    //assets
    char java_asset[] = KCAPP_JAVA_ASSET;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_asset);
    //android/content/Context
    char java_content[] = KCAPP_JAVA_CONTENT;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_content);
    //MODE_PRIVATE
    char java_private_mode[] = KCAPP_JAVA_PVMODE;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_private_mode);
    char java_init[] = KCAPP_JAVA_INIT;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_init);

    /////////File odex = this.getDir("assets", MODE_PRIVATE);
    jclass contextWrapperClass = (*env)->FindClass(env, contentWrap);
    jmethodID getDirMethodID = (*env)->GetMethodID(env, contextWrapperClass, "getCodeCacheDir", "()Ljava/io/File;");
    jstring path_name = (*env)->NewStringUTF(env, "code_cache");

    jclass contextClass = (*env)->FindClass(env, java_content);
    jfieldID fid = (*env)->GetStaticFieldID(env, contextClass, java_private_mode, "I");
    jint i = (*env)->GetStaticIntField(env, contextClass, fid);
    jobject fileObj = (*env)->CallObjectMethod(env, application, getDirMethodID, path_name, i);

    ////////String odexPath = odex.getAbsolutePath();
    jclass fileClass = (*env)->FindClass(env, "java/io/File");
    jmethodID getAbsolutePath_methodID = (*env)->GetMethodID(env, fileClass, "getAbsolutePath", "()Ljava/lang/String;");
    jstring odexPath = (jstring)(*env)->CallObjectMethod(env, fileObj, getAbsolutePath_methodID);
    LOGI("odexPath  name %s", (*env)->GetStringUTFChars(env, odexPath, NULL));

    ///////String targetFilename = odexPath + "/TargetApk.zip";
    jclass StringBufferClass = (*env)->FindClass(env, "java/lang/StringBuffer");
    jmethodID initStringBufferMethod =(*env)->GetMethodID(env, StringBufferClass, java_init,"()V");
    jobject stringBufferObj = (*env)->NewObject(env, StringBufferClass,initStringBufferMethod);
    jmethodID append_methodID =(*env)->GetMethodID(env, StringBufferClass, "append","(Ljava/lang/String;)Ljava/lang/StringBuffer;");

    (*env)->CallObjectMethod(env, stringBufferObj, append_methodID, odexPath);
    jstring zip_str = (*env)->NewStringUTF(env, target);
    (*env)->CallObjectMethod(env, stringBufferObj, append_methodID, zip_str);

    jmethodID toString_methodID = (*env)->GetMethodID(env, StringBufferClass, "toString","()Ljava/lang/String;");
    jstring targetFilename = (jstring)(*env)->CallObjectMethod(env, stringBufferObj, toString_methodID);

    LOGI("target save name %s", (*env)->GetStringUTFChars(env, targetFilename, NULL) );

    return targetFilename;
}

__attribute__((section (".kcniceway")))void native_start
  (JNIEnv *env, jobject obj, jobject application, jstring libraryPath, jobject parent, jobject loadedApk){

	char target[] = KCAPP_TARGET;
	ObfuscateCharv2(KCAPP_TARGET_KEY, target);
	//android/content/ContextWrapper
	char contentWrap[] = KCAPP_JAVA_CONTENTWRAP;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, contentWrap);
	//getDir
	char java_getdir[] = KCAPP_JAVA_GETDIR;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_getdir);
	//assets
	char java_asset[] = KCAPP_JAVA_ASSET;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_asset);
	//android/content/Context
	char java_content[] = KCAPP_JAVA_CONTENT;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_content);
	//MODE_PRIVATE
	char java_private_mode[] = KCAPP_JAVA_PVMODE;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_private_mode);
	char java_init[] = KCAPP_JAVA_INIT;
	ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_init);

	//niceway_entry();

	/////////File odex = this.getDir("assets", MODE_PRIVATE);
	jclass contextWrapperClass = (*env)->FindClass(env, contentWrap);
	jmethodID getDirMethodID = (*env)->GetMethodID(env, contextWrapperClass, "getCodeCacheDir", "()Ljava/io/File;");
	jstring path_name = (*env)->NewStringUTF(env, "code_cache");

	jclass contextClass = (*env)->FindClass(env, java_content);
	jfieldID fid = (*env)->GetStaticFieldID(env, contextClass, java_private_mode, "I");
	jint i = (*env)->GetStaticIntField(env, contextClass, fid);
	jobject fileObj = (*env)->CallObjectMethod(env, application, getDirMethodID, path_name, i);

	////////String odexPath = odex.getAbsolutePath();
	jclass fileClass = (*env)->FindClass(env, "java/io/File");
	jmethodID getAbsolutePath_methodID = (*env)->GetMethodID(env, fileClass, "getAbsolutePath", "()Ljava/lang/String;");
	jstring odexPath = (jstring)(*env)->CallObjectMethod(env, fileObj, getAbsolutePath_methodID);

	jstring targetFilename = get_target(env, obj, application);

	//////////////////////File targetApkZipFile = new File(targetFilename);
	jmethodID initFile_methodID = (*env)->GetMethodID(env, fileClass, java_init, "(Ljava/lang/String;)V");
	jobject targetApkZipFileObj = (*env)->NewObject(env, fileClass, initFile_methodID, targetFilename);

	//////////////////////targetApkZipFile.createNewFile();
	jmethodID createNewFile_methodID = (*env)->GetMethodID(env, fileClass, "createNewFile", "()Z");
	(*env)->CallBooleanMethod(env, targetApkZipFileObj,createNewFile_methodID);


	//TODO 解密
	jbyteArray classesDexData = readNiceWay_01(env, obj);
	readNiceWay_02(env, obj, classesDexData, targetFilename);

    LOGI("=============== before run is ok ===============");
	run(env, obj, targetFilename, odexPath, libraryPath, parent, loadedApk);

}

__attribute__((section (".kcniceway")))void app_nice_way
		(JNIEnv *env, jobject obj, jobject application, jstring libraryPath, jobject parent, jobject loadedApk) {

    //android/content/ContextWrapper
    char contentWrap[] = KCAPP_JAVA_CONTENTWRAP;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, contentWrap);
    //getDir
    char java_getdir[] = KCAPP_JAVA_GETDIR;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_getdir);
    //assets
    char java_asset[] = KCAPP_JAVA_ASSET;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_asset);
    //android/content/Context
    char java_content[] = KCAPP_JAVA_CONTENT;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_content);
    //MODE_PRIVATE
    char java_private_mode[] = KCAPP_JAVA_PVMODE;
    ObfuscateCharv2(KCAPP_JAVACLASS_KEY, java_private_mode);

	//niceway_entry();

    jclass contextWrapperClass = (*env)->FindClass(env, contentWrap);
    jmethodID getDirMethodID = (*env)->GetMethodID(env, contextWrapperClass, "getCodeCacheDir", "()Ljava/io/File;");
    jstring path_name = (*env)->NewStringUTF(env, "code_cache");

    jclass contextClass = (*env)->FindClass(env, java_content);
    jfieldID fid = (*env)->GetStaticFieldID(env, contextClass, java_private_mode, "I");
    jint i = (*env)->GetStaticIntField(env, contextClass, fid);
    jobject fileObj = (*env)->CallObjectMethod(env, application, getDirMethodID, path_name, i);

    jclass fileClass = (*env)->FindClass(env, "java/io/File");
    jmethodID getAbsolutePath_methodID = (*env)->GetMethodID(env, fileClass, "getAbsolutePath", "()Ljava/lang/String;");
    jstring odexPath = (jstring)(*env)->CallObjectMethod(env, fileObj, getAbsolutePath_methodID);

    jstring targetFilename = get_target(env, obj, application);

    run(env, obj, targetFilename, odexPath, libraryPath, parent, loadedApk);
}

__attribute__((section (".kcniceway")))jstring get_target_file
        (JNIEnv *env, jobject obj, jobject application){
    return get_target(env, obj, application);
}

__attribute__((section (".kcniceway")))jboolean mg_present
		(JNIEnv *env, jobject ob, jint pid){
	main_pid = (int)pid;
	jboolean result = JNI_FALSE;
	result = loop_status();
	result = result == JNI_TRUE ? result : loop_namedpipe();
	result = result == JNI_TRUE ? result : loop_mg();

	return result;
}



////////////////////////////////////
///JNI方法注册
////////////////////////////////////

static JNINativeMethod gMethods[] = 
{
	{"start", "(Landroid/app/Application;Ljava/lang/String;Ljava/lang/ClassLoader;Ljava/lang/Object;)V", (void*)native_start},
	{"niceway_start", "(Landroid/app/Application;Ljava/lang/String;Ljava/lang/ClassLoader;Ljava/lang/Object;)V", (void*)app_nice_way},
    {"get_target", "(Landroid/app/Application;)Ljava/lang/String;", (void*)get_target_file},
	{"mg_present", "(I)Z", (void*)mg_present}
};


static int registerNativeMethods(JNIEnv* env, const char* className, 
	JNINativeMethod* gMethods, int numMethods)
{
	jclass clazz;
	clazz = (*env)->FindClass(env, className);
	if(clazz == NULL)
		return JNI_FALSE;

	if((*env)->RegisterNatives(env, clazz, gMethods, numMethods) < 0)
		return JNI_FALSE;

	return JNI_TRUE;
}

static int registerNatives(JNIEnv* env)
{
    char reg_class[] = KCAPP_JNIREG_CLASS;
    ObfuscateCharv2(KCAPP_CLASS_KEY, reg_class);

	if(!registerNativeMethods(env, reg_class, gMethods, sizeof(gMethods)/sizeof(gMethods[0])))
		return JNI_FALSE;
	return JNI_TRUE;
}

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM*vm, void* reserved)
{
	JNIEnv* env = NULL;
	jint result = -1;
    jvm = vm;
    so_name = "libklabniceway.so";


	if( (*vm)->GetEnv(vm, (void**)&env, JNI_VERSION_1_4) != JNI_OK)
		return -1;

	if(env == NULL)
		return -1;

	if(!registerNatives(env))
		return -1;

	result = JNI_VERSION_1_4;

    char sdk[128] = "0";

    __system_property_get("ro.build.version.sdk", sdk);
	global_api_level = atoi(sdk);

	// __android_log_print(ANDROID_LOG_INFO, "JNITag", "pid = %d\n", getpid());
	return result;

}

JNIEXPORT void JNICALL JNI_OnUnload(JavaVM *vm, void *reserved){
	JNIEnv* env = NULL;

    char reg_class[] = KCAPP_JNIREG_CLASS;
    ObfuscateCharv2(KCAPP_CLASS_KEY, reg_class);
	if ((*vm)->GetEnv(vm, (void**) &env, JNI_VERSION_1_4) != JNI_OK) {
		return;
	}
	(*env) -> UnregisterNatives(env, reg_class);
}

