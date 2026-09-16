import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';
import fs from 'node:fs';
import path from 'node:path';

// Parse command-line arguments (e.g., --myArgument=192.168.1.100)
const myArgumentArg = process.argv.find((arg) => arg.startsWith('--myArgument='));
if (myArgumentArg) {
	const myArgument = myArgumentArg.split('=')[1];
	process.env.PUBLIC_MYARGUMENT = myArgument;
}

const target = process.env.APP_TARGET || 'admin';
const apiTarget = `http://${process.env.PUBLIC_MYARGUMENT || '127.0.0.1'}:8090`;

export default defineConfig({
	cacheDir: `node_modules/.vite-${target}`,
	plugins: [tailwindcss(), sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: apiTarget,
				changeOrigin: true
			}
		}
	}
});


