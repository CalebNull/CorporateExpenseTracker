package com.wgu.capstone.expenseapproval.ui.screens.requestdetail

import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.getValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wgu.capstone.expenseapproval.data.auth.Session
import com.wgu.capstone.expenseapproval.data.models.AuditLogEntry
import com.wgu.capstone.expenseapproval.data.models.ExpenseRequest
import com.wgu.capstone.expenseapproval.data.network.DecisionBody
import com.wgu.capstone.expenseapproval.data.network.DeleteRequestBody
import com.wgu.capstone.expenseapproval.data.network.MarkPaidBody
import com.wgu.capstone.expenseapproval.data.network.RetrofitClient
import kotlinx.coroutines.launch

class RequestDetailViewModel : ViewModel() {
    var request by mutableStateOf<ExpenseRequest?>(null)
        private set
    var auditTrail by mutableStateOf<List<AuditLogEntry>>(emptyList())
        private set
    var isLoading by mutableStateOf(false)
        private set
    var errorMessage by mutableStateOf<String?>(null)
        private set
    var isDeleted by mutableStateOf(false)
        private set

    fun load(requestId: String) {
        isLoading = true
        errorMessage = null

        viewModelScope.launch {
            try {
                request = RetrofitClient.api.getRequest(requestId)
                auditTrail = RetrofitClient.api.getAuditTrail(requestId)
            } catch (e: Exception) {
                errorMessage = e.message ?: "Something went wrong"
            } finally {
                isLoading = false
            }
        }
    }

    fun approve(requestId: String) = decide(requestId, "approve")
    fun reject(requestId: String) = decide(requestId, "reject")

    private fun decide(requestId: String, decision: String) {
        val approverId = Session.currentUser?.userId ?: return
        isLoading = true
        viewModelScope.launch {
            try {
                RetrofitClient.api.decisionRequest(requestId, DecisionBody(approverId = approverId, decision = decision))
                load(requestId)
            } catch (e: Exception) {
                errorMessage = e.message ?: "Something went wrong"
                isLoading = false
            }
        }
    }

    fun markPaid(requestId: String) {
        val financeUserId = Session.currentUser?.userId ?: return
        isLoading = true
        viewModelScope.launch {
            try {
                RetrofitClient.api.markPaid(requestId, MarkPaidBody(financeUserId = financeUserId))
                load(requestId)
            } catch (e: Exception) {
                errorMessage = e.message ?: "Something went wrong"
                isLoading = false
            }
        }
    }

    fun delete(requestId: String) {
        val employeeId = Session.currentUser?.userId ?: return
        isLoading = true
        viewModelScope.launch {
            try {
                RetrofitClient.api.deleteRequest(requestId, DeleteRequestBody(employeeId))
                isDeleted = true
            } catch (e: Exception) {
                errorMessage = e.message ?: "Something went wrong"
                isLoading = false
            }
        }
    }
}