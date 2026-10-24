package com.oasisfeng.island.ui

import android.content.Context
import android.content.DialogInterface
import android.content.DialogInterface.OnMultiChoiceClickListener
import android.util.TypedValue
import android.view.ContextThemeWrapper
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView
import androidx.annotation.CheckResult
import androidx.annotation.StringRes
import androidx.appcompat.app.AlertDialog
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.progressindicator.CircularProgressIndicator
import com.oasisfeng.island.shared.R

/**
 * Shima: Material 3 dialogs (Material Components' MaterialAlertDialogBuilder), replacing deagle's framework-AlertDialog `Dialogs`
 * with the same API. Hosts without a Material 3 theme (translucent / setup wizard activities) get the Shima theme.
 */
object Dialogs {

	@JvmStatic @CheckResult fun builder(context: Context) = Builder(themed(context))

	@JvmStatic @CheckResult fun buildAlert(context: Context, @StringRes title: Int, @StringRes message: Int)
		= buildAlert(context, if (title != 0) context.getText(title) else null, if (message != 0) context.getText(message) else null)
	@JvmStatic @CheckResult fun buildAlert(context: Context, title: CharSequence?, message: CharSequence?) = builder(context).apply {
		if (title != null) setTitle(title)
		if (message != null) setMessage(message) }

	@JvmStatic @CheckResult fun buildList(context: Context, @StringRes title: Int, items: Array<out CharSequence?>, listener: DialogInterface.OnClickListener)
		= buildList(context, if (title != 0) context.getText(title) else null, items, listener)
	@JvmStatic @CheckResult fun buildList(context: Context, title: CharSequence?, items: Array<out CharSequence?>, listener: DialogInterface.OnClickListener)
		= builder(context).apply { if (title != null) setTitle(title); setItems(items, listener) }

	@JvmStatic @CheckResult fun buildCheckList(context: Context, title: CharSequence?, items: Array<out CharSequence?>, checkedItems: BooleanArray?,
	                                           listener: OnMultiChoiceClickListener)
		= builder(context).apply { if (title != null) setTitle(title); setMultiChoiceItems(items, checkedItems, listener) }

	@JvmStatic @CheckResult fun buildProgress(context: Context, @StringRes message: Int) = buildProgress(context, context.getText(message))
	@JvmStatic @CheckResult fun buildProgress(context: Context, message: CharSequence) = FluentProgressDialog(themed(context), message)

	/** Shortcuts for simpler building. Call them before the setters inherited from [MaterialAlertDialogBuilder], which return the base type. */
	class Builder internal constructor(context: Context) : MaterialAlertDialogBuilder(context) {
		@CheckResult fun withOkButton(task: Runnable?) = apply {
			setPositiveButton(android.R.string.ok, if (task == null) null else DialogInterface.OnClickListener { _, _ -> task.run() }) }
		@CheckResult fun withCancelButton() = apply { setNegativeButton(android.R.string.cancel, null) }
	}

	/** Indeterminate progress, as a Material dialog (ProgressDialog is deprecated). */
	class FluentProgressDialog internal constructor(context: Context, message: CharSequence) {

		fun indeterminate() = this      // Always indeterminate
		fun nonCancelable() = apply { mDialog.setCancelable(false) }
		fun onCancel(listener: DialogInterface.OnCancelListener) = apply { mDialog.setOnCancelListener(listener) }
		fun start() = apply { mDialog.show() }
		fun show() = mDialog.show()
		fun dismiss() = mDialog.dismiss()

		private val mDialog: AlertDialog = MaterialAlertDialogBuilder(context).setView(LinearLayout(context).apply {
			val padding = (24 * resources.displayMetrics.density).toInt()
			setPadding(padding, padding, padding, padding); gravity = Gravity.CENTER_VERTICAL
			addView(CircularProgressIndicator(context).apply { isIndeterminate = true })
			addView(TextView(context).apply { text = message; setPaddingRelative(padding, 0, 0, 0)
				setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_BodyLarge) })
		}).create()
	}

	/** Material dialogs need a Material 3 (AppCompat) theme; activities on framework themes get the Shima theme for the dialog. */
	private fun themed(context: Context): Context {
		val value = TypedValue()
		val isMaterial3 = context.theme.resolveAttribute(com.google.android.material.R.attr.isMaterial3Theme, value, true) && value.data != 0
		return if (isMaterial3) context else ContextThemeWrapper(context, R.style.Base_Shima)
	}
}
