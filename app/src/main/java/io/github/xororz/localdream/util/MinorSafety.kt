package io.github.xororz.localdream.util

/**
 * et.258: the only remaining hard prompt rule.
 *
 * It deliberately does NOT block adult explicit content and does NOT inspect
 * ordinary prompts. The old [PromptSafety] gate matched raw substrings ("cum"
 * inside "cumulus"/"accumulate"), which is why normal descriptions were being
 * rejected as explicit. This rule fires only when a minor term and an explicit
 * sexual term appear together, using token boundaries for English.
 */
object MinorSafety {
    private val minor = Regex(
        "(?i)(?:^|[^a-z])(?:loli(?:ta)?|shota(?:con)?|underage|preteen|child|children|kid|minor|schoolgirl|schoolboy)(?:[^a-z]|$)" +
            "|未成年|幼女|幼童|萝莉|正太|小女孩|小男孩|儿童|女童|男童|小学生|初中生",
    )

    private val sexual = Regex(
        "(?i)(?:^|[^a-z])(?:nude|naked|topless|bottomless|genital|penis|vagina|vulva|nipple|areola|sex|sexual|intercourse|oral\\s+sex|anal|penetrat\\w*|masturbat\\w*|orgasm|ejaculat\\w*|semen|creampie|porn|hentai|fetish|bdsm|rape|molest\\w*)(?:[^a-z]|$)" +
            "|裸|全裸|裸露|性交|口交|肛交|性器|生殖器|阴茎|阴道|乳头|下体|淫|做爱|强奸|猥亵",
    )

    fun blockReason(prompt: String): String? =
        if (minor.containsMatchIn(prompt) && sexual.containsMatchIn(prompt)) {
            "提示词涉及未成年人的性化内容，已被拦截。"
        } else {
            null
        }
}
