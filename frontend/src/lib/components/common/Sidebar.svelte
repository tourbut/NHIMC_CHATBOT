<script>
    import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper,Tooltip } from 'flowbite-svelte';
    import { P } from 'flowbite-svelte';
    import { PlusOutline,  CloseCircleSolid } from 'flowbite-svelte-icons';
    let spanClass = 'flex-1 ms-3 whitespace-nowrap';
    let is_hidden = true;
    export let side_menus = [
    { 
        category : 'Top',
        items: [
            {id:1,label: 'Home', herf: '/',caption: 'Home'},
            {id:2,label: 'About', herf: '/about',caption: 'About'},
        ]
    }];
    
    export let btn_click;
    export let btn_item_more_click;
    export let btn_add_button;
    
</script>
<div class="relative">
    <Sidebar >
        <SidebarWrapper>
            <SidebarGroup>
                {#if (btn_add_button != undefined)}
                <SidebarItem label="채팅방 생성" on:click={btn_add_button}>
                    <svelte:fragment slot="icon">
                    <PlusOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                {/if}
                {#each side_menus as menu (menu.category)}
                
                    {#each menu.items as item}
                    <div style="display: flex; align-items: center;">
                        <SidebarItem spanClass={spanClass} id={item.id} label={item.label.substring(0,18)+"..."} href={item.herf} on:click={() => {btn_click(item.id); is_hidden = true;}} />
                        <button on:click={btn_item_more_click(item.id)}>
                            <CloseCircleSolid color="#ca0001"/>
                        </button>
                    </div>
                    <Tooltip target={item.id} placement="bottom">
                        <P color="text-white-700" size="sm" weight="black">{item.label}</P>
                        {#if item.caption}
                        <P color="text-white-700" size="xs">({item.caption})</P>
                        {/if}
                    </Tooltip>
                    {/each}
                {/each}
            </SidebarGroup>
        </SidebarWrapper>
    </Sidebar>
</div>