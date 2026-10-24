# Changelog

Shima versions are `<Island version>-shima.<n>`, with `versionCode = <Island versionCode> + n`
(e.g. 6.4.2-shima.1 = 64201). Releases are built by the Gitea pipeline from tags `v<version>`.

## 6.4.2-shima.1

First Shima release, based on Island 6.4.2 (`upstream/dev`).

- Rebranded as Shima (`com.theycallmejuzou.shima`), installable next to Island.
- Sakura launcher icon and Fuji symbol; Material 3 UI with a colour scheme generated from seed `#C94F7C`,
  optional system (Material You) colours on Android 12+.
- Settings on AndroidX Preference; dialogs on Material Components.
- Opt-in "Pick files from Mainland apps": personal apps' file and photo pickers can open files in Shima.
- No analytics or crash reporting (Google Analytics and Firebase removed).
- Fixes: startup crash with a placeholder Firebase key; release build stripping Settings screens.
