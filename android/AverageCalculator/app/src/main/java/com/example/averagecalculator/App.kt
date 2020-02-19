package com.example.averagecalculator

import android.content.Intent
import android.app.Application

class App : Application() {
    override fun onCreate() {
        super.onCreate();
        startService(Intent(this, MyFirebaseMessagingService::class.java));
    }
}