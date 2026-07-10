plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "uz.cyberguardian.android"
    compileSdk = 35

    defaultConfig {
        applicationId = "uz.cyberguardian.android"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.2.0-v1-shell"
    }

    sourceSets {
        getByName("main") {
            java.srcDirs("../src/main/java")
            manifest.srcFile("../src/main/AndroidManifest.xml")
        }
    }

    buildFeatures {
        compose = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    val composeBom = platform("androidx.compose:compose-bom:2024.12.01")
    // Uncomment when building in Android Studio:
    // implementation(composeBom)
    // implementation("androidx.compose.ui:ui")
    // implementation("androidx.compose.material3:material3")
    // implementation("androidx.activity:activity-compose:1.9.3")
    // implementation("com.squareup.okhttp3:okhttp:4.12.0")
}
