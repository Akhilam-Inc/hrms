<template>
  <ion-page>
    <div class="flex flex-col h-full w-fullte">
      <div class="w-full h-screen sm:w-96 flex flex-col justify-between overflow-y-auto">
          <ion-header>
            <header class="flex flex-row shadow-sm py-4 px-5 items-center border-b sticky top-0 z-[1000]">
              <router-link to="/"><FeatherIcon name="chevron-left" class="h-5 w-5" /></router-link>

            <h2 class="text-2xl font-semibold text-gray-900 px-2">
              Follow Up
            </h2>
          </header>
          </ion-header>
          <ion-content  :fullscreen="true">
            <div class="hidden">{{ checkDoc }}</div>
              <div class="grow px-3">
                <div v-if="showCustomerField" class="mt-7">
                  <div class=" text-base font-semibold mb-3">Customer Name</div>
                  <div class="">
                    <Autocomplete
                      :options="customer.data"
                      v-model="ToDo.custom_customer"
                    />
                  </div>
                </div>
                <div v-if="showLeadField" class="mt-7">
                  <div class=" text-base font-semibold mb-3">Lead Name</div>
                  <Input v-model="ToDo.custom_lead" class="" type="text" />
                </div>
                <div class="mt-7">
                  <div class="text-base font-semibold mb-3">Followup Date</div>
                  <Input v-model="ToDo.date" class="" type="date" />
                </div>
                <div class="mt-7">
                  <div class="text-base font-semibold mb-3">Followup Description</div>
                  <Input v-model="ToDo.description" class=" h-20" type="textarea" />
                </div>
            </div>
          </ion-content>
          <ion-footer>
            <div class="flex justify-end mb-5 px-3">
              <Button @click="CreateToDo()" class="w-full  rounded mt-2 p-5 text-base text-white" :variant="'solid'" theme="gray">
                Create Followup
              </Button>
            </div>
          </ion-footer>
      </div>
    </div>
  </ion-page>
  </template>

<script setup>
import { IonPage, IonHeader, IonContent, IonFooter } from '@ionic/vue';
import { FeatherIcon, Input, createListResource, Autocomplete, createResource} from 'frappe-ui'
import router from '../router';
import { reactive, computed, ref } from 'vue';
import { session } from '../data/session';

// const toast = useToast();
let showCustomerField = ref(true)
let showLeadField = ref(true)
let customerName = ref('')
let leadName = ref('')

let props = defineProps(['name', 'doc'])

let checkDoc = computed(() => {
  if(props.doc == 'Customer'){
    showLeadField.value = false
    ToDo.custom_customer = {"label": props.name, "value": props.name}
    return props.name
  }
  else if(props.doc == 'Lead'){
    showCustomerField.value = false
    ToDo.custom_lead = props.name
    return props.name
  }
  else if(props.doc == 'new'){
    return props.name = ''
  }

})

let ToDo = reactive({
    custom_customer: Object,
    custom_lead: '',
    date: '',
    description: '',
    allocated_to: session.user,
    assigned_by: session.user
})

const ToDoDocType = createListResource({
    doctype: 'ToDo',
    onSuccess: (data) => {
    }
})

ToDoDocType.reload()

const customer = createResource({
  url: "hrms.api.get_customer",
  transform(data) {
    if(data){
      return data.map((d) => ({
        label: d,
        value: d,
      }));
    }
    }
})

customer.reload()


const CreateToDo = () => {
      ToDoDocType.insert.submit({
                  custom_customer: ToDo.custom_customer.value,
                  custom_lead: ToDo.custom_lead,
                  date: ToDo.date,
                  description: ToDo.description,
                  allocated_to: session.user,
                  assigned_by: session.user
      }).then(response => {
              let origin = window.location.origin
              window.location.href = origin + "/hrms"

      })
}

  </script>
