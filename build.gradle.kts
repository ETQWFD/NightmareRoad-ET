// Top-level build file. Plugin versions are explicit because Gradle 9.3's
// version-catalog accessors are not available inside this root plugins block.
plugins {
    id("com.android.application") version "9.1.1" apply false
    id("org.jetbrains.kotlin.android") version "2.3.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.3.21" apply false
}
