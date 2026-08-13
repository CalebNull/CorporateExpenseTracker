package com.wgu.capstone.expenseapproval.data.models

import com.google.gson.annotations.SerializedName


data class ExpenseRequest(
    @SerializedName("request_id") val requestId: String,
    @SerializedName("employee_id") val employeeId: String,
    val department: String,
    val category: String,
    val amount: Double,
    val description: String,
    val status: String,
    @SerializedName("date_submitted") val dateSubmitted: String?,
    @SerializedName("date_decided") val dateDecided: String?,
    @SerializedName("approver_id") val approverId: String?,
)
