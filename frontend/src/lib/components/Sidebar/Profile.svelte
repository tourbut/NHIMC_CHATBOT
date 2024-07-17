<script>

    export let user; 
    let showMenu = false;
    function toggleMenu() {
        showMenu = !showMenu;
    }
</script>

<div class="p-4 flex items-center border-t border-gray-700">
    <div>
        <div class="font-medium">{user.dept_name}</div>
        <div class="font-medium">{user.name}</div>
    </div>
    <button class="ml-auto" on:click={toggleMenu}>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 12h12M6 6h12M6 18h12" />
        </svg>
    </button>

    {#if showMenu}
        <div class="fixed bottom-20 left-5 w-48 bg-white rounded-md shadow-lg py-1 z-20">
            <a href="/" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Profile</a>
            <a href="/" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Settings</a>
            <a href="/" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Logout</a>
        </div>
    {/if}
</div>

<style>
    /* Adjust the style to your liking */
    .relative {
        position: relative;
    }
</style>