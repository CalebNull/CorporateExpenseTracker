package com.wgu.capstone.expenseapproval.ui.screens.reports

import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.getValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wgu.capstone.expenseapproval.data.models.SpendingReport
import com.wgu.capstone.expenseapproval.data.network.RetrofitClient
import kotlinx.coroutines.launch

class ReportsViewModel : ViewModel() {
    var department by mutableStateOf("")
    var startDate by mutableStateOf("")
    var endDate by mutableStateOf("")

    var isLoading by mutableStateOf(false)
        private set
    var errorMessage by mutableStateOf<String?>(null)
        private set
    var report by mutableStateOf<SpendingReport?>(null)
        private set

    fun generateReport() {
        if (department.isBlank() || startDate.isBlank() || endDate.isBlank()) {
            errorMessage = "Department, start date, and end date are all required"
            return
        }

        isLoading = true
        errorMessage = null

        viewModelScope.launch {
            try {
                report = RetrofitClient.api.getSpendingReports(department, startDate, endDate)
            } catch (e: Exception) {
                errorMessage = e.message ?: "Something went wrong"
                report = null
            } finally {
                isLoading = false
            }
        }
    }
}