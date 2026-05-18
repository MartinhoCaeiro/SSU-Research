[app]
title = Vaulted Pass
package.name = vaultedpass
package.domain = org.ssuresearch
source.dir = App
source.include_exts = py,png,jpg,kv,ttf,otf
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

entrypoint = main.py

android.permissions = 
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1