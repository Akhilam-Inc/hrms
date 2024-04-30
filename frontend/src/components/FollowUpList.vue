<template>
    <ion-page>
        <div class=" flex flex-col justify-between sm:w-96 h-screen">
            <div class="h-full">
                <ion-header>
                        <div class="flex items-center justify-between px-3 py-4 shadow-sm">
                        <div class="flex">
                            <router-link to="/"><FeatherIcon name="chevron-left" class="h-7 w-7 mr-2" /></router-link><div class="text-[17px] font-semibold">Follow Up List</div>
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
                </ion-header>
                <ion-content :fullscreen="true">
                    <div v-if="followUp" class=" px-2">
                        <div v-for="data in followUp.data" :key="data.name" class="flex border cursor-pointer rounded-sm mt-3" @click="showDocument(data)">
                            <div class="flex justify-between items-center w-full p-2">
                                <div class="flex items-center">
                                    <div>
                                        <component :is="documentIcon" class="w-6 h-6" />
                                    </div>
                                    <div class="ml-3">
                                        <div class="text-[15px] text-gray-900">{{ data.name }}</div>
                                        <div class="text-[15px]  text-gray-900">{{ data.custom_customer || data.custom_lead }} <span class="ml-4 text-gray-700">{{ data.date }}</span></div>
                                        <div class="description text-[14px] w-[180px] text-gray-500" v-html="data.description"></div>
                                    </div>
                                </div>
                                <div>
                                    <FeatherIcon name="chevron-right" class="w-5 h-5 text-gray-600" />
                                </div>
                            </div>
                        </div>
                        <Dialog v-model="showDoc">
                        <template #body-title>
                            <div class="text-center w-full">
                            <h3 class=" font-bold text-[18px]">Follow Up</h3>
                            </div>
                        </template>
                        <template #body-content>
                            <div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">ID</div><div class="text-[15px]  text-gray-900">{{ document.name }}</div></div>
                            <div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">Status</div><div class="text-[15px]  text-gray-900">{{ document.status }}</div></div>
                            <div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">Name</div><div class="text-[15px]  text-gray-900">{{ document.custom_customer || document.custom_lead }}</div></div>
                            <div class="flex justify-between mb-2"><div class="text-[15px] text-gray-500 font-semibold">Date</div><div class="ml-4 text-gray-900">{{ document.date }}</div></div>
                            <div class="">
                                <div class="text-[15px] text-gray-500 font-semibold mb-1">Description</div>
                                <div class="text-[14px] text-gray-900" v-html="document.description"></div>
                                <Button class="w-full mt-5" @click="[changeStatus(document.name), showDoc = false]" variant="solid" theme="red" size="lg">Close</Button>
                            </div>
                        </template>
                        </Dialog>
                    </div>
                    <div class="h-full flex justify-center items-center" v-if="isEmpty">
                        No Followup Found
                    </div>
                </ion-content>
            </div>
        </div>
    </ion-page>
</template>
<script setup>
import { IonPage, IonHeader, IonContent, IonFooter } from '@ionic/vue';
import { createListResource, createResource } from 'frappe-ui'
import { FeatherIcon, Dialog, Popover, Input, toast, Button } from 'frappe-ui'
import { computed, markRaw, reactive, ref } from 'vue';
import DocumentIcon from './icons/DocumentIcon.vue';
import { session } from '../data/session';

let showDoc = ref(false)
let document = ref({})
const documentIcon = markRaw(DocumentIcon)
const today = new Date().toJSON().slice(0, 10)
let oneMonthBefore = new Date()
let isEmpty = ref(false)
oneMonthBefore.setMonth(oneMonthBefore.getMonth() - 1)
let fromDate = oneMonthBefore.toISOString().slice(0, 10)

let date = reactive({
    from: fromDate,
    to: today,
})

let followUp = createResource({
        url: "frappe.desk.reportview.get",
        params: {"doctype":"ToDo",
                "fields":["`tabToDo`.name","`tabToDo`.date","`tabToDo`.description","`tabToDo`.custom_customer","`tabToDo`.custom_lead", "`tabToDo`.status"],
                "group_by":"`tabToDo`.name","order_by":"`tabToDo`.modified desc","page_length":100,"start":0,
                "filters":  [["ToDo","date","Between",[date.from , date.to ]], ["ToDo", "owner", "=", session.user], ["ToDo", "status", "=", "Open"]],
            },
        transform(data){
            let transformData = []
            if(data){
                if(data.length == 0) {
                    isEmpty.value = true;
                    return []
                }
            }
            data.values?.map(valuesArray => {
                    const obj = {};
                    data?.keys?.forEach((key, index) => {
                    obj[key] = valuesArray[index];
                    });
                transformData.push(obj);
                });
            return transformData
        }
})

followUp.reload()

let datas = computed(() => {
    
})

function changeFromDate(d) {
    date.from = d
}

function changeToDate(d) {
    date.to = d
}

function changeStatus (name) {
    console.log(name, "change statsus")
    todo.setValue.submit({
        name: name,
        status: "Closed",
    }).then((r) => {
        location.reload()
    })
}

let todo = createListResource({
    doctype: "ToDo",
})

function dateFilter () {
    if(date.from <= date.to) {
        followUp.update({
        params: {"doctype":"ToDo",
                "fields":["`tabToDo`.name","`tabToDo`.date","`tabToDo`.description","`tabToDo`.custom_customer","`tabToDo`.custom_lead"],
                "group_by":"`tabToDo`.name","order_by":"`tabToDo`.modified desc","page_length":100,"start":0,
                "filters":  [["ToDo","date","Between",[date.from, date.to ]], ["ToDo", "owner", "=", session.user]],
            },
    });
    followUp.reload()
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
<style>
.description {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

</style>