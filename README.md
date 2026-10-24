# Shima

<img src="art/icon/shima-icon-512.png" alt="Shima icon" width="128" />

Shima (島, "island") is a fork of [Island](https://github.com/oasisfeng/island) by Oasis Feng, based on its `dev` branch (v6.4.2).
It installs as `com.theycallmejuzou.shima` and can live side-by-side with the original Island.

### Differences from upstream

* Application ID, `sharedUserId`, permissions, intent actions/categories and content provider authorities use the `com.theycallmejuzou.shima` prefix.
  Java/Kotlin packages and Gradle namespaces are intentionally kept as `com.oasisfeng.island.*` to keep merging upstream changes easy.
* User-visible name is "Shima".
* The private `ninja` module (not published upstream) is dropped from the build.
* `assembly/google-services.json` is a placeholder. Replace it with your own Firebase project's config to get analytics / crash reports.
* The Open API (see below) uses the `com.theycallmejuzou.shima.*` action and permission names, so apps built for Island's API must target Shima explicitly.

To pull in upstream changes: `git fetch upstream && git merge upstream/dev`.

## Build Instructions

Requirements: JDK 17, Android SDK with platform `android-35` and build-tools `34.0.0`.

Shima depends on ["deagle" library](https://github.com/oasisfeng/deagle) (branch `dev`), which must be cloned alongside Shima in the same path.

```
\--
  \- shima
  \- deagle
```

Build the full debug APK with `./gradlew assembleCompleteNormalDebug` (output in `assembly/build/outputs/apk/`).

This project is constructed into several modules, with **assembly** module as the build portal,
to support separate "light" build for core modules, in the form of "product flavor" in Gradle build configuration.

The **"engine"** module shares the same package name with the **"complete"** build, to inherit the profile/device owner privilege.
The **"mobile"** and other modules can be installed and updated separately alongside **"engine"** module for development convenience.

## Open API

Due to the exclusivity nature, user could only use one Android DPC app at a time, and price of switching DPC is far too heavy. To encourage active exploration and broader development in the capabilities of DPC and therefore better benefit users,
Island is devoted to build an open collaboration for community developers, either in development of this project or opening DPC capabilities to 3rd-party apps via open API. Island itself will not focus on the rich set of features, but mainly focuses on building a powerful **engine** as an open platform for much more apps from the community.

Starting from the first public version of Island, all APIs are open to 3rd-party apps with the standard runtime-permission of Android as user authorization. Developers can start building apps now to take advantage of the Island open APIs.

The protocol of all APIs are well defined and maintained in the **[class "Api"](/shared/src/main/java/com/oasisfeng/island/api/Api.java)**. 

## Contribution

If you found bugs, made minor improvements or translated the strings, please feel free to send us pull-requests.

If you are interested in improving the functionality of Island, please create an issue first to discuss your thoughts with us, we are open to collaboration in future development.

If you need new APIs for your apps to take advantage of the DPC capabilities, please feel free to create an issue to describe your app and its use case of those APIs. We are still in the early stage of building a rich set of open APIs.
