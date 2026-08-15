package com.wgu.capstone.expenseapproval.ui.screens.requestlist

import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.getValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wgu.capstone.expenseapproval.data.models.ExpenseRequest
import com.wgu.capstone.expenseapproval.data.network.RetrofitClient
import kotlinx.coroutines.launch

class RequestListViewModel : ViewModel() {
    var employeeIdFilter by mutableStateOf("")
    var statusFilter by mutableStateOf("")
    var departmentFilter by mutableStateOf("")

    var isLoading by mutableStateOf(false)
        private set
    var errorMessage by mutableStateOf<String?>(null)
        private set
    var results by mutableStateOf<List<ExpenseRequest>>(emptyList())
        private set

    fun search() {
        if (employeeIdFilter.isBlank() && statusFilter.isBlank() && departmentFilter.isBlank()) {
            errorMessage = "Enter at least one filter to search"
            return
        }

        isLoading = true
        errorMessage = null

        viewModelScope.launch {
            try {
                results = RetrofitClient.api.searchRequests(
                    employeeId = employeeIdFilter.ifBlank { null },
                    status = statusFilter.ifBlank { null },
                    department = departmentFilter.ifBlank { null },
                )
            } catch (e: Exception) {
                errorMessage = e.message ?: "Something went wrong"
                results = emptyList()
            } finally {
                isLoading = false
            }
        }
    }
}