#!/usr/bin/env bash
set -euo pipefail

HOME_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
OBFUSCATOR_CONFIGE_PATH=${OBFUSCATOR_CONFIGE_PATH:-~/.DeClang/config.json}
LAPIS_CLIENT_PLUGIN_IOS_PATH=${1}
OBFUSCATOR_SOURCE_CLASS_NAME=${2}
#TOOL_CHAIN=" -toolchain \"Local Swift Development Snapshot 2021-07-28\""
TOOL_CHAIN_NAME="Local Swift Development Snapshot 2021-10-24"
TOOL_CHAIN=" -toolchain "


export DEVELOPER_DIR=/Applications/Xcode13.0.app/Contents/Developer
xcode-select -p

# pls install ollvm toochain and install
# download path  https://github.com/DeNA/DeClang/releases/tag/swift5.4-v1.1.0

PROJECT_IOSSECURITY=${HOME_DIR}/../../config/ios_protected_klab/IOSSecuritySuite.xcodeproj
SWIFT_OUTPUT=${HOME_DIR}/../../config/ios_protected_klab/swiftshield-output

if [[ -d "${SWIFT_OUTPUT}" ]]; then
	rm -rf ${SWIFT_OUTPUT}
fi

# download ollvm toochain and install
# download url https://github.com/rockbruno/swiftshield/releases/download/4.2.0/swiftshield.zipc
swiftshield obfuscate -p ${PROJECT_IOSSECURITY} -s IOSUtilSuite -i AssemblyLibs

get_swift_shield_latest_result() {
    ls "${SWIFT_OUTPUT}" | sort -r | head -1
}


absfucator_result=$( get_swift_shield_latest_result )


echo ${SWIFT_OUTPUT}/$absfucator_result

# python version 3.7 and pls install dependency by reqirement 
echo python GeneralRandomFunction.py obfuscate -d ${SWIFT_OUTPUT}/$absfucator_result -c $OBFUSCATOR_CONFIGE_PATH -s $OBFUSCATOR_SOURCE_CLASS_NAME 
python GeneralRandomFunction.py obfuscate -d ${SWIFT_OUTPUT}/$absfucator_result -c $OBFUSCATOR_CONFIGE_PATH -s $OBFUSCATOR_SOURCE_CLASS_NAME

# cp category class  *.mm & *.h
cp -rf "${OBFUSCATOR_SOURCE_CLASS_NAME}+NiceWay.mm" $LAPIS_CLIENT_PLUGIN_IOS_PATH
cp -rf "${OBFUSCATOR_SOURCE_CLASS_NAME}+NiceWay.h" $LAPIS_CLIENT_PLUGIN_IOS_PATH


# set project to build arm7  && arm 64 platform
sed -i '' 's/ARCHS = arm64;/ARCHS = "$(ARCHS_STANDARD)";/g' ${PROJECT_IOSSECURITY}/project.pbxproj
# clean project
echo "start clean project "
xcodebuild clean -project ${PROJECT_IOSSECURITY} -scheme IOSUtilSuite -arch arm64
xcodebuild clean -project ${PROJECT_IOSSECURITY} -scheme AssemblyLibs -arch arm64

echo "clean done "


echo "start build project "
# build project 
xcodebuild build $TOOL_CHAIN "${TOOL_CHAIN_NAME}" -project ${PROJECT_IOSSECURITY} -scheme AssemblyLibs -configuration Release -arch arm64 -sdk "iphoneos"
xcodebuild build $TOOL_CHAIN "${TOOL_CHAIN_NAME}" -project ${PROJECT_IOSSECURITY} -scheme IOSUtilSuite -configuration Release -arch arm64 -sdk "iphoneos" > ./result.txt

echo " build done "


# cp builded framework to lapis client project
cat ./result.txt | grep -E 'METAL_LIBRARY_OUTPUT_DIR' | awk -F"[=]" '{print $2}' | xargs -J % cp -rp % $LAPIS_CLIENT_PLUGIN_IOS_PATH









