
const routes = [
	{
		name: "SalesVisitFormView",
		path: "/sales-visit/new",
		component: () => import("@/components/SalesVisit.vue"),
	},
	{
		name: "CustomerFormView",
		path: "/customer/new",
		component: () => import("@/components/Customer.vue"),
	},
	{
		name: "FollowupFormView",
		path: "/follow-up/:doc/:name",
		props: true,
		component: () => import("@/components/FollowUp.vue"),
	},
    {
        name: "FollowupListView",
        path: "/follow-up-list",
        component: () => import("@/components/FollowUpList.vue"),
    },
]

export default routes
