package com.wgu.capstone.expenseapproval.ui.screens.login

import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.compose.runtime.setValue
import androidx.compose.runtime.getValue
import com.wgu.capstone.expenseapproval.data.auth.DemoAccounts
import com.wgu.capstone.expenseapproval.data.auth.Session

class LoginViewModel : ViewModel() {
    var username by mutableStateOf("")
    var password by mutableStateOf("")
    var errorMessage by mutableStateOf<String?>(null)
        private set
    var loginSucceed by mutableStateOf(false)
        private set

    fun login(){
        val account = DemoAccounts.authenticate(username, password)
        if (account == null) {
            errorMessage = "Invalid username or password"
            return
        }
        Session.logIn(account)
        errorMessage = null
        loginSucceed = true
    }
}