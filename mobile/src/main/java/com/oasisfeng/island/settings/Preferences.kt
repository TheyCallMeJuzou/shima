package com.oasisfeng.island.settings

import androidx.annotation.StringRes
import androidx.preference.EditTextPreference
import androidx.preference.Preference
import androidx.preference.PreferenceCategory
import androidx.preference.PreferenceFragmentCompat
import androidx.preference.TwoStatePreference

inline fun <T: Preference> PreferenceFragmentCompat.setup(@StringRes key: Int, crossinline block: T.() -> Unit)
        = @Suppress("UNCHECKED_CAST") (findPreference<Preference>(getString(key)) as? T)?.apply { block() }

fun PreferenceFragmentCompat.remove(preference: Preference) {
    preference.parent?.apply { removePreference(preference); if (this is PreferenceCategory && preferenceCount == 0) remove(this) }
}

fun Preference.onClick(block: Preference.() -> Unit) { onPreferenceClickListener = Preference.OnPreferenceClickListener { block(); true }}
inline fun TwoStatePreference.onChange(crossinline block: (Boolean) -> Boolean) = setOnPreferenceChangeListener { _, v -> block(v as Boolean) }
inline fun EditTextPreference.onChange(crossinline block: (String) -> Boolean) = setOnPreferenceChangeListener { _, v -> block(v as String) }
fun TwoStatePreference.lock(checked: Boolean) { isChecked = checked; isSelectable = false }
