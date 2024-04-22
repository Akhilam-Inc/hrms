const route = [
    {
        name: "RequestForm",
        path: "/request-form/new",
        component: () => import("../views/request_form/Form.vue")
    },
    {
        name: "RequestList",
        path: "/dashboard/request-list",
        component: () => import("../views/request_form/List.vue")
        // component: () => import("@/views/request_form/List.vue")
    },
]
export default route