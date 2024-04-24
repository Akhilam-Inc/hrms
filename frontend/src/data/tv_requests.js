import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"
import { reactive } from "vue"

export const teamTVRequests = createResource({
	url: "hrms.api.get_tv_requests",
	params: {
		employee: employeeResource.data.name,
		approver_id: employeeResource.data.user_id,
		for_approval: 1,
		limit: 5,
	},
	auto: true,
	cache: "hrms:team_requests",
	transform(data) {
		return transformClaimData(data)
	},
})