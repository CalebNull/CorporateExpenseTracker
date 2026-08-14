package com.wgu.capstone.expenseapproval.ui.screens.submit

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wgu.capstone.expenseapproval.data.auth.Session
import com.wgu.capstone.expenseapproval.data.network.RetrofitClient
import com.wgu.capstone.expenseapproval.data.network.SubmitRequestBody
import kotlinx.coroutines.launch

class SubmitRequestViewModel : ViewModel() {
    var department by mutableStateOf("")
    var category by mutableStateOf("")
    var amount by mutableStateOf("")
    var description by mutableStateOf("")

    var isSubmitting by mutableStateOf(false)
        private set
    var errorMessage by mutableStateOf<String?>(null)
        private set
    var submittedRequestId by mutableStateOf<String?>(null)
        private set

    fun submit() {
        val employeeId = Session.currentUser?.userId
        val amountValue = amount.toDoubleOrNull()

        if (employeeId == null) {
            errorMessage = "You must be logged in to submit a request"
            return
        }

        if (department.isBlank() || category.isBlank() || amountValue == null) {
            errorMessage = "Please fill in all fields with a valid amount"
            return
        }

        isSubmitting = true
        errorMessage = null

        viewModelScope.launch {
            try {
                val result = RetrofitClient.api.submitRequest(
                    SubmitRequestBody(
                        employeeId = employeeId,
                        department = department,
                        category = category,
                        amount = amountValue,
                        description = description,
                    )
                )
                submittedRequestId = result.requestId
            } catch (e: Exception) {
                errorMessage = e.message ?: "Something went wrong"
            } finally {
                isSubmitting = false
            }
        }
    }
}