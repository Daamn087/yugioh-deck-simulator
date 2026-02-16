import { createRouter, createWebHistory } from 'vue-router';
import SimulatorView from '../views/SimulatorView.vue';
import HelpView from '../views/HelpView.vue';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'simulator',
            component: SimulatorView
        },
        {
            path: '/docs-faq',
            name: 'docs',
            component: HelpView
        }
    ]
});

export default router;
