<template>
    <!-- <ion-modal> -->
        <div class=" mb-52 py-5 shadow-2xl sha bg-white mt-24 rounded-sm main-div">
            <div class="flex justify-between mb-3 text-[17px]">
                <span class="px-3">{{ fileName }} - Image Preview</span><Button variant="gost" class="text-blue-800 font-semibold" @click="close">close</Button>
            </div>
            <img :src="props.file[1]" class="image-preview h-auto w-full" />
        </div>
    <!-- </ion-modal> -->
</template>

<script setup>
import { computed, ref } from "vue"
import { IonModal } from "@ionic/vue";

let dialog = ref(true)
let emits = defineEmits("close")

let props = defineProps({
    file: {
        type: Object,
        required: true
    }
})

const fileName = computed(() => {
    return props.file[0][0].file_name || props.file[0][0].name
})


function close () {
    emits("close")
    dialog.value = false
}
</script>
<style>
.image-preview {
    image-orientation: from-image;
}



@keyframes ScrollInUp {
    from {
        transform: translateY(500px);
    }

    to {
        transform: translateY(0);
    }
}
@keyframes ScrollInDown {
    from {
        transform: translateY(0);
    }

    to {
        transform: translateY(500px);
    }
}
.main-div {
    animation: ScrollInUp .5s 0s 1 normal none;
}

</style>