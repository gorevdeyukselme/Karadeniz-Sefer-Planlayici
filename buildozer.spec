[app]
title = Karadeniz Sefer Planlayici
package.name = karadenizsefer
package.domain = tr.gov.seferplanlayici
source.dir = .
source.include_exts = py,csv,kv,atlas,png,jpg
version = 0.4
requirements = python3,kivy,kivy_garden.mapview,plyer,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 35
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
