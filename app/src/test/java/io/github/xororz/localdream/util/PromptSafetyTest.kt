package io.github.xororz.localdream.util

import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test

class PromptSafetyTest {
    @Test
    fun blocksSexualisedMinor() {
        assertNotNull(PromptSafety.blockReason("1girl, loli, nude, explicit"))
        assertNotNull(PromptSafety.blockReason("小女孩，裸体"))
    }

    @Test
    fun blocksExplicitSexualContent() {
        assertNotNull(PromptSafety.blockReason("two people having sex, nude"))
        assertNotNull(PromptSafety.blockReason("全裸，性交"))
    }

    @Test
    fun allowsOrdinaryPrompts() {
        assertNull(PromptSafety.blockReason("masterpiece, 1girl, white shirt, portrait, soft light"))
        assertNull(PromptSafety.blockReason("一只猫在窗台上晒太阳"))
    }

    @Test
    fun allowsNonSexualMinorDescription() {
        // A child can be drawn safely; only sexualised content is blocked.
        assertNull(PromptSafety.blockReason("a child playing in a sunny park, watercolor"))
    }
}
