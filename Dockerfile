# 使用基础镜像
FROM ubuntu:22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive \
    ANDROID_HOME=/usr/local/android-sdk \
    ANDROID_NDK_HOME=/usr/local/android-sdk/ndk/23.1.7779620 \
    PATH="$PATH:/usr/local/android-sdk/cmdline-tools/latest/bin:/usr/local/android-sdk/platform-tools:/usr/local/android-sdk/build-tools:/usr/local/android-ndk:/usr/local/android-sdk/ndk/23.1.7779620"

# 更新系统并安装必要工具
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    git \
    zip \
    build-essential \
    python3.11 \
    python3.11-venv \
    python3.11-distutils \
    openjdk-17-jdk \
    && apt-get clean

# 设置 Python 11 的别名
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 安装 Gradle 8.12
RUN wget https://services.gradle.org/distributions/gradle-8.12-bin.zip -P /tmp \
    && unzip /tmp/gradle-8.12-bin.zip -d /opt \
    && rm /tmp/gradle-8.12-bin.zip \
    && ln -s /opt/gradle-8.12/bin/gradle /usr/bin/gradle

# 安装 Android SDK 和必要的工具
RUN mkdir -p $ANDROID_HOME \
    && wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip -P /tmp \
    && unzip /tmp/commandlinetools-linux-9477386_latest.zip -d $ANDROID_HOME/cmdline-tools \
    && mv $ANDROID_HOME/cmdline-tools/cmdline-tools $ANDROID_HOME/cmdline-tools/latest \
    && rm /tmp/commandlinetools-linux-9477386_latest.zip

# 接受 SDK 许可并安装 Android SDK 34、33 和构建工具
RUN yes | sdkmanager --licenses \
    && sdkmanager "platform-tools" \
    "platforms;android-34" \
    "platforms;android-33" \
    "build-tools;34.0.0" \
    "build-tools;33.0.2"

# 安装 Android NDK 23.1.7779620
RUN sdkmanager "ndk;23.1.7779620"

# pip安装
RUN curl -O https://bootstrap.pypa.io/get-pip.py \
    && python get-pip.py 

# 下载 bundletool 最新版本
RUN wget https://github.com/google/bundletool/releases/download/1.17.2/bundletool-all-1.17.2.jar -O /usr/local/bin/bundletool.jar

# 添加执行权限并创建快捷命令
RUN echo '#!/bin/bash\njava -jar /usr/local/bin/bundletool.jar "$@"' > /usr/local/bin/bundletool && \
    chmod +x /usr/local/bin/bundletool


# 验证安装
RUN python --version && \
    pip --version && \
    java --version && \
    gradle --version && \
    sdkmanager --list && \
    ndk-build --version && \
    bundletool version

RUN mkdir -p /workspace/req
COPY ./requirements.txt /workspace/req/


# 默认工作目录
WORKDIR /workspace/worker/scripts


RUN pip install -r /workspace/req/requirements.txt

# 添加脚本文件或其他资源（根据需要）

# 入口点（根据需要修改）
CMD ["python", "main.py", "protected", "protectedaab", "-p", "/workspace/output/Android.aab" ,"-s", "CC"]