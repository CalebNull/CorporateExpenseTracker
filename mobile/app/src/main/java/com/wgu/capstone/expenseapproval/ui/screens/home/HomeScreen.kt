package com.wgu.capstone.expenseapproval.ui.screens.home

import androidx.compose.material3.Button
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.wgu.capstone.expenseapproval.data.auth.Session

@Composable
fun HomeScreen (
    onSubmitRequest: () -> Unit,
    onViewRequests: () -> Unit,
    onViewReports: () -> Unit,
    onLogout: () -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxWidth().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(text = "Welcome, ${Session.currentUser?.name ?: "Guest"}")
        Text(text = "Role: ${Session.currentUser?.role ?: "unknown"}")

        Button(onClick = onSubmitRequest, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Submit Expense Request")
        }
        Button(onClick = onViewRequests, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Search / View Requests")
        }
        Button(onClick = onViewReports, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Spending Reports")
        }
        Button(onClick = onLogout, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Log Out")
        }
    }
}