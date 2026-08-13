package com.wgu.capstone.expenseapproval.data.models

import com.google.gson.annotations.SerializedName

data class User(
    @SerializedName("user_id") val userId: String,
    val name: String,
    val email: String,
    val department: String,
    val role: String,
)
