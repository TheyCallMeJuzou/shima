package com.oasisfeng.island.settings

import android.content.Context
import android.content.Intent
import android.content.pm.LauncherApps
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.os.UserHandle
import android.os.UserManager
import android.util.Log
import android.view.MenuItem
import android.widget.Toast
import androidx.annotation.XmlRes
import androidx.core.app.NavUtils
import androidx.core.content.getSystemService
import androidx.fragment.app.FragmentActivity
import androidx.preference.Preference
import androidx.preference.PreferenceFragmentCompat
import com.oasisfeng.android.app.Activities
import com.oasisfeng.android.google.GooglePlayStore
import com.oasisfeng.android.ui.Dialogs
import com.oasisfeng.island.Config
import com.oasisfeng.island.IslandNameManager
import com.oasisfeng.island.MainActivity
import com.oasisfeng.island.mobile.BuildConfig
import com.oasisfeng.island.mobile.R
import com.oasisfeng.island.util.DevicePolicies
import com.oasisfeng.island.util.Modules
import com.oasisfeng.island.util.Users
import com.oasisfeng.island.util.Users.Companion.isParentProfile

class SettingsActivity : FragmentActivity(), PreferenceFragmentCompat.OnPreferenceStartFragmentCallback {

	override fun onCreate(savedInstanceState: Bundle?) {
		super.onCreate(savedInstanceState)
		setContentView(R.layout.activity_settings)
		setActionBar(findViewById(R.id.toolbar))
		actionBar?.setDisplayHomeAsUpEnabled(true) // Show the Up button in the action bar.
		mDefaultTitle = title
		supportFragmentManager.addOnBackStackChangedListener { if (supportFragmentManager.backStackEntryCount == 0) title = mDefaultTitle }

		if (savedInstanceState != null) { savedInstanceState.getCharSequence(STATE_TITLE)?.also { title = it }; return }
		val fragment = intent.getStringExtra(EXTRA_SHOW_FRAGMENT)?.takeIf(::isValidFragment)
			?.let { supportFragmentManager.fragmentFactory.instantiate(classLoader, it) } ?: HeadersFragment()
		supportFragmentManager.beginTransaction().replace(R.id.settings_container, fragment).commit()
	}

	override fun onSaveInstanceState(outState: Bundle) = super.onSaveInstanceState(outState).also { outState.putCharSequence(STATE_TITLE, title) }

	override fun onResume() {
		super.onResume()
		if (! DevicePolicies(this).isProfileOrDeviceOwnerOnCallingUser) {
			val profiles = getSystemService<UserManager>()!!.userProfiles
			if (profiles.size == 1) {     // The last Island is just destroyed
				Log.i(TAG, "Nothing left, back to initial setup.")
				finishAffinity()
				startActivity(Intent(this, MainActivity::class.java)) }}
	}

	override fun onOptionsItemSelected(item: MenuItem): Boolean {
		if (item.itemId != android.R.id.home) return super.onOptionsItemSelected(item)
		if (supportFragmentManager.backStackEntryCount > 0) supportFragmentManager.popBackStack()
		else NavUtils.navigateUpFromSameTask(this)
		return true
	}

	/** Open the sub-screen of a header (or "Licenses" in About), with its title in the action bar. */
	override fun onPreferenceStartFragment(caller: PreferenceFragmentCompat, pref: Preference): Boolean {
		val fragmentName = pref.fragment?.takeIf(::isValidFragment) ?: return false
		val fragment = supportFragmentManager.fragmentFactory.instantiate(classLoader, fragmentName).apply { arguments = pref.extras }
		supportFragmentManager.beginTransaction().replace(R.id.settings_container, fragment).addToBackStack(null).commit()
		title = pref.title
		return true
	}

	internal fun launchSettingsActivityAsUser(profile: UserHandle) {
		val la = getSystemService<LauncherApps>()!!
		val activities = la.getActivityList(packageName, profile).map { it.componentName }
		val settingsActivity = activities.firstOrNull { it.className == IslandSettingsActivity::class.java.name}
				?: return Toast.makeText(this, R.string.prompt_island_not_yet_setup, Toast.LENGTH_LONG).show()
		la.startMainActivity(settingsActivity, profile, null, null)
	}

	/** This method stops fragment injection in malicious applications. Make sure to deny any unknown fragments here.  */
	private fun isValidFragment(fragmentName: String) = fragmentName.startsWith(javaClass.getPackage()!!.name)

	class HeadersFragment : PreferenceFragmentCompat() {

		override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) = setPreferencesFromResource(R.xml.pref_headers, rootKey)

		override fun onPreferenceTreeClick(preference: Preference): Boolean {
			if (preference.key != getString(R.string.key_header_island)) return super.onPreferenceTreeClick(preference)

			val users = ArrayList<UserHandle>() // Support multiple managed-profiles
			users.add(Users.parentProfile)
			users.addAll(Users.getProfilesManagedByIsland())
			if (users.size <= 1)        // Managed mainland without Island
				return super.onPreferenceTreeClick(preference)

			val activity = requireActivity() as SettingsActivity
			val names = IslandNameManager.getAllNames(activity)
			val labels = users.map { user ->
				if (user.isParentProfile()) getText(com.oasisfeng.island.shared.R.string.mainland_name) else names[user]
			}.toTypedArray()
			Dialogs.buildList(activity, null, labels) { _, which ->
				if (which == 0) activity.onPreferenceStartFragment(this, preference)
				else activity.launchSettingsActivityAsUser(users[which])
			}.show()
			return true
		}
	}

	abstract class SubPreferenceFragment(@param:XmlRes private val mPreferenceXml: Int) : PreferenceFragmentCompat() {

		override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) = setPreferencesFromResource(mPreferenceXml, rootKey)
	}

	class AboutFragment : SubPreferenceFragment(R.xml.pref_about) {

		override fun onCreate(savedInstanceState: Bundle?) {
			super.onCreate(savedInstanceState)
			val activity = requireActivity()
			val pm = activity.packageManager
			val pkg = activity.packageName
			val installer = pm.getInstallerPackageName(pkg)
			if (installer == GooglePlayStore.PACKAGE_NAME || (BuildConfig.DEBUG && installer == pkg))
				findPreference<Preference>(getString(R.string.key_beta))?.apply {
					summary = getText(R.string.pref_about_beta_play_summary)
					intent = Intent(Intent.ACTION_VIEW, Uri.parse(Config.URL_PLAY_ALPHA.get()))
				}
			try {
				val info = pm.getPackageInfo(pkg, 0)
				var summary: String = info.versionName ?: info.versionCode.toString()
				if (BuildConfig.DEBUG) {
					val ago = System.currentTimeMillis() - info.lastUpdateTime
					summary += " (${info.versionCode}, ${ago / 60_000} minutes ago)"
					if (pkg != Modules.MODULE_ENGINE) try {
						val engine = pm.getPackageInfo(Modules.MODULE_ENGINE, 0)
						summary += ", Engine: " + engine.versionName + " (" + engine.versionCode + ")"
					} catch (ignored: PackageManager.NameNotFoundException) {}
				}
				findPreference<Preference>(getString(R.string.key_version))?.summary = summary
			} catch (ignored: PackageManager.NameNotFoundException) {} // Should never happen
		}
	}

	class LicensesFragment : SubPreferenceFragment(R.xml.pref_licenses)

	companion object {

		@JvmStatic fun startWithPreference(context: Context, fragment: Class<out PreferenceFragmentCompat>) {
			val intent = Intent(context, SettingsActivity::class.java).putExtra(EXTRA_SHOW_FRAGMENT, fragment.name)
			Activities.startActivity(context, intent)
		}
	}

	private lateinit var mDefaultTitle: CharSequence
}

private const val EXTRA_SHOW_FRAGMENT = "show_fragment"
private const val STATE_TITLE = "title"
private const val TAG = "Island.SA"
