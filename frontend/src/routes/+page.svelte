<script>
  import { username, dept_nm } from '$lib/stores';
  import { goto } from '$app/navigation';
  import { P } from 'flowbite-svelte';
</script>
{#if $username}
  <div class="container mx-auto p-4 max-w-md">
    <P>{$dept_nm} {$username}님 반갑습니다.</P>
  </div>
{:else}
  <div class="container mx-auto p-4 max-w-md">
    {goto('/login')}
  </div>
{/if}
