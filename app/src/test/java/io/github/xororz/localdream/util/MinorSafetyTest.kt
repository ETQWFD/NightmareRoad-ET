package io.github.xororz.localdream.util

import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test

class MinorSafetyTest {
    @Test
    fun blocksSexualisedMinor() {
        assertNotNull(MinorSafety.blockReason("1girl, loli, nude"))
        assertNotNull(MinorSafety.blockReason("小女孩，裸体"))
    }

    @Test
    fun allowsAdultContent() {
        assertNull(MinorSafety.blockReason("adult woman, nude, studio light"))
        assertNull(MinorSafety.blockReason("全裸，性交"))
    }

    @Test
    fun allowsOrdinaryPrompts() {
        assertNull(MinorSafety.blockReason("cumulus clouds over a mountain"))
        assertNull(MinorSafety.blockReason("accumulate wealth, still life"))
        assertNull(MinorSafety.blockReason("a child playing in a sunny park, watercolor"))
        assertNull(MinorSafety.blockReason("一只猫在窗台上晒太阳"))
    }
}
