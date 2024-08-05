import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: 'Fractalistic',
    description:
        'The Terminal-Based Fractal Explorer. Fractalistic is your terminal gateway to Mandelbrot, Burning Ship, and Julia.',
    srcDir: 'src',
    appearance: 'force-dark',
    themeConfig: {
        siteTitle: "Fractalistic",
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            { text: 'Home', link: '/' },
            { text: 'Getting Started', link: '/getting-started' }
        ],
        outline: 'deep',
        footer: {
            message: 'Released under the GNU General Public License (GPLv3).',
            copyright: 'Copyright © 2021-present Léopold Koprivnik'
        },
        search: {
            provider: 'local'
        },
        editLink: {
            pattern: 'https://github.com/skwalexe/fractalistic/edit/main/docs/src/:path'
        },
        sidebar: [
            {
                text: 'Introduction',
                items: [
                    { text: '📥 Getting Started', link: '/getting-started' },
                    { text: '❗  Color Issues', link: '/color-issues' },
                    { text: '🌟 Screenshots', link: '/screenshots' }
                ]
            },
            {
                text: 'Guides',
                items: [
                    { text: '💎 General Presentation', link: '/presentation' },
                ]
            },
            {
                text: 'Development',
                items: [
                    { text: '🫂 Contributing', link: '/contributing' },
                    { text: '✅ Recommended IDE setup', link: '/recommended-ide-setup' },
                    { text: '🏗️ Project setup', link: '/project-setup' },
                    { text: '🩷 Creating a pull request', link: '/creating-a-pull-request' },
                ]
            }
        ],

        socialLinks: [{ icon: 'github', link: 'https://github.com/skwalexe/fractalistic' }]
    }
})
