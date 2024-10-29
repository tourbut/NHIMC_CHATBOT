<script>
    import { Fileupload, Label, Helper } from 'flowbite-svelte';
    export let files = null;
    export let value = null;
</script>

<Label for="with_helper" class="pb-2">Upload file</Label>
<Fileupload id="with_helper" class="mb-2" bind:files ={files} bind:value={value} />
<Helper>지원형식: txt, PDF, xlsx, csv</Helper>