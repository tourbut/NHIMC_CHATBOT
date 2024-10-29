<script>
  import { Toast } from 'flowbite-svelte';
  import { ExclamationCircleSolid,CloseCircleSolid,CheckCircleSolid } from 'flowbite-svelte-icons';
  import { toasts } from '$lib/stores';
  import { removeToast } from '$lib/common.js';

  function handleDismiss(id) {
    removeToast(id);
  }

  let lastToast;

  $: {
    if ($toasts) {
      if ($toasts.length > 0) {
        lastToast = $toasts[$toasts.length - 1];
        setTimeout(() => removeToast(lastToast.id), 5000);
      }
    }
  }

</script>
{#if $toasts}
<div class="toasts">
  {#each $toasts as toast (toast.id)}
    {#if toast.category == 'warning'}
      <Toast color="red" on:close={handleDismiss(toast.id)}>
          <svelte:fragment slot="icon">
          <ExclamationCircleSolid class="w-5 h-5" />
          <span class="sr-only">Warning icon</span>
          </svelte:fragment>
        {toast.message}
      </Toast>
      {:else if toast.category == 'error'}
      <Toast color="red" on:close={handleDismiss(toast.id)}>
        <svelte:fragment slot="icon">
          <CloseCircleSolid class="w-5 h-5" />
          <span class="sr-only">Error icon</span>
        </svelte:fragment>
        {toast.message}
      </Toast>
      {:else}
      <Toast color="green" on:close={handleDismiss(toast.id)}>
        <svelte:fragment slot="icon">
          <CheckCircleSolid class="w-5 h-5" />
          <span class="sr-only">Check icon</span>
        </svelte:fragment>
        {toast.message}
      </Toast>
    {/if}
  {/each}
</div>
{/if}