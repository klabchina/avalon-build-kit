LOCAL_PATH:= $(call my-dir)

APP_ABI := all
include $(CLEAR_VARS)
APP_PROJECT_PATH := $(call my-dir)/../
APP_MODULES      := klabniceway assistant1 assistant2

TEST_ROOT_DIR:=$(APP_PROJECT_PATH)jni/