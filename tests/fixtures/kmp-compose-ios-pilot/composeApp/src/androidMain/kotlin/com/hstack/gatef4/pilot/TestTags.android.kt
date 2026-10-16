package com.hstack.gatef4.pilot

import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.testTagsAsResourceId

internal actual fun Modifier.enableTestTagsAsResourceIds(): Modifier =
    semantics { testTagsAsResourceId = true }
