package com.wgu.capstone.expenseapproval.ui.screens.reports

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.wgu.capstone.expenseapproval.data.models.SpendingReportRow

@Composable
fun ReportsScreen(
    viewModel: ReportsViewModel = viewModel(),
) {
    Column(
        modifier = Modifier.fillMaxWidth(). padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(text = "Spending Report")

        OutlinedTextField(
            value = viewModel.department,
            onValueChange = { viewModel.department = it },
            label = { Text("Department") },
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = viewModel.startDate,
            onValueChange = { viewModel.startDate = it },
            label = { Text("Start Date (YYYY-MM-DD)") },
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = viewModel.endDate,
            onValueChange = { viewModel.endDate = it },
            label = { Text("End Date (YYYY-MM-DD)") },
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = { viewModel.generateReport() },
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(text = "Generate Report")
        }

        viewModel.errorMessage?.let { message ->
            Text(text = message)
        }

        if (viewModel.isLoading) {
            CircularProgressIndicator()
        }

        viewModel.report?.let { report ->
            Text(text = report.title)

            Row(modifier = Modifier.fillMaxWidth()) {
                report.columns.forEach { column ->
                    Text(text = column, modifier = Modifier.weight(1f))
                }
            }
            HorizontalDivider()

            LazyColumn(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                items(report.rows) { row: SpendingReportRow ->
                    Row(modifier = Modifier.fillMaxWidth()) {
                        Text(text = row.date, modifier = Modifier.weight(1f))
                        Text(text = row.employeeId, modifier = Modifier.weight(1f))
                        Text(text = row.category, modifier = Modifier.weight(1f))
                        Text(text = "${row.amount}", modifier = Modifier.weight(1f))
                        Text(text = row.status, modifier = Modifier.weight(1f))
                    }
                }
            }
        }
    }
}