package com.wgu.capstone.expenseapproval.ui.screens.submit

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun SubmitRequestScreen(
    onSubmitted: (String) -> Unit,
    viewModel: SubmitRequestViewModel = viewModel(),
) {
    LaunchedEffect(viewModel.submittedRequestId) {
        viewModel.submittedRequestId?.let { onSubmitted(it) }
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(text = "Submit Expense Request")

        OutlinedTextField(
            value = viewModel.department,
            onValueChange = { viewModel.department = it },
            label = { Text("Department") },
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = viewModel.category,
            onValueChange = { viewModel.category = it },
            label = { Text("Category") },
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = viewModel.amount,
            onValueChange = { viewModel.amount = it },
            label = { Text("Amount") },
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = viewModel.description,
            onValueChange = { viewModel.description = it },
            label = { Text("Description") },
            modifier = Modifier.fillMaxWidth(),
        )

        viewModel.errorMessage?.let { message ->
            Text(text = message)
        }

        if (viewModel.isSubmitting) {
            CircularProgressIndicator()
        } else {
            Button(
                onClick = { viewModel.submit() },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Submit Request")
            }
        }
    }
}