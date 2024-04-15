<template>
	<ion-page>
		<ion-content>
		<div class=" flex flex-col justify-between sm:w-96 h-screen">
			<div class="">
				<div class="flex items-center justify-between px-3 py-4 shadow-sm">
					<div class="flex">
						<router-link to="/"><FeatherIcon name="chevron-left" class="h-7 w-7 mr-2" /></router-link><div class="text-[17px] font-semibold">Request Form List</div>
					</div>
					<div>
						<Popover>
							<template #target="{ togglePopover }">
								<Button @click="togglePopover()">
								<FeatherIcon name="filter" class="w-5 h-5 font-semibold" />
								</Button>
							</template>
							<template #body-main>
								<div class="p-2 flex flex-col justify-center gap-1">
								<Input class="mb-2" id="from" v-model="date.from" :value="date.from" @change="(d) => {changeFromDate(d)}" type="date" label="From Date" /> <Input v-model="date.to" :value="date.to" @change="(d) => {changeToDate(d)}" type="date" label="To Date" /><Button class="mt-3" variant="solid" @click="dateFilter()">Apply Filter</Button>
								</div>
							</template>
						</Popover>
					</div>
				</div>
				<div v-if="requestForm.data" class=" px-2">
					<div v-for="data in requestForm.data" :key="data.name" class="flex border cursor-pointer rounded-sm mt-3" @click="showDocument(data)">
						<div class="flex justify-between items-center w-full p-2">
							<div class="flex items-center">
								<div>
									<component :is="documentIcon" class="w-6 h-6" />
								</div>
								<div class="ml-3">
									<div class="text-[15px] text-gray-900 font-bold">{{ data.name }}</div>
									<div class="text-[15px]  text-gray-900 font-medium">From Date: <span class="ml-4 text-gray-700"> {{ data.from_date }}</span></div>
									<div class="text-[15px]  text-gray-900 font-medium">To Date: <span class="ml-4 text-gray-700"> {{ data.to_date }}</span></div>
									<div class="text-[14px] w-[180px] text-gray-900 font-semibold" >{{ data.reason }}</div>
								</div>
							</div>
							<div>
								<FeatherIcon name="chevron-right" class="w-5 h-5 text-gray-600" />
							</div>
						</div>
					</div>
					<!-- <div v-if="showDoc" class=""> -->
							<Dialog v-model="showDoc">
							<template #body-title>
								<div class="text-center w-full">
								<h3 class=" font-bold text-[18px]">Request Form</h3>
								</div>
							</template>
							<template #body-content>
								<div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">ID</div><div class="text-[15px]  text-gray-900">{{ document.name }}</div></div>
								<div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">Employee</div><div class="text-[15px]  text-gray-900">{{ document.employee }}</div></div>
								<div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">Employee Name</div><div class="ml-4 text-gray-900">{{ document.employee_name }}</div></div>
								<div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">From Date</div><div class="ml-4 text-gray-900">{{ document.from_date }}</div></div>
								<div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">To Date</div><div class="ml-4 text-gray-900">{{ document.to_date }}</div></div>
								<div class="flex justify-between mb-2" v-if="document.half_day"><div class="text-[15px] text-gray-500 font-semibold">Half Day Date</div><div class="ml-4 text-gray-900">{{ document.half_day_date }}</div></div>
								<div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">Reason</div><div class="ml-4 text-gray-900">{{ document.reason }}</div></div>
								<div class="">
									<div class="text-[15px] text-gray-500 font-semibold mb-1">Ex[planation</div>
									<div class="text-[14px] text-gray-900">{{ document.explanation }}</div>
								</div>
							</template>
							</Dialog>
					<!-- </div> -->
				</div>
				<div v-if="!requestForm.data.length" class=" mt-80 text-center flex justify-center items-center">
					<div class="text-gray-500">No Request Form Found</div>
				</div>
			</div>
			<div class="sticky bottom-0 bg-white border border-t-2">
				<BottomTabs />
			</div>
		</div>
		</ion-content>
	</ion-page>
</template>
<script setup>
import { IonPage, IonContent } from "@ionic/vue";
import BottomTabs from "../../components/BottomTabs.vue"
import { createListResource, createResource } from 'frappe-ui'
import { FeatherIcon, Dialog, Popover, Input, toast } from 'frappe-ui'
import { computed, markRaw, reactive, ref } from 'vue';
import DocumentIcon from '../../components/icons/DocumentIcon.vue';
import { session } from '../../data/session';

let showDoc = ref(false)
let document = ref({})
const documentIcon = markRaw(DocumentIcon)
const today = new Date().toJSON().slice(0, 10)
let oneMonthBefore = new Date()
oneMonthBefore.setMonth(oneMonthBefore.getMonth() + 1)
let fromDate = oneMonthBefore.toISOString().slice(0, 10)

let date = reactive({
	from: today,
	to: fromDate,
})

const requestForm = createResource({
		url: "frappe.desk.reportview.get",
		params: {"doctype":"Request Form",
				"fields":["`tabRequest Form`.name","`tabRequest Form`.from_date","`tabRequest Form`.to_date","`tabRequest Form`.half_day_date","`tabRequest Form`.reason", "`tabRequest Form`.explanation", "`tabRequest Form`.half_day", "`tabRequest Form`.employee", "`tabRequest Form`.employee_name"],
				"group_by":"`tabRequest Form`.name","order_by":"`tabRequest Form`.modified desc","page_length":100,"start":0,
				"filters": [["Request Form", "from_date", "Between", [date.from, date.to]], ["Request Form", "owner", "=", session.user]],
			},
		transform(data) {
			if (data.length === 0) {
				return []
			}
			let transformData = []
			// convert keys and values arrays to docs object
			const fields = data["keys"]
			const values = data["values"]
			const docs = values.map((value) => {
				const doc = {}
				fields.forEach((field, index) => {
					doc[field] = value[index]
				})
				transformData.push(doc)
			})
			return transformData
	},
})

requestForm.reload()


function changeFromDate(d) {
	date.from = d
}

function changeToDate(d) {
	date.to = d
}

function dateFilter () {
	if(date.from <= date.to) {
		requestForm.update({
			params: {"doctype":"Request Form",
				"fields":["`tabRequest Form`.name","`tabRequest Form`.from_date","`tabRequest Form`.to_date","`tabRequest Form`.half_day_date","`tabRequest Form`.reason", "`tabRequest Form`.explanation", "`tabRequest Form`.half_day", "`tabRequest Form`.employee", "`tabRequest Form`.employee_name"],
				"group_by":"`tabRequest Form`.name","order_by":"`tabRequest Form`.modified desc","page_length":100,"start":0,
				"filters": [["Request Form", "from_date", "Between", [date.from, date.to]], ["Request Form", "owner", "=", session.user]],
			},
	});
	requestForm.reload()
	}
	else {
		toast({
					title: "Invalid Date",
					text: `From Date must be less than To Date!`,
					icon: "alert-circle",
					position: "bottom-right",
					iconClasses: "text-red-500",
				})
	}
}

function showDocument (doc) {
	showDoc.value = true
	document.value = doc
}

</script>