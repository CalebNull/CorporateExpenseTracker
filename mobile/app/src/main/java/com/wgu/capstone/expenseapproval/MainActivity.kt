package com.wgu.capstone.expenseapproval

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.wgu.capstone.expenseapproval.ui.navigation.Routes
import com.wgu.capstone.expenseapproval.ui.screens.login.LoginScreen
import com.wgu.capstone.expenseapproval.ui.theme.ExpenseApprovalAppTheme
import com.wgu.capstone.expenseapproval.ui.screens.submit.SubmitRequestScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ExpenseApprovalAppTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    AppNavHost(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}

@Composable
fun AppNavHost(modifier: Modifier = Modifier) {
    val navController: NavHostController = rememberNavController()

    NavHost(navController = navController, startDestination = Routes.LOGIN, modifier = modifier) {
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
            PlaceholderScreen("Home") { navController.navigate(Routes.SUBMIT_REQUEST) }
        }
        composable(Routes.SUBMIT_REQUEST) {
            SubmitRequestScreen(
                onSubmitted = { requestId -> navController.navigate(Routes.requestDetail(requestId)) }
            )
        }
        composable(Routes.REQUEST_LIST) { backStackEntry ->
            PlaceholderScreen("Request List") { navController.navigate(Routes.REPORTS) }
        }
        composable(Routes.REQUEST_DETAIL) { backStackEntry ->
            val requestId = backStackEntry.arguments?.getString("requestId") ?: ""
            PlaceholderScreen("Request Detail ($requestId)") { }
        }
        composable(Routes.REPORTS) {
            PlaceholderScreen("Reports") { }
        }
    }
}

@Composable
fun PlaceholderScreen(name: String, onNext: () -> Unit) {
    Text(text = "$name screen placeholder")
    Button(onClick = onNext) {
        Text("Next")
    }
}