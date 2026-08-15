package com.wgu.capstone.expenseapproval.ui.screens.requestdetail

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.wgu.capstone.expenseapproval.data.auth.Session

@Composable
fun RequestDetailScreen(
    requestId: String,
    onDeleted: () -> Unit,
    viewModel: RequestDetailViewModel = viewModel(),
) {
    LaunchedEffect(requestId) {
        viewModel.load(requestId)
    }

    LaunchedEffect(viewModel.isDeleted) {
        if (viewModel.isDeleted) onDeleted()
    }

    val request = viewModel.request
    val role = Session.currentUser?.role

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(text = "Request Detail")

        if (viewModel.isLoading && request == null) {
            CircularProgressIndicator()
        }

        viewModel.errorMessage?.let { message ->
            Text(text = message)
        }

        request?.let {
            Text(text = "Department: ${it.department}")
            Text(text = "Category: ${it.category}")
            Text(text = "Amount: $${it.amount}")
            Text(text = "Description: ${it.description}")
            Text(text = "Status: ${it.status}")
            Text(text = "Submitted: ${it.dateSubmitted ?: "-"}")

            if (role == "approver" && it.status == "submitted") {
                Button(onClick = { viewModel.approve(requestId) }, modifier = Modifier.fillMaxWidth()) {
                    Text("Approve")
                }
                Button(onClick = { viewModel.reject(requestId) }, modifier = Modifier.fillMaxWidth()) {
                    Text("Reject")
                }
            }

            if (role == "finance" && it.status == "approved") {
                Button(onClick = { viewModel.markPaid(requestId) }, modifier = Modifier.fillMaxWidth()) {
                    Text("Mark Paid")
                }
            }

            if (role == "employee" && it.status == "submitted" && it.employeeId == Session.currentUser?.userId) {
                Button(onClick = { viewModel.delete(requestId) }, modifier = Modifier.fillMaxWidth()) {
                    Text("Delete Request")
                }
            }
        }

        Text(text = "Audit Trail")
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(viewModel.auditTrail) { entry ->
                Column {
                    Text(text = "${entry.action} by ${entry.performedBy}")
                    Text(text = entry.timestamp)
                    HorizontalDivider()
                }
            }
        }
    }
}