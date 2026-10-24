package com.oasisfeng.island.engine

import android.app.admin.DevicePolicyManager.FLAG_MANAGED_CAN_ACCESS_PARENT
import android.content.Context
import android.content.Intent.ACTION_GET_CONTENT
import android.content.Intent.ACTION_OPEN_DOCUMENT
import android.content.Intent.CATEGORY_DEFAULT
import android.content.Intent.CATEGORY_OPENABLE
import com.oasisfeng.android.content.IntentFilters
import com.oasisfeng.island.shared.R
import com.oasisfeng.island.util.DevicePolicies

/**
 * Shima: let apps in the parent profile (Mainland) pick files in the managed profile (Shima) through the system pickers,
 * i.e. the "Work" tab of the file / photo picker. Off by default, toggled in Shima's own settings.
 *
 * Cross-profile intent filters can only be removed all at once, so toggling triggers [ACTION_REFRESH] in IslandProvisioning,
 * which clears them and re-adds the standard set (including these filters if enabled).
 */
object CrossProfileFileAccess {

	const val ACTION_REFRESH = "com.theycallmejuzou.shima.action.REFRESH_CROSS_PROFILE_FORWARDING"

	/** Stored in device-protected default preferences, where IslandSettingsFragment keeps its preferences. */
	@JvmStatic fun isEnabled(context: Context) = context.createDeviceProtectedStorageContext()
		.getSharedPreferences(context.packageName + "_preferences", Context.MODE_PRIVATE)
		.getBoolean(context.getString(R.string.setting_cross_profile_file_access), false)

	/** Must be called by the profile owner in the managed profile. */
	@JvmStatic fun addFilters(policies: DevicePolicies) {
		for (action in arrayOf(ACTION_GET_CONTENT, ACTION_OPEN_DOCUMENT))
			policies.addCrossProfileIntentFilter(IntentFilters.forAction(action).withCategories(CATEGORY_DEFAULT, CATEGORY_OPENABLE)
				.withDataType("*/*"), FLAG_MANAGED_CAN_ACCESS_PARENT)
		// System photo picker (MediaStore.ACTION_PICK_IMAGES, API 33+), with or without a MIME type
		policies.addCrossProfileIntentFilter(IntentFilters.forAction(ACTION_PICK_IMAGES).withCategory(CATEGORY_DEFAULT)
			.withDataType("image/*").withDataType("video/*"), FLAG_MANAGED_CAN_ACCESS_PARENT)
		policies.addCrossProfileIntentFilter(IntentFilters.forAction(ACTION_PICK_IMAGES).withCategory(CATEGORY_DEFAULT),
			FLAG_MANAGED_CAN_ACCESS_PARENT)
	}

	private const val ACTION_PICK_IMAGES = "android.provider.action.PICK_IMAGES"
}
