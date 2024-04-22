<template>
	<ion-page>
		<ion-header>
			<div>
				<div class=" shadow-sm h-[60px] sm:w-96 flex items-center bg-white">
					<Button class="text-[40px]" variant="ghost" ><FeatherIcon name="chevron-left" @click="router.back()" class="h-6 w-6 text-black"  /></Button>
					<span class=" font-bold text-[20px]">Request Form</span>
				</div>
			</div>
		</ion-header>
		<ion-content  :fullscreen="true">
			<div class="main-div w-full h-full sm:w-96">
				<div class=" flex h-full flex-col justify-between">
					<div class="">
						<div class=" h-full mt-10 mx-3 relative-div">
							<div class=" w-full">
								<div class="mb-3 font-medium text-[14px]">Employee</div>
								<Input disabled v-model="requestForm.employee" class="" type="text" />
							</div>
							<div class="mt-4 w-full">
								<div class="mb-3 font-medium text-[14px]">Employee Name</div>
								<Input disabled v-model="requestForm.employee_name" type="text" class=" w-full" />
							</div>
							<div class="mt-4 w-full">
								<div class="mb-3 font-medium text-[14px]">Company</div>
								<Input disabled v-model="requestForm.company" type="text" class=" w-full" />
							</div>
							<div class="mt-4 w-full">
								<div class="mb-3 font-medium text-[14px]">From Date</div>
								<Input v-model="requestForm.from_date" type="date" class=" w-full" />
							</div>
							<div class="mt-4 w-full">
								<div class="mb-3 font-medium text-[14px]">To Date</div>
								<Input type="date" v-model="requestForm.to_date" :min="requestForm.from_date" class=" w-full" />
							</div>
							<div class="mt-4">
								<Checkbox v-model="requestForm.half_day" size="sm" label="Half Day" />
							</div>
							<div v-if="showHalfDayDate" class="mt-3 w-full">
								<div class="mb-3 font-medium text-[14px]">Half Day Date</div>
								<Input type="date" v-model="requestForm.half_day_date" :min="requestForm.from_date" :max="requestForm.to_date" class=" w-full" />
							</div>
							<div class="mt-4 w-full">
								<div class="mb-3 font-medium text-[14px]">Reason</div>
								<Select v-model="requestForm.reason" :options="options" class="input-style" />
							</div>
							<div class="mt-4 w-full">
								<div class="mb-3 font-medium text-[14px]">Explanation</div>
								<Input v-model="requestForm.explanation" type="textarea" :min="requestForm.from_date" :max="requestForm.to_date"  class=" h-[100px] w-full input-style" />
							</div>
						</div>
					</div>
					<div class="w-full sm:w-96 p-3 fixed bottom-0 shadow-sm bg-white">
					<div v-if="showError" class="text-red-800 px-3 text-[15px] font-semibold mb-3">{{ errorMessage }}</div>
						<Button @click="save" variant="solid" theme="gray" size="lg" class=" w-full  text-white font-bold btn-style">Save</Button>
					</div>
				</div>
			</div>
		</ion-content>
	</Ion-Page>
</template>
<script setup>
import { IonPage, IonContent, IonHeader } from "@ionic/vue"
import { createListResource, FeatherIcon, Button, Input, Select, Checkbox, toast } from 'frappe-ui'
import { ref, watch, inject, computed, reactive } from "vue"
import router from "../../router";
import { capitalize } from "eslint-plugin-vue/lib/utils/casing";

let showHalfDayDate = ref(false)
const employee = inject("$employee")
let showError = ref(false)
let errorMessage = ref('')

let requestForm = reactive({
	employee: employee.data.name,
	employee_name: employee.data.employee_name,
	company: employee.data.company,
	from_date: "",
	to_date: "",
	half_day: false,
	half_day_date: "",
	reason: "",
	explanation: "",
})

let options = [
	{
		label: 'Mispunch',
		value: 'Mispunch',
	},
	{
		label: 'Leave Related',
		value: 'Leave Related',
	},
	{
		label: 'Difference In Salary',
		value: 'Difference In Salary',
	},
	{
		label: 'Claim Related',
		value: 'Claim Related',
	},
	{
		label: 'Travel Advance',
		value: 'Travel Advance',
	},
	{
		label: 'Outdoor Duty',
		value: 'Outdoor Duty',
	},
	{
		label: 'Over Time',
		value: 'Over Time',
	},
	{
		label: 'Compensatory Leave',
		value: 'Compensatory Leave',
	},]


watch( () => requestForm.half_day,
		(half_day) => setHalfDayDate(half_day))

function setHalfDayDate (half_day) {
	if(half_day){
		showHalfDayDate.value = true
		if(requestForm.from_date === requestForm.to_date) {
			requestForm.half_day_date = requestForm.from_date
		}
	}
	else{
		showHalfDayDate.value = false
	}
}

const requestFormList = createListResource({
	doctype: 'Request Form',
})
requestFormList.reload()


function save() {
	let missingFields = []
	
	for(let i in requestForm){
		if(Object.values(requestForm[i]) == ""){
			missingFields.push(capitalize(i.replaceAll("_", " ")))
		}
	}
	if(requestForm.half_day == false){
		let index = missingFields.indexOf("Half day")
		missingFields.splice(index, 2)
		console.log("Missing", missingFields, index)
	}
	else{
		let index = missingFields.indexOf("Half day")
		missingFields.splice(index, 1)
		console.log("Missing", missingFields, index)
	}

	if(missingFields.length){
		errorMessage.value = missingFields.join(",") + " are mandatory fields"
		showError.value = true
	}
	else{
		showError.value = false
		requestFormList.insert.submit(requestForm).then(r => {
			toast({
			title: "Success",
			text: `successful!`,
			icon: "check-circle",
			position: "top-right",
			iconClasses: "text-green-500",
		})
		let origin = window.location.origin
		window.location.href = `${origin}/hrms/home`
		})
	}
}
</script>
<style>
.input-style {
	border: 1px solid rgb(216, 214, 214);
	border-radius: 5px;
	background-color: rgb(240, 238, 238);
}

.input-style:focus{
	border: 1px solid rgb(196, 194, 194);
}

</style>