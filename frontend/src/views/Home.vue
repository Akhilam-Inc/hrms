<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col items-center my-7 p-4 gap-7">
				<CheckInPanel />
				<QuickLinks :items="quickLinks" title="Quick Links" />
				<RequestPanel />
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { markRaw } from "vue"

import CheckInPanel from "@/components/CheckInPanel.vue"
import QuickLinks from "@/components/QuickLinks.vue"
import BaseLayout from "@/components/BaseLayout.vue"
import RequestPanel from "@/components/RequestPanel.vue"
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"
import EmployeeAdvanceIcon from "@/components/icons/EmployeeAdvanceIcon.vue"
import SalaryIcon from "@/components/icons/SalaryIcon.vue"
import RequestIcon from "@/components/icons/RequestIcon.vue"
import SalesVisitIcon from "@/components/icons/SalesVisitIcon.vue"

const quickLinks = [
	{
		icon: markRaw(LeaveIcon),
		title: "Leave Application",
		route: "LeaveApplicationFormView",
	},
	{
		icon: markRaw(ExpenseIcon),
		title: "Expense Claim",
		route: "ExpenseClaimFormView",
	},
	{
		icon: markRaw(SalaryIcon),
		title: "View Salary Slips",
		route: "SalarySlipsDashboard",
	},
	{
		icon: markRaw(RequestIcon),
		title: "Request Form",
		route: "RequestForm",
	},
	{
		icon: markRaw(SalesVisitIcon),
		title: "Field Report",
        route: "SalesVisitListView",
	},
	{
		icon: markRaw(SalesVisitIcon),
		title: "Customer",
        route: "CustomerFormView",
	},

]
</script>
