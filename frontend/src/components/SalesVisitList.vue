<template>
	<ion-page>
	<div class="w-full sm:w-96 bg-white flex flex-col items-center h-screen overflow-hidden">
		<ion-header>
		<div class="w-full sm:w-96 bg-white h-14 shadow-lg fixed top-0 z-10">
			<div class="p-2 flex pt-3">
				<FeatherIcon class="w-8 h-8 text-gray-600 hover:text-black" name="chevron-left" @click="goBack" />
				<p class="font-semibold text-xl pt-[8px] pr-2 truncate w-[10rem]">{{ title }}</p>
				<div class="w-full flex justify-end">
					<div class="p-1 pr-4">
						<FeatherIcon class="w-6 h-6 text-gray-600 hover:text-black" name="bell" />
					</div>
				</div>
			</div>
		</div>
	</ion-header>
	<ion-content>
		<div class="w-full h-[88%] flex-1 bg-gray-200 mt-14 overflow-y-auto no-scrollbar">
			<div class="p-2 h-full">
				<div class="flex bg-white p-2 rounded-lg items-center">
					<FeatherIcon name="list" class="w-5 h-5 text-gray-600" />
					<div class=" w-[10rem] ml-2">
						<Autocomplete
							:options="customer.data"
							placeholder="Customer Name"
							v-model="customer_filter"
                        />
					</div>
					<FeatherIcon name="filter" class="w-5 h-5 text-gray-600 ml-auto hover:text-black hover:cursor-pointer" @click="dialog2 = true" />
					<FeatherIcon name="refresh-ccw" class="w-5 h-5 text-gray-600 ml-[1rem] hover:text-black hover:cursor-pointer" @click="refreshData"/>
				</div>
				<div class="bg-white h-full w-full rounded-lg mt-2 p-2">
					<div class="h-full overflow-y-auto no-scrollbar">
						<div v-if="reports.length === 0" class="flex justify-center items-center h-full">
							<p class="text-gray-600 text-lg">No Report Found</p>
						</div>
						<div v-else>
							<div v-for="report in reports" :key="report.id" class="border-gray-200 border-b-[1.5px]">
								<div class="p-2 flex pt-2 items-center">
									<FeatherIcon name="file-text" class="text-gray-600 h-5 w-5" />
									<div class="flex flex-col pl-3">
										<p class="text-black truncate w-[8rem]">{{ report.name }}</p>
										<div class="flex space-x-2">
											<p class="text-gray-600 text-[10px] truncate w-[4rem]">{{ report.owner }}</p>
											<p class="text-gray-600 text-[10px] truncate w-[4rem]">{{ report.creation }}</p>
										</div>
									</div>
									<!-- <div v-if="report.amended_from_value" class="ml-auto">
										<div v-if="report.docstatus === 0" class="p-1 pl-2 pr-2 bg-red-300 rounded-xl">
											<p class="text-[12px] text-red-700">Draft</p>
										</div>
										<div v-else-if="report.docstatus === 1" class="p-1 pl-2 pr-2 bg-blue-300 rounded-xl">
											<p class="text-[12px] text-blue-700">Submitted</p>
										</div>
										<div v-else-if="report.docstatus === 2" class="p-1 pl-2 pr-2 bg-red-300 rounded-xl">
											<p class="text-[12px] text-red-700">Cancelled</p>
										</div>
									</div> -->
									<div class='touchable ml-auto' @click="handleClick(report)">
										<FeatherIcon name="arrow-right" class="text-gray-600 h-5 w-5 hover:text-black" />
									</div>
								</div>
							</div>
						</div>
					</div>
					<!-- <div class="border-gray-200 border-[1.5px] p-1 mb-2 mt-2 flex rounded-xl w-fit">
						<div class="border-r-[1.5px] border-gray-200 touchable" data-number="20" @click="printNumber(20)">
							<p class="text-[14px] pr-2 pl-2">20</p>
						</div>
						<div class="border-r-[1.5px] border-gray-200 touchable" data-number="100" @click="printNumber(100)">
							<p class="text-[14px] pr-2 pl-2">100</p>
						</div>
						<div class="touchable" data-number="500" @click="printNumber(500)">
							<p class="text-[14px] pr-2 pl-2">500</p>
						</div>
					</div> -->
				</div>
			</div>
		</div>
		<Dialog v-model="dialog2" :options="{size: 'sm'}">
			<template #body-title>
				<h1 class="font-bold text-[25px]">Filters</h1>
			</template>
			<template #body-content>
				<div class="flex p-[1rem] flex-col justify-center h-[12rem] mt-[1rem] overflow-y-auto no-scrollbar">
					<Input class="mt-2" id="from" v-model="date.from" :value="date.from" @change="(d) => {changeFromDate(d)}" type="date" label="From Date" />
					<Input class="mt-2" v-model="date.to" :value="date.to" @change="(d) => {changeToDate(d)}" type="date" label="To Date" />
					<div class="mt-2 w-full">
							<div class="mb-4 block text-sm leading-4 text-gray-700">Sales Visit Type</div>
							<Select v-model="sales_visit_type" :options="[
                                        {
                                            label: 'Field Type',
                                            value: 'Field Type',
                                        },
                                        {
                                            label: 'Tele Calling',
                                            value: 'Tele Calling',
                                        },
                                        ]" class="input-style"  />
					</div>
				</div>
			</template>
			<template #actions>
				<div class="flex border-t-[1.5px] border-gray-200 p-2">
					<Button class="ml-auto" variant="solid" @click="applyFilter()">
						Apply Filter
					</Button>
					<Button class="ml-2" @click="dialog2 = false">
						Close
					</Button>
				</div>
			</template>
		</Dialog>
	</ion-content>
	<ion-footer>
		<div class = "p-3 mb-3">
			<Button @click = "handelNew()" variant="solid" theme="gray" class="w-full p-5 mb-2">Create New Field Report</Button>
		</div>
	</ion-footer>
	</div>
	</ion-page>
</template>

<script setup>
import { IonPage, IonHeader, IonContent, IonFooter } from '@ionic/vue';
import { ref, watch, reactive } from 'vue';
import { FeatherIcon, createListResource, Dialog, TextInput,Select, Button, Autocomplete, createResource } from 'frappe-ui';
import {  useRouter } from 'vue-router';

const reports = ref([]);
const router = useRouter();
const selectedNumber = ref(20);
const dialog2 = ref(false);
// const customer = ref('');
const filters = ref([])
const sales_visit_type = ref('')
const customer_filter = ref({})

const today = new Date().toJSON().slice(0, 10)
let oneMonthBefore = new Date()
oneMonthBefore.setMonth(oneMonthBefore.getMonth() - 1)
let fromDate = oneMonthBefore.toISOString().slice(0, 10)

let date = reactive({
    from: fromDate,
    to: today,
})

function changeFromDate(d) {
    date.from = d
}

function changeToDate(d) {
    date.to = d
}

watch(customer_filter, (newCustomer) => {
	if(newCustomer){
		console.log("customer", newCustomer.label);

		filters.value = [["Field Report", "customer", "Like", `${newCustomer.label}`]]
	}
	else {
        filters.value = []
    }
	applyFilter()
})

function applyFilter() {
	console.log(filters.value);
	// Clear previous date and sales visit type filters before applying new ones
    filters.value = filters.value.filter(filter =>
        filter[1] !== "creation" && filter[1] !== "sales_visit_type"
    );

    // Add customer filter
    if (customer_filter.value && customer_filter.value.label) {
        filters.value.push(["Field Report", "customer", "Like", `${customer_filter.value.label}`]);
    }

    // Add sales visit type filter
    if (sales_visit_type.value) {
        filters.value.push(["Field Report", "sales_visit_type", "=", sales_visit_type.value]);
    }

    // Add date filter
    filters.value.push(["Field Report", "creation", "Between", [date.from, date.to]]);

    // Load data with updated filters
    loadData();

    // Close the filter dialog
    dialog2.value = false;
}

const customer = createResource({
  url: "hrms.api.get_customer",
  transform(data) {
    if(data){
      return data.map((d) => ({
        label: d.customer_name,
        value: d.customer_name + d.firm_name,
      }));
    }
    }
})

customer.reload()

const loadData = () => {

    const DocT = createResource({
        url: 'frappe.desk.reportview.get',
        method: 'POST',
        params: {
            doctype: "Field Report",
            filters: filters.value.length != 0 ? filters.value : [],
            fields: ["*"],
            distinct: false,
            start: 0,
            page_length: selectedNumber.value,
        },
    });

    DocT.fetch().then(() => {
        if (DocT.data.length === 0) {
            reports.value = [];
            return;
        }

        reports.value = DocT.data.values.map((row) => {
            const mappedItem = {};
            DocT.data.keys.forEach((key, index) => {
                mappedItem[key] = row[index];
            });

            return {
				name: mappedItem.name,
                owner: mappedItem.owner,
                creation: mappedItem.creation,
                docstatus: mappedItem.docstatus,
                meeting_with : mappedItem.meeting_with,
                customer : mappedItem.customer,
                lead : mappedItem.lead,
                meeting_details : mappedItem.meeting_details,
                sales_visit_type : mappedItem.sales_visit_type,
            };
        });
		filters.value = []
    });
};


loadData();

const handleClick = (report) => {
    console.log("report",report);

	router.push({
		name: 'SalesVisitFormView',
		query: {
			docname: report.name,
			meeting_with : report.meeting_with,
			customer : report.customer,
			lead : report.lead,
			meeting_details : report.meeting_details,
			sales_visit_type : report.sales_visit_type,
			creation : report.creation
		}
	})
};


const handelNew = () => {
	router.push({
		path: '/sales-visit/form',
	});
}

const printNumber = (number) => {
	selectedNumber.value = number;
	loadData();
};

const handleRemoveFilter = (index) => {
	filters.value.splice(index, 1);
};


const goBack = () => {
	router.push({
		path: '/'
	});
};

const refreshData = () => {
	loadData();
};

</script>
<style scoped>
.no-scrollbar::-webkit-scrollbar {
	display: none;
}

.no-scrollbar {
	-ms-overflow-style: none;
	scrollbar-width: none;
}
</style>