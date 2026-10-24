package com.oasisfeng.island.analytics

import android.os.Bundle
import android.util.Log
import androidx.annotation.CheckResult
import org.intellij.lang.annotations.Pattern

/**
 * Shima: local-only implementation. Island's Google Analytics / Firebase Analytics reporting is removed,
 * events and properties are only written to logcat.
 */
internal class AnalyticsImpl : Analytics {

	@CheckResult override fun event(@Pattern("^[a-zA-Z][a-zA-Z0-9_]*$") event: String): Analytics.Event {
		val bundle = Bundle()
		return object : Analytics.Event {
			@CheckResult override fun withRaw(key: String, value: String?) = this.also { bundle.putString(key, value ?: return@also) }
			override fun send() = reportEvent(event, bundle) }
	}

	override fun trace(key: String, value: String): Analytics = this.also { CrashReport.setProperty(key, value) }
	override fun trace(key: String, value: Int): Analytics = this.also { CrashReport.setProperty(key, value) }
	override fun trace(key: String, value: Boolean): Analytics = this.also { CrashReport.setProperty(key, value) }

	override fun report(t: Throwable) = CrashReport.logException(t)
	override fun report(message: String, t: Throwable) { CrashReport.log(message); CrashReport.logException(t) }

	override fun reportEvent(event: String, params: Bundle) {
		Log.d(TAG, if (params.isEmpty) "Event: $event" else "Event: $event $params")
	}

	override fun setProperty(property: Analytics.Property, value: String) {
		Log.d(TAG, "Property: ${property.key} = $value")
	}
}

private const val TAG = "Analytics"
