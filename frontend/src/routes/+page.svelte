<script>
  import { username } from '$lib/stores';
  import { goto } from '$app/navigation';
</script>
{#if $username}
  <div class="container mx-auto p-4 max-w-md">
    <h1>{$username}님 반갑습니다.</h1>
  </div>
{:else}
  <div class="container mx-auto p-4 max-w-md">
    {goto('/login')}
  </div>
{/if}
