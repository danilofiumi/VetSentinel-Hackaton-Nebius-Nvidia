import adapter from '@sveltejs/adapter-static';

// import adapter from "svelte-adapter-bun";
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

const target = process.env.APP_TARGET || 'admin';
const outDir = process.env.OUTPUT_DIR || `../app/pb/pb_public/${target}`;

/** @type {import('@sveltejs/kit').Config} */
const config = {
    extensions: ['.svelte'],

    preprocess: [
        // commonjs() // add this line
        vitePreprocess(),
    ],
    onwarn: (warning, handler) => {
        if (warning.code.startsWith('a11y-')) return;

        if (warning.code === 'missing-exports-condition') return;
        if (warning.code === 'ownership-invalid-mutation') return;
        if (warning.code === 'a11y-no-static-element-interactions') return;
        if (warning.code === 'a11y-click-events-have-key-events') return;
        if (warning.code === 'svelte-ignore a11y-autofocus') return;
        if (warning.code.startsWith('css-unused-selector')) return;
        handler(warning);
    },

    vitePlugin: {
        inspector: {
            toggleKeyCombo: 'control-a',
            showToggleButton: 'always',
            toggleButtonPos: 'bottom-right',
        },
    },

    kit: {
        outDir: `.svelte-kit-${target}`,

        files: {
            routes: `src/apps/${target}/routes`,
        },
        alias: {
            $icons: 'node_modules/@icons-pack/svelte-simple-icons/build',
            $css: 'src/app.css',
        },
        paths: {
            relative: process.env.RELATIVE_PATHS === 'true'
        },
        appDir: 'app-content',
        adapter: adapter({
            pages: outDir,
            assets: outDir,

            fallback: 'index.html',
            precompress: false,
            strict: false,
        }),

        prerender: {
            entries: ['*'], // Pre-render all routes
            handleHttpError: ({ path, referrer, message }) => {
                // ignore deliberate link to shiny 404 page
                if (path === '/not-found-404') {
                    return;
                }

                // otherwise fail the build
                // throw new Error(message);
            },
            handleMissingId({ path }) {
                if (path === '/not-found-404') {
                    return;
                }
            },
        },
    },
};

export default config;
