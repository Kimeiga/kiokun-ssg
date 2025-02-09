import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		sveltekit(),
		{
			name: 'build-time',
			buildStart() {
				console.time('build-time');
			},
			buildEnd() {
				console.timeEnd('build-time');
			}
		}
	],
	server: {
		fs: {
			allow: ['..', './dictionary'] // This allows serving files from one level up, which includes your public folder
		}
	}
});
