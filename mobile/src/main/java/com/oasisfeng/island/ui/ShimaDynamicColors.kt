package com.oasisfeng.island.ui

import android.app.Activity
import android.content.Context
import android.util.Log
import com.google.android.material.color.DynamicColors
import com.oasisfeng.island.settings.IslandSettings
import com.oasisfeng.island.util.Users

/** Opt-in to the system's Material You colours (Android 12+) instead of the Shima seed colours. */
object ShimaDynamicColors {

	@JvmStatic fun isAvailable() = DynamicColors.isDynamicColorAvailable()

	/** The setting lives in the parent profile and cannot be read from the managed profile (no INTERACT_ACROSS_USERS), so profile UI keeps Shima colours. */
	@JvmStatic fun isEnabled(context: Context) = isAvailable() && Users.isParentProfile() && try { IslandSettings(context).DynamicColors().enabled }
		catch (e: RuntimeException) { false.also { Log.w(TAG, "Error reading setting", e) }}	// e.g. settings provider unavailable before unlock

	/** Call at the start of [Activity.onCreate], before any view is inflated. @return whether system colours are applied */
	@JvmStatic fun apply(activity: Activity) = isEnabled(activity).also { if (it) DynamicColors.applyToActivityIfAvailable(activity) }
}

private const val TAG = "Island.DC"
