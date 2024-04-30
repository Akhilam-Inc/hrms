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
			<router-link :to="route" class="flex flex-row flex-start p-4 items-center justify-between border-b">
				<div class="flex flex-row items-center gap-3 grow">
					<!-- <component :is="" class="h-5 w-5 text-gray-500" /> -->
					<FollowUpIcon class="h-5 w-5 text-gray-500"/>
					<div class="text-base font-normal text-gray-800">
						Followup
					</div>
				</div>
				<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
			</router-link>
		</div>
	</div>
</template>

<script setup>
import { FeatherIcon } from "frappe-ui"
import Button from "frappe-ui/src/components/Button.vue";
import FollowUpIcon from "./icons/FollowUpIcon.vue";

let doc = 'follow-up'
let name = 'new'

let route = `/follow-up/${doc}/${name}`

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

const followup = () => {
	let origin = window.location.origin
	window.location.href = origin + `hrms/follow-up/${doc}/${name}`
}


</script>
