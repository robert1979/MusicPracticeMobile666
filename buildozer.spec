[app]

# (str) Title of your application
title = MusicPractice

# (str) Package name
package.name = musicpractice

# (str) Package domain (needed for android/ios packaging)
package.domain = org.robertattard

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 0.1

# (list) Application requirements
requirements = python3, kivy, kivymd

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions required for Android
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Minimum API level for Android
android.minapi = 21

# (int) Target API level for Android
android.api = 31

# (int) NDK API level for Android
android.ndk_api = 21

# (list) Supported architectures for Android
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup of the app data on Android
android.allow_backup = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
