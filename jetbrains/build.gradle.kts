plugins {
    id("java")
    id("org.jetbrains.intellij.platform") version "2.11.0"
}

repositories {
    mavenCentral()
    intellijPlatform { defaultRepositories() }
}

val platformType = project.findProperty("platformType") as? String ?: "IU"
val platformVersion = project.findProperty("platformVersion") as? String ?: "2025.3.2"
val sampleProjectOverride = project.findProperty("sampleProject") as? String
val sampleProjectsMap = mapOf(
    "CL" to "cpp",
    "DB" to "database",
    "GO" to "go",
    "IU" to "java",
    "IC" to "java",
    "PS" to "php",
    "PY" to "python",
    "PC" to "python",
    "RM" to "ruby",
    "RR" to "rust",
    "WS" to "typescript-react"
)
val projectSubDir = sampleProjectOverride ?: sampleProjectsMap[platformType] ?: "java"

dependencies {
    intellijPlatform {
        create(platformType, platformVersion)
    }
}

intellijPlatform {
    buildSearchableOptions = false
    pluginVerification {
        ides {
            recommended()
        }
    }
}

tasks.runIde {
    autoReload.set(true)

    val repoRoot = project.projectDir.parentFile
    val sampleProjectPath = repoRoot.resolve("sample-projects").resolve(projectSubDir).absolutePath
    args(sampleProjectPath)

    systemProperty("ide.experimental.ui", "true")
    systemProperty("idea.trust.all.projects", "true")
    systemProperty("ide.show.tips.on.startup", "false")
    systemProperty("idea.ignore.project.colors", "true")
    systemProperty("jetbrains.privacy_policy.accepted", "true")
}

tasks.patchPluginXml {
    sinceBuild.set("251")
    untilBuild.set(null as String?)
}

tasks.signPlugin {
    certificateChain.set(providers.environmentVariable("CERTIFICATE_CHAIN"))
    privateKey.set(providers.environmentVariable("PRIVATE_KEY"))
    password.set(providers.environmentVariable("PRIVATE_KEY_PASSWORD"))
}

tasks.publishPlugin {
    token.set(providers.environmentVariable("PUBLISH_TOKEN"))
}