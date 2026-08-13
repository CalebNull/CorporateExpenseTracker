package com.wgu.capstone.expenseapproval.data.models

import com.google.gson.annotations.SerializedName

data class AuditLogEntry(
    @SerializedName("audit_id") val auditId: String,
    @SerializedName("request_id") val requestId: String,
    val action: String,
    @SerializedName("performed_by") val performedBy: String,
    val details: String,
    val timestamp: String,
)
