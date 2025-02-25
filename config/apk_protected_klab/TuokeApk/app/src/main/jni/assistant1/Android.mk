LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := assistant1

define walk
$(wildcard $(1)) $(foreach e, $(wildcard $(1)/*), $(call walk, $(e)))
endef


LOCAL_SRC_FILES := assistant1.c \
                   checksum.c
LOCAL_LDLIBS := -llog
#LOCAL_CFLAGS += -fvisibility=hidden -mllvm -sub_loop=6 -mllvm -bcf_loop=3 -mllvm -bcf_prob=50 -mllvm -fla
LOCAL_CPPFLAGS += -std=c++11

ifeq ($(TARGET_ARCH_ABI),arm64-v8a)
	LOCAL_CFLAGS += -D_64_BIT
endif
include $(BUILD_SHARED_LIBRARY)


