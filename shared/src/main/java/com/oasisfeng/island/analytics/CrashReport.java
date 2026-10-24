package com.oasisfeng.island.analytics;

import android.util.Log;

/**
 * Crash report breadcrumbs.
 *
 * Shima: Island's Firebase Crashlytics reporting is removed (no crash data leaves the device);
 * breadcrumbs and handled exceptions are only written to logcat.
 *
 * Created by Oasis on 2017/7/14.
 */
public abstract class CrashReport {

	static void logException(final Throwable t) { Log.w(TAG, "Reported exception", t); }
	static void log(final String message) { Log.i(TAG, message); }
	static void setProperty(final String key, final String value) { Log.v(TAG, key + " = " + value); }
	static void setProperty(final String key, final int value) { Log.v(TAG, key + " = " + value); }
	static void setProperty(final String key, final boolean value) { Log.v(TAG, key + " = " + value); }

	/** Uncaught exceptions are left to the default handler. */
	public static void initCrashHandler() {}

	private static final String TAG = "Island.Crash";
}
