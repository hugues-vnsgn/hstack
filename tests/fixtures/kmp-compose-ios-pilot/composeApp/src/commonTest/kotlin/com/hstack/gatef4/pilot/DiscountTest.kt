package com.hstack.gatef4.pilot

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

class DiscountTest {
    @Test
    fun subtotalBelowThresholdHasNoDiscount() {
        assertEquals(0, discountCents(9_999))
    }

    @Test
    fun subtotalAboveThresholdGetsTenPercentDiscount() {
        assertEquals(1_000, discountCents(10_001))
    }

    @Test
    fun negativeSubtotalIsRejected() {
        assertFailsWith<IllegalArgumentException> { discountCents(-1) }
    }
}
