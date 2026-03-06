import { createRouter, createWebHistory } from 'vue-router'
import CafeList from '../views/CafeList.vue'
import CafeDetail from '../views/CafeDetail.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: CafeList
        },
        {
            path: '/cafe/:id',
            name: 'cafe-detail',
            component: CafeDetail
        }
    ]
})

export default router
