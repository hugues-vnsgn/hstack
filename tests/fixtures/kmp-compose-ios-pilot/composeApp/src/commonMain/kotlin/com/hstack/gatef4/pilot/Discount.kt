package com.hstack.gatef4.pilot

internal fun discountCents(subtotalCents: Int): Int {
    require(subtotalCents >= 0) { "Subtotal must be nonnegative" }
    return if (subtotalCents > 10_000) subtotalCents / 10 else 0
}
