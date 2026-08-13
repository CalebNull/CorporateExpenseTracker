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
import com.wgu.capstone.expenseapproval.ui.theme.ExpenseApprovalAppTheme

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

    NavHost(navController = navController, startDestination = Routes.HOME, modifier = modifier) {
        composable(Routes.HOME) {
            PlaceholderScreen("Home") { navController.navigate(Routes.SUBMIT_REQUEST) }
        }
        composable(Routes.SUBMIT_REQUEST) {
            PlaceholderScreen("Submit Request") { navController.navigate(Routes.REQUEST_LIST) }
        }
        composable(Routes.REQUEST_LIST) {
            PlaceholderScreen("Request List") { navController.navigate(Routes.REPORTS) }
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