package com.oasisfeng.island.settings

import android.content.Context
import android.util.AttributeSet
import android.widget.TextView
import androidx.preference.Preference
import androidx.preference.PreferenceViewHolder

/** Non-selectable preference showing a long summary. AndroidX port of deagle's framework WallOfTextPreference. */
class WallOfTextPreference @JvmOverloads constructor(context: Context, attrs: AttributeSet? = null) : Preference(context, attrs) {

	init { isSelectable = false }

	override fun onBindViewHolder(holder: PreferenceViewHolder) {
		super.onBindViewHolder(holder)
		(holder.findViewById(android.R.id.summary) as? TextView)?.maxLines = 20
	}
}
