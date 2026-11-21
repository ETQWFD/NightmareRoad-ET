package io.github.xororz.localdream.util

/**
 * et.255: hard safety gate for the generation entry points.
 *
 * The diagnostic report exposed a prompt that sexualised a canonically
 * child-like character. That is not a quality bug to tune — it must never
 * reach the diffusion engine. This gate is intentionally narrow and only
 * rejects explicit sexual content, with a separate, stronger rule for minors.
 */
object PromptSafety {
    private val minorTerms = listOf(
        "loli", "lolita", "shota", "shotacon", "underage", "minor child",
        "preteen", "little girl", "little boy", "young girl", "young boy",
        "child", "childish", "child-like", "schoolgirl", "schoolboy",
        "未成年", "幼女", "幼童", "萝莉", "正太", "小女孩", "小男孩",
        "儿童", "女童", "男童", "小学生", "初中生",
    )

    private val sexualTerms = listOf(
        "nude", "naked", "nudity", "topless", "bottomless",
        "genital", "penis", "vagina", "vulva", "nipple", "areola",
        "sex", "sexual", "intercourse", "oral sex", "anal", "penetrat",
        "masturbat", "orgasm", "ejaculat", "cum", "semen", "creampie",
        "porn", "hentai", "fetish", "bdsm", "rape", "molest",
        "裸", "全裸", "裸露", "性交", "口交", "肛交", "性器", "生殖器",
        "阴茎", "阴道", "乳头", "下体", "淫", "做爱", "强奸", "猥亵",
    )

    fun blockReason(prompt: String): String? {
        val text = prompt.lowercase()
        if (sexualTerms.none { text.contains(it) }) return null
        return if (minorTerms.any { text.contains(it) }) {
            "提示词涉及未成年人的性化内容，已被安全策略拦截，无法生成或重试。"
        } else {
            "提示词包含露骨性内容，已被安全策略拦截，请改用非露骨描述。"
        }
    }
}
