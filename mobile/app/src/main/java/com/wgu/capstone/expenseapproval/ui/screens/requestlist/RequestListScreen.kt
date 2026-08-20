package com.wgu.capstone.expenseapproval.ui.screens.requestlist

import androidx.compose.foundation.clickable
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import com.wgu.capstone.expenseapproval.data.models.ExpenseRequest

@Composable
fun RequestListScreen(
    onRequestClick: (String) -> Unit,
    navController: NavHostController,
    viewModel: RequestListViewModel = viewModel(),
) {
    val shouldRefresh = navController.currentBackStackEntry?.savedStateHandle?.get<Boolean>("shouldRefresh")

    LaunchedEffect(shouldRefresh) {
        if (shouldRefresh == true) {
            viewModel.search()
            navController.currentBackStackEntry?.savedStateHandle?.set("shouldRefresh", false)
        }
    }

    Column(
        modifier = Modifier.fillMaxWidth().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(text = "Search Requests")

        OutlinedTextField(
            value = viewModel.employeeIdFilter,
            onValueChange = { viewModel.employeeIdFilter = it },
            label = { Text("Employee ID") },
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = viewModel.statusFilter,
            onValueChange = { viewModel.statusFilter = it },
            label = { Text("Status") },
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = viewModel.departmentFilter,
            onValueChange = { viewModel.departmentFilter = it },
            label = { Text("Department") },
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = { viewModel.search() },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Search")
        }

        viewModel.errorMessage?.let { message ->
            Text(text = message)
        }

        if (viewModel.isLoading) {
            CircularProgressIndicator()
        } else {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(viewModel.results) { request ->
                    RequestRow(request = request, onClick = {
                        onRequestClick(request.requestId)
                    })
                }
            }
        }
    }
}

@Composable
fun RequestRow(request: ExpenseRequest, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(8.dp),
    ) {
        Text(text = "${request.category} - ${request.department}")
        Text(text = "$${request.amount} - ${request.status}")
        HorizontalDivider()
    }
}