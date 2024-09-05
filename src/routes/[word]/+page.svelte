<script>
    import { onMount } from 'svelte';
    import pako from 'pako';

    /** @type {import('./$types').PageData} */
    export let data;

    let decompressedData = null;

    async function fetchAndDecompress(url) {
        const response = await fetch(url);
        const compressedData = await response.arrayBuffer();
        const decompressedString = pako.inflate(new Uint8Array(compressedData), { to: 'string' });
        return JSON.parse(decompressedString);
    }

    onMount(async () => {
        try {
            decompressedData = await fetchAndDecompress(data.url);
        } catch (error) {
            console.error('Error decompressing data:', error);
        }
    });
</script>

{#if decompressedData}
    {JSON.stringify(decompressedData)}
{:else}
    Loading...
{/if}