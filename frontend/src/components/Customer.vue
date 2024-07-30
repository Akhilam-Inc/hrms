<template>
	<ion-page>
		<div class="flex flex-col h-full w-full">
			<div class="w-full h-screen sm:w-96 flex flex-col justify-between overflow-y-auto">
				<ion-header>
					<header class="flex flex-row shadow-sm py-4 px-3 items-center border-b sticky top-0 z-[1000]">
						<Button @click="router.back()" variant="ghost" class="!pl-0">
							<FeatherIcon name="chevron-left" class="h-5 w-5" />
						</Button>

						<h2 class="text-2xl font-semibold text-gray-900">
							Create Customer
						</h2>
					</header>
				</ion-header>
				<ion-content  :fullscreen="true">
					<div class="grow px-5">
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
				</ion-content>
				<ion-footer>
					<div class="flex justify-end px-3 mb-5">
						<Button @click="savecustomer()" class="w-full  rounded mt-2 p-5 text-base text-white" :variant="'solid'" theme="gray">
							Save
						</Button>
					</div>
				</ion-footer>
			</div>
		</div>
	</ion-page>
</template>

<script setup>
import { IonPage, IonHeader, IonContent, IonFooter } from '@ionic/vue';
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
		url: "hrms.api.create_customer"
})


function savecustomer(){
	if (customer.custom_phone && !validatePhoneNumber(customer.custom_phone)) {
		alert("Invalid phone number");
		return;
	}
	if (customer.custom_gst_number && !validateGSTNumber(customer.custom_gst_number)) {
		alert("Invalid GST number");
        return;
	}
	createCustomer.submit({
		customer
	}).then( r => {
            let origin = window.location.origin
            window.location.href = origin + "/hrms"
    })
}

function validateGSTNumber(gstNumber) {
	console.log(gstNumber)
        const gstRegex = /^([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1})$/;
        if (!gstRegex.test(gstNumber)) {
            return false;
        }
        return true;
    }

function validatePhoneNumber(phoneNumber) {
	console.log(phoneNumber)
	if (phoneNumber.length !== 10) {
		return false;
	}else{
		return true;
	}
}

</script>