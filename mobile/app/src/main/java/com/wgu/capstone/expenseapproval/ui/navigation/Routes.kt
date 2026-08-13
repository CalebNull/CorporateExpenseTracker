package com.wgu.capstone.expenseapproval.ui.navigation

object Routes {
    const val HOME = "home"
    const val SUBMIT_REQUEST = "submit_request"
    const val REQUEST_LIST = "request_list"
    const val REQUEST_DETAIL = "request_detail/{requestId}"
    const val REPORTS = "reports"

    fun requestDetail(requestId: String) = "request_detail/$requestId"
}