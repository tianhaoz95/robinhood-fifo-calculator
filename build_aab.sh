#!/bin/sh

# pip3 install git+https://github.com/flet-dev/python-for-android.git@3.11.6

# export JAVA_HOME="/home/tianhaoz/Dev/android-studio/jbr"
# export JAVA_HOME="/usr/lib/jvm/temurin-8-jdk-amd64/"
export JAVA_HOME="/usr/lib/jvm/temurin-21-jdk-amd64/"
export ANDROID_SDK_ROOT="/home/tianhaoz/Android/Sdk"
# export NDK_VERSION="27.0.11902837"
export NDK_VERSION=25.2.9519653
export SDK_VERSION=android-33
export PATH=$ANDROID_SDK_ROOT/tools/bin:$PATH

# echo "y" | sdkmanager --install "ndk;$NDK_VERSION" --channel=3
# echo "y" | sdkmanager --install "platforms;$SDK_VERSION"

p4a create \
    --requirements pandas \
    --arch arm64-v8a \
    --arch armeabi-v7a \
    --arch x86_64 \
    --sdk-dir $ANDROID_SDK_ROOT \
    --ndk-dir $ANDROID_SDK_ROOT/ndk/$NDK_VERSION \
    --dist-name robinhood1year

export SERIOUS_PYTHON_P4A_DIST="/home/tianhaoz/.local/share/python-for-android/dists/robinhood1year_test"

flet build apk --no-android-splash

flet build aab --no-android-splash

flet build aab --template-dir /home/tianhaoz/Projects/robinhood1year/flet-build-template-0.23.2

# echo "deb https://packages.adoptium.net/artifactory/deb \
#     $(awk -F= '/^UBUNTU_CODENAME/{print$2}' /etc/os-release) main" \
#     | sudo tee /etc/apt/sources.list.d/adoptium.list

keytool \
    -genkey -v \
    -keystore /home/tianhaoz/Projects/robinhood1year/store-key.jks \
    -storetype JKS \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias upload