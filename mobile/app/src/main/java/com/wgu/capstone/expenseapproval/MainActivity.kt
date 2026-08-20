package com.wgu.capstone.expenseapproval

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.wgu.capstone.expenseapproval.data.auth.Session
import com.wgu.capstone.expenseapproval.ui.navigation.Routes
import com.wgu.capstone.expenseapproval.ui.screens.home.HomeScreen
import com.wgu.capstone.expenseapproval.ui.screens.login.LoginScreen
import com.wgu.capstone.expenseapproval.ui.screens.reports.ReportsScreen
import com.wgu.capstone.expenseapproval.ui.screens.requestdetail.RequestDetailScreen
import com.wgu.capstone.expenseapproval.ui.screens.requestlist.RequestListScreen
import com.wgu.capstone.expenseapproval.ui.screens.submit.SubmitRequestScreen
import com.wgu.capstone.expenseapproval.ui.theme.ExpenseApprovalAppTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ExpenseApprovalAppTheme {
                AppNavHost()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppNavHost() {
    val navController: NavHostController = rememberNavController()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route
    val showBackToHome = currentRoute != null && currentRoute != Routes.LOGIN && currentRoute != Routes.HOME

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            if (showBackToHome) {
                TopAppBar(
                    title = { Text("Expense Approval") },
                    navigationIcon = {
                        IconButton(onClick = {
                            navController.navigate(Routes.HOME) {
                                popUpTo(Routes.HOME) { inclusive = true }
                                launchSingleTop = true
                            }
                        }) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back to Home")
                        }
                    }
                )
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Routes.LOGIN,
            modifier = Modifier.padding(innerPadding),
        ) {
            composable(Routes.LOGIN) {
                LoginScreen(
                    onLoginSuccess = {
                        navController.navigate(Routes.HOME) {
                            popUpTo(Routes.LOGIN) { inclusive = true }
                        }
                    }
                )
            }
            composable(Routes.HOME) {
                HomeScreen(
                    onSubmitRequest = { navController.navigate(Routes.SUBMIT_REQUEST) },
                    onViewRequests = { navController.navigate(Routes.REQUEST_LIST) },
                    onViewReports = { navController.navigate(Routes.REPORTS) },
                    onLogout = {
                        Session.logOut()
                        navController.navigate(Routes.LOGIN) {
                            popUpTo(0) { inclusive = true }
                        }
                    },
                )
            }
            composable(Routes.SUBMIT_REQUEST) {
                SubmitRequestScreen(
                    onSubmitted = { requestId -> navController.navigate(Routes.requestDetail(requestId)) }
                )
            }
            composable(Routes.REQUEST_LIST) {
                RequestListScreen(
                    onRequestClick = { requestId ->
                        navController.navigate(Routes.requestDetail(requestId))
                    },
                    navController = navController,
                )
            }
            composable(Routes.REQUEST_DETAIL) { backStackEntry ->
                val requestId = backStackEntry.arguments?.getString("requestId") ?: ""
                RequestDetailScreen(
                    requestId = requestId,
                    onDeleted = {
                        navController.previousBackStackEntry?.savedStateHandle?.set("shouldRefresh", true)
                        navController.popBackStack()
                    }
                )
            }
            composable(Routes.REPORTS) {
                ReportsScreen()
            }
        }
    }
}