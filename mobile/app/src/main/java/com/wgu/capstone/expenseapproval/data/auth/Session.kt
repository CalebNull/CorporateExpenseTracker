package com.wgu.capstone.expenseapproval.data.auth

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue

object Session {
    var currentUser by mutableStateOf<DemoAccount?>(null)

    fun logIn(account: DemoAccount) {
        currentUser = account
    }

    fun logOut() {
        currentUser = null
    }
}