<script>
    /** @type {import('./$types').PageData} */
    export let data;

    // $: ({ entries } = data);

    console.log(data);
</script>

{#if data}
    {JSON.stringify(data)}
{/if}