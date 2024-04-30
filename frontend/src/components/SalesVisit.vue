<template>
    <ion-page>
    <ion-content>
    <div class=" sm:w-96 w-full flex flex-col h-screen justify-between relative">
        <div class="">
            <div class=" flex items-center justify-start sticky shadow-sm p-2">
                <router-link to="/"><FeatherIcon name="chevron-left" class="w-6 h-6" /></router-link>
            
            <span class=" font-bold text-[19px] px-2">New Field Report</span>
            </div>
            <div class="px-5 mt-7">
                <div class="">
                    <div class=" mb-3 font-semibold text-base">Meeting With</div>
                    <div>
                        <Autocomplete
                                :options="[ 
                                    {
                                    label: 'Customer',
                                    value: 'Customer',
                                },
                                {
                                    label: 'Lead',
                                    value: 'Lead',
                                },
                                ]"
                                :value="salesVisit.meeting_with"
                                @change="(e) => changeEvent(e)"
                                v-model="salesVisit.meeting_with"
                            />
                    </div>
                    <div v-if="showCustomerField" class="mt-7">
                        <div class="mb-3 font-semibold text-base">Customer</div>
                            <Autocomplete
                                :options="getCustomerNames"
                                placeholder="Customer Name"
                                v-model="salesVisit.customer"
                            />
                        </div>
                        <div v-if="showLeadField" class="mt-7">
                        <div class="mb-3 text-base">Lead Name</div>
                            <Input v-model="salesVisit.lead" type="text" placeholder="Lead Name" />
                        </div>
                    <div class="mt-7">
                        <div class="mb-3 text-base font-semibold">Meeting Details</div>
                        <Input v-model="salesVisit.meeting_details" type="textarea" class="h-[70px] w-full"  required/>
                    </div>
                    <div class="mt-7">
                        <label class="file-select">
                            <h2 class="text-base font-semibold pb-4">Attachments</h2>
                            <div class="select-button cursor-pointer">
                                <div class="flex flex-col w-full border shadow-sm items-center rounded p-3 gap-2">
                                    <FeatherIcon name="upload" class="h-6 w-6 text-gray-700" />
                                    <span class="block text-sm font-normal leading-5 text-gary-700">
                                        Upload images
                                    </span>
                                </div>
                                <input class="hidden" type="file" ref="input" multiple accept="*" @change="(e) => handleFileSelect(e)" />
                            </div>
                        </label>
                        <div v-if="selectedFiles.length" class="w-full mt-4">
                            <ul class="w-full flex fle-col items-center gap-2 mt-2"  v-for="file in selectedFiles">
                                <li class="bg-gray-100 rounded p-2 w-full" >
                                    <div class="flex flex-row items-center w-full justify-between text-gray-700 text-sm">
                                        <span class="grow cursor-pointer" @click="showPreview(file)">
                                            {{ file[0][0].name || file[0].file_name }}
                                        </span>
                                        <FeatherIcon name="x"
                                        class="h-4 w-4 cursor-pointer text-gray-700"
                                        @click="() => handleFileDelete(file)" />
                                    </div>
                                </li>
                            </ul>
                        </div>
                        <div class="h-full flex items-center justify-center bg-white shadow-sm px-4">
                            <ImagePreview class=" absolute z-10 h-full" v-if="showDialog" :file="imageFile" @close="closePreView"/>
                        </div>
                        <!-- <ion-modal
                        ref="modal"
                        :is-open="showPreviewModal"
                        @didDismiss="showPreviewModal = false"
			            >
                            <FilePreviewModal :file="previewFile" />
                        </ion-modal> -->
                    </div>
                    <div class="mt-7">
                        <div class="mb-3 text-base font-semibold">Sales Visit Type</div>
                        <div
                            class="w-full"
                            >
                            <Select
                                v-model="salesVisit.sales_visit_type"
                                placeholder="types"
                                :options="[
                                {
                                    label: 'Field Type',
                                    value: 'Field Type',
                                },
                                {
                                    label: 'Tele Calling',
                                    value: 'Tele Calling',
                                },
                                ]"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="p-2 mb-3">
            <div v-if="showError" class="text-red-800 px-3 text-[15px] font-semibold mb-3">{{ errorMessage }}</div>
            <Button v-if="showSave"  @click="save()" variant="solid" theme="gray" class="w-full p-5 mb-1">Save</Button>
            <Button v-if="createFollowUp" @click = "folloup()" variant="solid" theme="gray" class="w-full p-5 mb-1">Create Followup</Button>
            <router-link v-if="showBack" to="/"><Button variant="solid" theme="gray" class="w-full p-5 mt-3">Back</Button></router-link>
        </div>
    </div>
</ion-content>
    </ion-page>
</template>

<script setup>
import { createListResource, createResource} from 'frappe-ui';
import { Button, Input, Autocomplete, Select, Dialog } from 'frappe-ui';
import { capitalize, reactive, ref, onMounted } from 'vue';
import { FeatherIcon, toast } from 'frappe-ui'
import router from '../router';
import { computed } from 'vue';
import { IonPage, IonContent, IonModal } from '@ionic/vue';
import FilePreviewModal from './FilePreviewModal.vue';
import ImagePreview from './ImagePreview.vue';


const salesVisit = reactive({
    meeting_with: 'Customer',
    customer: Object,
    lead: '',
    meeting_details: '',
    sales_visit_type: '',
})

let selectedFiles = ref([])
let previewFile = ref({})
let showCustomerField = ref(true)
let showDialog = ref(false)
let showLeadField = ref(false)
let showError = ref(false)
let errorMessage = ref('')
let file = {}
let doc = ''
let endpoint = ''
let base64Content = ''
let createFollowUp = ref(false)
let showSave = ref(true)
let showBack = ref(false)
let showPreviewModal = ref(false)
let imageFile = ref({})
let result = ref(null)

function handleFileDelete(fileobj){
    let index = selectedFiles.value.indexOf(fileobj)
    selectedFiles.value.splice(index, 1)
    delete file[fileobj[0]['name']]
}


function handleFileSelect(ev) {
    if (!ev.target.files[0]) return;
    let file_content = ev.target.files[0]
    const reader = new FileReader();
    reader.onload = (e) => {
        result.value = e.target.result
        selectedFiles.value.push([ev.target.files, result.value])
        base64Content = reader.result.split(',')[1];
        file[ev.target.files[0]['name']] = base64Content
    };
    reader.readAsDataURL(file_content);

}

function showPreview(file) {
    console.log("showpreview", file)
    imageFile.value = file
    showDialog.value = true
    // previewFile.value = file
    // showPreviewModal.value = true
}

const uploader = createResource({
        url: "hrms.api.upload_file"
})

const customer = createListResource({
    doctype: 'Customer',
    fields: ['name'],
    auto: true,
})

customer.reload()

const salesVisitdoc = createListResource({
    doctype: 'Field Report',
})

salesVisitdoc.reload()

function changeEvent (doc) {
    salesVisit.meeting_with = doc.value
    if(doc.value == "Customer"){
        showCustomerField.value = true
        showLeadField.value = false
    }
    if(doc.value == "Lead"){
        showLeadField.value = true
        showCustomerField.value = false
    }
}

let getCustomerNames = computed(() => {
    if(salesVisit.meeting_with){
        return customer.data.map((d) => ({
        label: d.name,
        value: d.name,
    }))
    }
})

function closePreView () {
    showDialog.value = false
}

function save () {
    let missing_fields = []
    for(let i in salesVisit){
        if(Object.values(salesVisit[i]) == ''){
            missing_fields.push(capitalize(i.replaceAll('_', ' ')))
        }
    }
    if(salesVisit.meeting_with == "Customer") {
        let index = missing_fields.indexOf("Lead")
        missing_fields.splice(index, 1)
        doc = 'Customer'
        endpoint = salesVisit.customer.value
    }
    else if(salesVisit.meeting_with == "Lead") {
        let index = missing_fields.indexOf("Customer")
        missing_fields.splice(index, 1)
        doc = 'Lead'
        endpoint = salesVisit.lead
    }


    if(missing_fields.length){
        errorMessage.value = missing_fields.join(",") + " are mandatory fields"
        showError.value = true
    }
    else{
        showError.value = false
        showSave.value = false
        salesVisitdoc.insert.submit({
        meeting_with: salesVisit.meeting_with,
        customer: salesVisit.customer.value,
        lead: salesVisit.lead,
        meeting_details: salesVisit.meeting_details,
        sales_visit_type: salesVisit.sales_visit_type,
        latitude: window.location.lat,
        longitude: window.location.long
    }).then(r => {
            uploader.submit({        
                file_list: file,
                dt: 'Field Report',
                dn: r.name
            })
            showBack.value = true
            createFollowUp.value = true
            toast({
                    title: "Success",
                    text: `successful!`,
                    icon: "check-circle",
                    position: "top-right",
                    iconClasses: "text-green-500",
                })
    }).catch( (error) => {
        toast({
                    title: "Failed",
                    text: `Failed!`,
                    icon: "alert-circle",
                    position: "top-right",
                    iconClasses: "text-red-500",
                })
                showSave.value = true
    })
    
    }
}

function folloup(){
    let origin = window.location.origin
    window.location.href = `${origin}/hrms/follow-up/${doc}/${endpoint}`
}
onMounted(() => {
    navigator.geolocation.getCurrentPosition((position) => {
        window.location.lat = position.coords.latitude;
        window.location.long = position.coords.longitude;
    });
})

</script>