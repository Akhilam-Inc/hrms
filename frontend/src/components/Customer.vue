<template>
	<div class="flex flex-col h-full w-full">
		<div class="w-full h-screen bg-white sm:w-96 flex flex-col justify-between overflow-y-auto">
			<div>
				<header class="flex flex-row bg-white shadow-sm py-4 px-3 items-center border-b sticky top-0 z-[1000]">
				<Button @click="router.back()" variant="ghost" class="!pl-0 hover:bg-white">
					<FeatherIcon name="chevron-left" class="h-5 w-5" />
				  </Button>

				<h2 class="text-2xl font-semibold text-gray-900">
					Create Customer
				</h2>
			</header>
			<div class="bg-white grow px-5">
				<div class="mt-7">
					<div class=" text-base font-semibold mb-3">Firm Name</div>
					<Input v-model="customer.custom_firm_name" type="text" />
				</div>
				<div class="mt-7">
					<div class="text-base font-semibold mb-3">Owner Name</div>
					<Input v-model="customer.customer_name" type="text" />

				</div>
				<div class="mt-7">
					<div class="text-base font-semibold mb-3">Email Address</div>
					<Input v-model="customer.custom_email_address" type="email" />
				</div>
				<div class="mt-7">
					<div class="text-base font-semibold mb-3">Phone</div>
					<Input v-model="customer.custom_phone"  type="number" />
				</div>
				<div class="mt-7">
					<div class="text-base font-semibold mb-3">GST Number</div>
					<Input v-model="customer.custom_gst_number" type="text" />
				</div>
				<div class="mt-7">
					<div class="text-base font-semibold mb-3">City</div>
					<Input v-model="customer.custom_city" type="text" />
				</div>
			</div>
			</div>
			

			<div class="flex justify-end px-3 mb-5">
				<Button @click="savecustomer()" class="w-full  rounded mt-2 p-5 text-base text-white" :variant="'solid'" theme="gray">
					Save
				</Button>

			</div>
		</div>
	</div>
</template>

<script setup>
import { FeatherIcon, Input, createListResource, createResource } from 'frappe-ui'
import router from '../router';
import { reactive } from 'vue';

let customer = reactive({
	customer_name: '',
	custom_firm_name: '',
	custom_email_address: '',
	custom_phone: null,
	custom_gst_number: '',
	custom_city: '',
})

const customerDocType = createListResource({
	doctype: 'Customer',
	fields: ["name", "customer_type", "customer_group"],
	limit: 10,
})

customerDocType.reload()

const createCustomer = createResource({
		url: "saleswise.api.create_customer"
})


function savecustomer(){
	createCustomer.submit({        
		customer
	}).then( r => {
            let origin = window.location.origin
            window.location.href = origin + "/saleswise"
    })
}

</script>