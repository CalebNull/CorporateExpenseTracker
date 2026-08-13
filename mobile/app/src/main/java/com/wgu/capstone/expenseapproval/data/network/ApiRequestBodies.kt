package com.wgu.capstone.expenseapproval.data.network

import com.google.gson.annotations.SerializedName

data class SubmitRequestBody(
    @SerializedName("employee_id") val employeeId: String,
    val department: String,
    val category: String,
    val amount: Double,
    val description: String,
)

data class DecisionBody(
    @SerializedName("approver_id") val approverId: String,
    val decision: String,
)

data class MarkPaidBody(
    @SerializedName("finance_user_id") val financeUserId: String,
)

data class DeleteRequestBody(
    @SerializedName( "employee_id") val employeeId: String
)

data class BudgetUpdateBody(
    @SerializedName("allocated_amount") val allocatedAmount: Double,
    @SerializedName("fiscal_period") val fiscalPeriod: String,
)

data class CreateUserBody(
    val role: String,
    val name: String,
    val email: String,
    val department: String,
)
