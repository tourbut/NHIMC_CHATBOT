<script>
    import Sidebar from "$lib/components/Sidebar/Sidebar.svelte";
</script>

<main>
    <Sidebar />
    <div class="w-1/5"></div>
    <div class="flex-1">
        <slot></slot>
    </div>
    <div class="w-1/5"></div>
</main>

<style>
    main {
        display: flex;
        flex-direction: row;
        height: 100vh;
    }

    .flex-1 {
        flex: 1;
        overflow-y: auto;
    }
</style>