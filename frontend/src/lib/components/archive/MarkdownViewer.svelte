<script>
  import { Skeleton ,Toggle} from 'flowbite-svelte';
  import { DownloadOutline } from 'flowbite-svelte-icons';
  import { marked } from 'marked'
  export let markdown = ""
  export let orgin_data =""
  export let loading = false
  export let onclick_download;
  let is_toggle = false
</script>

{#if loading}
  <Skeleton size="xl" class="my-8" />
  <Skeleton size="xl" class="my-8" />
  <Skeleton size="xl" class="my-8" />
{:else}
<div class="flex justify-between items-center">
  {#if orgin_data}
    <Toggle bind:checked={is_toggle}>Show HTML</Toggle>
  {:else}
    <div></div>
  {/if}
  <button on:click={onclick_download} class="text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
    <DownloadOutline />
  </button>
</div>

<div class="bg-gray-50 dark:bg-gray-700 dark:text-white rounded-lg border-gray-300 dark:border-gray-700 divide-gray-300 dark:divide-gray-700 px-2 sm:px-4 py-2.5 w-full text-black">
  <div>
    {#if (is_toggle==false)}
      <div class='dark:text-white prose max-w-none'>{@html marked(markdown)}</div>
    {:else}
      <div class='dark:text-white prose max-w-none'>{orgin_data}</div>
    {/if}
  </div>
</div>
{/if}
