  [app]
title = TikTok DL Pro
package.name = tiktokdlpro
package.domain = org.tiktokdl
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy==2.2.1,requests,certifi,urllib3,charset-normalizer,idna
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.release_artifact = apk
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
