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
        versionName = "0.1.0-v1-shell"
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
    // Add Compose BOM + Retrofit when opening in Android Studio.
    // implementation(platform("androidx.compose:compose-bom:2024.12.01"))
}
