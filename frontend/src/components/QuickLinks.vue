<template>
	<div class="flex flex-col gap-5 my-4 w-full">
		<div class="text-lg font-medium text-gray-900">{{ title }}</div>
		<div class="flex flex-col bg-white rounded">
			<router-link
				class="flex flex-row flex-start p-4 items-center justify-between border-b"
				v-for="link in props.items"
				:key="link.title"
				:to="{ name: link.route }"
			>
				<div class="flex flex-row items-center gap-3 grow">
					<component :is="link.icon" class="h-5 w-5 text-gray-500" />
					<div class="text-base font-normal text-gray-800">
						{{ link.title }}
					</div>
				</div>
				<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
			</router-link>
			<div  @click="salesWise()" class="flex flex-row flex-start items-center justify-between border-b p-4">				
				<div class="flex flex-row items-center gap-3 grow">
					<svg xmlns="http://www.w3.org/2000/svg"
					height="24" 
					viewBox="0 -960 960 960"
					fill="#999999"
					width="24">
					<path d="M760-400v-260L560-800 360-660v60h-80v-100l280-200 280 200v300h-80ZM560-800Zm20 160h40v-40h-40v40Zm-80 0h40v-40h-40v40Zm80 80h40v-40h-40v40Zm-80 0h40v-40h-40v40ZM280-220l278 76 238-74q-5-9-14.5-15.5T760-240H558q-27 0-43-2t-33-8l-93-31 22-78 81 27q17 5 40 8t68 4q0-11-6.5-21T578-354l-234-86h-64v220ZM40-80v-440h304q7 0 14 1.5t13 3.5l235 87q33 12 53.5 42t20.5 66h80q50 0 85 33t35 87v40L560-60l-280-78v58H40Zm80-80h80v-280h-80v280Z"/>
					</svg>
					<div class="text-base font-normal text-gray-800">Switch to Sales Wise</div>
				</div>
				<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
			</div>
		</div>
	</div>
</template>

<script setup>
import { FeatherIcon } from "frappe-ui"

const props = defineProps({
	title: {
		type: String,
		required: false,
		default: "Quick Links",
	},
	items: {
		type: Array,
		required: true,
	},
})

function salesWise() {
	let origin = window.location.origin
	window.open(`${origin}/frontend`, "__self")
}

</script>
