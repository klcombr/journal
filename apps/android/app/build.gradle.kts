plugins {
    id("com.android.application")
}

val webAppUrl = (project.findProperty("WEB_APP_URL") as String?)
    ?: "https://klcombr.github.io/journal/apps/web/"

android {
    namespace = "br.com.klcombr.journal"
    compileSdk = 35

    defaultConfig {
        applicationId = "br.com.klcombr.journal"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "2.0.0"
        buildConfigField("String", "WEB_APP_URL", "\"$webAppUrl\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }

    buildFeatures {
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation("androidx.webkit:webkit:1.12.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.core:core-ktx:1.13.1")
    constraints {
        implementation("org.jetbrains.kotlin:kotlin-stdlib:1.9.25")
        implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.9.25")
        implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.9.25")
    }
}
