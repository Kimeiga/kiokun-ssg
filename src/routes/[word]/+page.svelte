<script lang="ts">
	// import { onMount } from 'svelte';
	// import pako from 'pako';

	/** @type {import('./$types').PageData} */
	export let data;

	console.log(data);

	// let decompressedData: any = null;

	// async function fetchAndDecompress(url: string) {
	// 	try {
	// 		const response = await fetch(url);
	// 		if (!response.ok) {
	// 			throw new Error(`HTTP error! status: ${response.status}`);
	// 		}
	// 		const compressedData = await response.arrayBuffer();
	// 		if (!compressedData) {
	// 			throw new Error('No data received from server');
	// 		}
	// 		const decompressedString = pako.inflate(new Uint8Array(compressedData), { to: 'string' });
	// 		return JSON.parse(decompressedString);
	// 	} catch (error) {
	// 		console.error('Error in fetchAndDecompress:', error);
	// 		throw error;
	// 	}
	// }

	// onMount(async () => {
	// 	try {
	// 		if (!data?.url) {
	// 			throw new Error('URL is undefined');
	// 		}
	// 		decompressedData = await fetchAndDecompress(data.url);
	// 	} catch (error) {
	// 		console.error('Error decompressing data:', error);
	// 		decompressedData = { error: error.message };
	// 	}
	// });
</script>

{#if data}
	<pre>{JSON.stringify(data, null, 2)}</pre>
{:else}
	<p>Loading...</p>
{/if}
