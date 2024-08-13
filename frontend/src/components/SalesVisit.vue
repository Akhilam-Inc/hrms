<template>
    <ion-page>
        <div class=" sm:w-96 w-full flex flex-col h-screen justify-between relative">
            <ion-content>
                <div class="">
                    <div class=" flex items-center justify-start sticky shadow-sm p-2">
                        <!-- <router-link to="/sales"><FeatherIcon name="chevron-left" class="w-6 h-6" /></router-link> -->
                        <FeatherIcon name="chevron-left" class="w-6 h-6" @click = "router.back()"/>
                    <span class=" font-bold text-[19px] px-2">Field Report</span>
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
                                        :disabled="!canEdit"
                                    />
                            </div>
                            <div v-if="showCustomerField" class="mt-7">
                                <div class="mb-3 font-semibold text-base">Customer</div>
                                    <Autocomplete
                                        :options="customer.data"
                                        placeholder="Customer Name"
                                        v-model="salesVisit.customer"
                                        :disabled="!canEdit"
                                    />
                                </div>
                                <div v-if="showLeadField" class="mt-7">
                                <div class="mb-3 text-base">Lead Name</div>
                                    <Input v-model="salesVisit.lead" type="text" placeholder="Lead Name" :disabled="!canEdit"/>
                                </div>
                                <div class="mt-7">
                                <div class="mb-3 text-base font-semibold">Sales Visit Type</div>
                                <div
                                    class="w-full"
                                    >
                                    <Select
                                        v-model="salesVisit.sales_visit_type"
                                        placeholder="types"
                                        :disabled="!canEdit"
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

                                <div class="mt-7">
                                <div class="mb-3 text-base font-semibold">Meeting Details</div>
                                <Input v-model="salesVisit.meeting_details" type="textarea" class="h-[70px] w-full"  required :disabled="!canEdit"/>
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
                                        <!-- <input class="hidden" type="file" ref="input" multiple accept="*" @change="(e) => handleFileSelect(e)" /> -->
                                        <input class="hidden" type="file" ref="cameraInput" accept="image/*" capture="environment" @change="(e) => handleFileSelect(e)" :disabled="!canEdit"/>
                                    </div>
                                    <div v-if="salesVisit.sales_visit_type === 'Tele Calling'" class="select-button cursor-pointer">
                                        <div class="flex flex-col w-full border shadow-sm items-center rounded p-3 gap-2">
                                            <FeatherIcon name="upload" class="h-6 w-6 text-gray-700" />
                                            <span class="block text-sm font-normal leading-5 text-gary-700">
                                                Upload from gallery
                                            </span>
                                        </div>
                                        <!-- <input class="hidden" type="file" ref="input" multiple accept="*" @change="(e) => handleFileSelect(e)" /> -->
                                        <input class="hidden" type="file" ref="galleryInput" accept="*" @change="(e) => handleFileSelect(e)" :disabled="!canEdit"/>
                                    </div>
                                </label>
                                <div v-if="selectedFiles.length" class="w-full mt-4">
                                    <ul class="w-full flex fle-col items-center gap-2 mt-2"  v-for="file in selectedFiles">
                                        <li class="bg-gray-100 rounded p-2 w-full" >
                                            <div class="flex flex-row items-center w-full justify-between text-gray-700 text-sm">
                                                <span class="grow cursor-pointer" @click="showPreview(file)">
                                                    {{ file[0][0].name || file[0][0].file_name }}
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

                        </div>
                    </div>
                </div>
            </ion-content>
            <ion-footer>
                <!-- Attachment upload -->
                <div
                    class="flex flex-row gap-2 items-center justify-center p-5"
                    v-if="isFileUploading"
                >
                    <LoadingIndicator class="w-3 h-3 text-gray-800" />
                    <span class="text-gray-900 text-sm">Uploading...</span>
                </div>
                <div class="p-2 mb-3">
                    <!-- <LoadingIndicator>Loading...</LoadingIndicator> -->
                    <div v-if="showWarning" class="text-red-800 px-3 text-[15px] font-semibold mb-3">{{ WarningMessage }}</div>
                    <div v-if="showError" class="text-red-800 px-3 text-[15px] font-semibold mb-3">{{ errorMessage }}</div>
                    <Button v-if="showSave"  @click="save()" variant="solid" theme="gray" class="w-full p-5 mb-1">Save</Button>
                    <Button v-if="showUpdate"  @click="update()" variant="solid" theme="gray" class="w-full p-5 mb-1">Update</Button>
                    <div v-if="!canEdit" class="text-red-800 text-[15px] font-semibold text-center my-3">
                        Editing is disabled as the allowed time window has passed.
                    </div>
                    <Button v-if="createFollowUp" @click = "folloup()" variant="solid" theme="gray" class="w-full p-5 mb-1">Create Followup</Button>
                    <router-link v-if="showBack" to="/"><Button variant="solid" theme="gray" class="w-full p-5 mt-3">Back</Button></router-link>
                </div>
            </ion-footer>
        </div>
    </ion-page>
</template>

<script setup>
import { createListResource, createResource, createDocumentResource} from 'frappe-ui';
import { Button, Input, Autocomplete, Select, Dialog, LoadingIndicator } from 'frappe-ui';
import { capitalize, reactive, ref, onMounted } from 'vue';
import { FeatherIcon, toast } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
import { IonPage, IonContent, IonModal, IonFooter } from '@ionic/vue';
import FilePreviewModal from './FilePreviewModal.vue';
import ImagePreview from './ImagePreview.vue';

const route = useRoute();
const router = useRouter();

const salesVisit = reactive({
    docname : route.query.docname || '',
    meeting_with: route.query.meeting_with || '',
    customer: route.query.customer || Object,
    lead: route.query.lead || '',
    meeting_details: route.query.meeting_details || '',
    sales_visit_type: route.query.sales_visit_type || '',
    creation: route.query.creation || '',
})

let selectedFiles = ref([])
let previewFile = ref({})
let showCustomerField = ref(true)
let showDialog = ref(false)
let showLeadField = ref(false)
let showError = ref(false)
let showWarning = ref(false)
let WarningMessage = ref('')
let errorMessage = ref('')
let file = {}
let files = {}
let deletedFiles = []
let doc = ''
let endpoint = ''
let base64Content = ''
let createFollowUp = ref(false)
let showSave = ref(true)
let showUpdate = ref(false)
let showBack = ref(false)
let showPreviewModal = ref(false)
let imageFile = ref({})
let result = ref(null)
let isFileUploading = ref(false)
let isFormView = ref(false)
let imageUrl= ''
let canEdit = ref(true);
const creationTime = ref(new Date())


function handleFileDelete(fileobj){
    console.log("fileobj", fileobj);

    let index = selectedFiles.value.indexOf(fileobj)
    selectedFiles.value.splice(index, 1)
    deletedFiles.push(fileobj[0][0]['name'])
    delete file[fileobj[0][0]['name']]
    console.log("deleteFiles",deletedFiles);
}

// function handleFileSelect(ev) {
//     isFileUploading.value = true
//     if (!ev.target.files[0]) return;
//     let file_content = ev.target.files[0]
//     const reader = new FileReader();
//     reader.onload = (e) => {
//         result.value = e.target.result
//         selectedFiles.value.push([ev.target.files, result.value])
//         base64Content = reader.result.split(',')[1];
//         file[ev.target.files[0]['name']] = base64Content
//     };
//     reader.readAsDataURL(file_content);
//     isFileUploading.value = false
//     console.log("SelectedFile", selectedFiles.value);

// }

const routeBack = () => {
	router.push({
		path: '/sales-visit'
	});
};

function handleFileSelect (ev) {
    isFileUploading.value = true;
    if (!ev.target.files[0]) return;

    const fileContent = ev.target.files[0];
    const reader = new FileReader();

    reader.onload = (e) => {
        const base64Content = e.target.result.split(',')[1];
        selectedFiles.value.push([
            [ev.target.files[0]],
            e.target.result,
        ]);

        // Storing base64 content in a separate object for quick access by file name
        file[ev.target.files[0]['name']] = base64Content;
        console.log("SelectedFile", selectedFiles.value);
    };

    reader.readAsDataURL(fileContent);
    isFileUploading.value = false;
};

function showPreview(file) {
    console.log("showpreview", file)
    imageFile.value = file
    showDialog.value = true
    // previewFile.value = file
    // showPreviewModal.value = true
}

const fileAttachments = createResource({
    url: "hrms.api.get_attachments",
    params: {
        dt: "Field Report",
        dn: salesVisit.docname,
    },
    transform(data) {
        return data.map((file) => {
            file.uploaded = true;
            return file;
        });
    },
    onSuccess(data) {
        console.log("onSuccess", data);

        data.forEach((file) => {
            if (file.file_url) {
                files[file.file_name] = file.name
                const url = new URL(window.location.href);
                const imageUrl = `${url.protocol}//${url.hostname}:8014${file.file_url}`;

                getBase64FromImageUrl(imageUrl).then((base64Image) => {
                    const base64Content = base64Image.split(',')[1];
                    selectedFiles.value.push([
                    [
                        {
                            name: file.file_name
                        }
                    ],
                    base64Image,
                    ]);
                });
            }
        });

        console.log("AttachedFile after onSuccess", selectedFiles.value);
    },
});

fileAttachments.reload()

// console.log("attachedFiles...", attachedFiles);

async function getBase64FromImageUrl(imageUrl) {
    try {
        // Fetch the image from the URL
        const response = await fetch(imageUrl);

        // Ensure the response is OK
        if (!response.ok) {
            throw new Error('Failed to fetch image');
        }

        // Convert the response to a Blob
        const blob = await response.blob();

        // Create a FileReader to read the Blob as base64
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            // Handle the load event to get the base64 string
            reader.onloadend = () => resolve(reader.result);

            // Handle errors
            reader.onerror = reject;

            // Read the Blob as a Data URL (base64)
            reader.readAsDataURL(blob);
        });
    } catch (error) {
        console.error('Error converting image to base64:', error);
        return null;
    }
}


const uploader = createResource({
        url: "hrms.api.upload_file"
})

const deleteFile = createResource({
        url: "hrms.api.delete_attachment"
})

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

const salesVisitdoc = createListResource({
    doctype: 'Field Report',
})

const updateSalesVisit = createDocumentResource({
    doctype : 'Field Report',
    name : salesVisit.docname
})

salesVisitdoc.reload()

function update () {
    isFileUploading.value = true
    updateSalesVisit.setValue.submit({
        meeting_with: salesVisit.meeting_with,
        customer: salesVisit.customer.label,
        lead: salesVisit.lead,
        meeting_details: salesVisit.meeting_details,
        sales_visit_type: salesVisit.sales_visit_type,
        latitude: window.location.lat,
        longitude: window.location.long
    }).then(() => {
        uploader.submit({
                file_list: file,
                dt: 'Field Report',
                dn: salesVisit.name
            })
        if (deletedFiles.length) {
            deletedFiles.forEach((f) => {
                console.log("filename", f);

                deleteFile.submit({
                    filename : files[f]
                })
            })
        }
        isFileUploading.value = false
        toast({
                    title: "Success",
                    text: `Updated Document`,
                    icon: "check-circle",
                    position: "top-right",
                    iconClasses: "text-green-500",
                })
    }).catch((e) => {
        console.log("cathch", e);

        toast({
                    title: "Failed",
                    text: `Update Failed!`,
                    icon: "alert-circle",
                    position: "top-right",
                    iconClasses: "text-red-500",
                })
                showUpdate.value = true
    })

}

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



function closePreView () {
    showDialog.value = false
}

function save () {
    isFileUploading.value = true

    if(selectedFiles.value.length == 0){
        alert("To create field report you must have to click photo and upload!")
        return
    }
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
        endpoint = salesVisit.customer.label
    }
    else if(salesVisit.meeting_with == "Lead") {
        let index = missing_fields.indexOf("Customer")
        missing_fields.splice(index, 1)
        doc = 'Lead'
        endpoint = salesVisit.lead
    }

    if(window.location.lat == undefined || window.location.long == undefined){
        showWarning.value = true
        WarningMessage.value = "Report is created without location. Please enable location."
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
            customer: salesVisit.customer.label,
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
            isFileUploading.value = false
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
        isFileUploading.value = false
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
    if (route.query.docname) {
        isFormView.value = true
        showSave.value = false
        showUpdate.value = true
        console.log("creation", salesVisit.creation);
        creationTime.value = new Date(salesVisit.creation || new Date());
        // Check if the document is editable
        checkEditPermission();
        setInterval(checkEditPermission, 1000 * 60);
    }


    navigator.geolocation.getCurrentPosition((position) => {
        window.location.lat = position.coords.latitude;
        window.location.long = position.coords.longitude;
    });
})

function checkEditPermission() {
    const currentTime = new Date();
    const timeDifference = Math.abs(currentTime - creationTime.value);
    const differenceInHours = timeDifference / (1000 * 60 * 60);

    console.log("differenceInHours", differenceInHours);


    if (differenceInHours > 1) {
        canEdit.value = false;
        showUpdate.value = false;
    } else {
        canEdit.value = true;
        showUpdate.value = true;
    }
}

</script>