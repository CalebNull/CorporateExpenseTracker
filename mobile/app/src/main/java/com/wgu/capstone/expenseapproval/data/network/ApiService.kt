package com.wgu.capstone.expenseapproval.data.network

import com.wgu.capstone.expenseapproval.data.models.AuditLogEntry
import com.wgu.capstone.expenseapproval.data.models.Budget
import com.wgu.capstone.expenseapproval.data.models.ExpenseRequest
import com.wgu.capstone.expenseapproval.data.models.SpendingReport
import com.wgu.capstone.expenseapproval.data.models.User
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.HTTP
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    @POST("requests")
    suspend fun submitRequest(@Body body: SubmitRequestBody): ExpenseRequest

    @GET("requests/{request_id}")
    suspend fun getRequest(@Path("request_id") requestId: String): ExpenseRequest

    @GET("requests")
    suspend fun searchRequests(
        @Query("employee_id") employeeId: String? = null,
        @Query("status") status: String? = null,
        @Query("department") department: String? = null,
    ): List<ExpenseRequest>

    @PUT("requests/{request_id}/decision")
    suspend fun decisionRequest(
        @Path("request_id") requestId: String,
        @Body body: DecisionBody,
    ): ExpenseRequest

    @PUT("requests/{request_id}/pay")
    suspend fun markPaid(
        @Path("request_id") requestId: String,
        @Body body: MarkPaidBody,
    ): ExpenseRequest

    @HTTP(method = "DELETE", path = "requests/{request_id}", hasBody = true)
    suspend fun deleteRequest(
        @Path("request_id") requestId: String,
        @Body body: DeleteRequestBody,
    )

    @GET("requests/{request_id}/audit")
    suspend fun getAuditTrail(@Path("request_id") requestId: String): List<AuditLogEntry>

    @GET("budgets/{department}/{category}")
    suspend fun getBudget(
        @Path("department") department: String,
        @Path("category") category: String,
    ): Budget

    @GET("budgets")
    suspend fun listBudgets(@Query("department") department: String): List<Budget>

    @PUT("budgets/{department}/{category}")
    suspend fun updateBudget(
        @Path("department") department: String,
        @Path("category") category: String,
        @Body body: BudgetUpdateBody,
    ): Budget

    @GET("users/{user_id}")
    suspend fun getUser(@Path("user_id") userId: String): User

    @POST("users")
    suspend fun createUser(@Body body: CreateUserBody): User

    @GET("reports/spending")
    suspend fun getSpendingReports(
        @Query("department") department: String,
        @Query("start") start: String,
        @Query("end") end: String,
    ): SpendingReport
}