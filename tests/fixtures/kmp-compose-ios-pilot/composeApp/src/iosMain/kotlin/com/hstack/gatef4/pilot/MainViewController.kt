package com.hstack.gatef4.pilot

import androidx.compose.ui.window.ComposeUIViewController
import platform.UIKit.UIViewController

public fun MainViewController(): UIViewController = ComposeUIViewController { CalculatorApp() }
