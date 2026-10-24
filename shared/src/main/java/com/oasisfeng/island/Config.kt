package com.oasisfeng.island

/**
 * Configurable values.
 *
 * Shima: Island fetched these from its Firebase Remote Config; Shima has no remote config, so the defaults are used.
 *
 * Created by Oasis on 2016/5/26.
 */
enum class Config(private val key: String, private val default: String) {
	IS_REMOTE("is_remote", ""),
	URL_PLAY_ALPHA("url_play_alpha", "https://groups.google.com/g/islandroid"),
	URL_FAQ("url_faq", "https://island.oasisfeng.com/faq"),
	URL_SETUP("url_setup", "https://island.oasisfeng.com/setup"),
	URL_SETUP_MANAGED_MAINLAND("url_setup_god_mode", "https://island.oasisfeng.com/setup#activate-managed-mainland"),
	URL_SETUP_TROUBLESHOOTING("url_setup_trouble", "https://island.oasisfeng.com/faq"),
	PERMISSION_REQUEST_ALLOWED_APPS("permission_allowed_apps", "com.oasisfeng.greenify,com.oasisfeng.nevo");

	fun get(): String = default

	companion object {
		@JvmStatic fun isRemote() = false
	}
}
