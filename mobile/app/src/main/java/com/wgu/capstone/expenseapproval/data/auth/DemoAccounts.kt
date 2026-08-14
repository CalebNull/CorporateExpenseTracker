package com.wgu.capstone.expenseapproval.data.auth


data class DemoAccount(
    val username: String,
    val password: String,
    val userId: String,
    val name: String,
    val email: String,
    val role: String,
)

object DemoAccounts {
    val accounts = listOf(
        DemoAccount(
            username="employee1",
            password="password",
            userId="emp1",
            name="Jamie Employee",
            email="jaimie@example.com",
            role="employee"
        ),
        DemoAccount(
            username="approver1",
            password="password",
            userId="appr1",
            name="Robin Approver",
            email="robin@example.com",
            role="approver"
        ),
        DemoAccount(
            username="finance1",
            password="password",
            userId="fin1",
            name="Alex Finance",
            email="alex@example.com",
            role="finance"
        ),
    )

    fun authenticate(
        username: String,
        password: String,
    ): DemoAccount? {
        return accounts.find { it.username == username && it.password == password }
    }
}