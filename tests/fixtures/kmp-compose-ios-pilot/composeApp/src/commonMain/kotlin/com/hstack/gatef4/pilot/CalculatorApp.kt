package com.hstack.gatef4.pilot

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.clickable
import androidx.compose.foundation.text.BasicText
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp

internal const val SUBTOTAL_INPUT_TAG = "subtotal_input"
internal const val CALCULATE_BUTTON_TAG = "calculate_button"
internal const val DISCOUNT_RESULT_TAG = "discount_result"

@Composable
internal fun CalculatorApp() {
    val focusManager = LocalFocusManager.current
    var subtotal by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<Int?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .enableTestTagsAsResourceIds()
            .safeDrawingPadding()
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        BasicText("Discount calculator")
        BasicText("Subtotal in cents")
        BasicTextField(
            value = subtotal,
            onValueChange = { subtotal = it },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = 48.dp)
                .padding(12.dp)
                .testTag(SUBTOTAL_INPUT_TAG),
        )
        BasicText(
            text = "Calculate",
            modifier = Modifier
                .fillMaxWidth()
                .testTag(CALCULATE_BUTTON_TAG)
                .clickable(role = Role.Button) {
                    result = subtotal.toIntOrNull()?.takeIf { it >= 0 }?.let(::discountCents)
                    focusManager.clearFocus()
                }
                .padding(12.dp),
        )
        BasicText(
            text = result?.let { "Discount: $it cents" } ?: "Enter a nonnegative whole number of cents",
            modifier = Modifier.testTag(DISCOUNT_RESULT_TAG),
        )
    }
}
