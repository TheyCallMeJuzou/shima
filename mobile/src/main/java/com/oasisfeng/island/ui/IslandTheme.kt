package com.oasisfeng.island.ui

import android.os.Build.VERSION.SDK_INT
import android.os.Build.VERSION_CODES.S
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext

@Composable fun IslandTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    val context = LocalContext.current
    val systemColors = remember(context) { ShimaDynamicColors.isEnabled(context) }
    val colorScheme = if (SDK_INT >= S && systemColors) { if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context) }
        else if (darkTheme) ShimaDarkColorScheme else ShimaLightColorScheme
    MaterialTheme(colorScheme = colorScheme, content = content)
}
