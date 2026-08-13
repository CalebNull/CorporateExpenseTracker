package com.wgu.capstone.expenseapproval.data.models

import com.google.gson.annotations.SerializedName

data class Budget(
    val department: String,
    val category: String,
    @SerializedName("allocated_amount") val allocatedAmount: Double,
    @SerializedName("spent_amount") val spentAmount: Double,
    @SerializedName("fiscal_period") val fiscalPeriod: String,
)
