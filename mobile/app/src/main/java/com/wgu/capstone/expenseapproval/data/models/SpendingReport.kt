package com.wgu.capstone.expenseapproval.data.models

import com.google.gson.annotations.SerializedName

data class SpendingReport(
    val title: String,
    val columns: List<String>,
    val rows: List<SpendingReportRow>,
)

data class SpendingReportRow(
    val date: String,
    @SerializedName("employee_id") val employeeId: String,
    val category: String,
    val amount: Double,
    val status: String,
)
