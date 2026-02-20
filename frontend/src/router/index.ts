import { createRouter, createWebHistory } from 'vue-router';
import SimulatorView from '../views/SimulatorView.vue';
import HelpView from '../views/HelpView.vue';
import ChangelogView from '../views/ChangelogView.vue';

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
        },
        {
            path: '/changelog',
            name: 'changelog',
            component: ChangelogView
        }
    ]
});

export default router;
