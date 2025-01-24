<script>
    import { Sidebar, SidebarGroup, SidebarItem, SidebarWrapper,Tooltip } from 'flowbite-svelte';
    import { Button, Dropdown, DropdownItem, ToolbarButton, DropdownDivider } from 'flowbite-svelte';
    import { DotsHorizontalOutline, DotsVerticalOutline } from 'flowbite-svelte-icons';
    import { P } from 'flowbite-svelte';
    import { PlusOutline,  CloseCircleSolid } from 'flowbite-svelte-icons';
    let is_hidden = true;
    export let side_menus = [
    { 
        category : 'Top',
        items: [
            {id:1,label: 'Home', herf: '/',caption: 'Home'},
            {id:2,label: 'About', herf: '/about',caption: 'About'},
        ]
    }];
    export let create_btn_name='채팅방 생성';
    export let btn_click;
    export let btn_item_more_click;
    export let btn_add_button;
    
</script>
<div class="relative">
    <Sidebar >
        <SidebarWrapper>
            <SidebarGroup>
                {#if (btn_add_button != undefined)}
                <SidebarItem label={create_btn_name} on:click={btn_add_button}>
                    <svelte:fragment slot="icon">
                    <PlusOutline class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" />
                    </svelte:fragment>
                </SidebarItem>
                {/if}
                {#each side_menus as menu (menu.category)}
                
                    {#each menu.items as item}
                    <div style="display: flex; align-items: center;">
                        <SidebarItem id={item.id} label={item.label.substring(0,18)+"..."} href={item.herf} 
                                     on:click={() => {btn_click(item.id); is_hidden = true;}} />
                        <DotsHorizontalOutline class="dots-menu dark:text-white" />
                        <Dropdown triggeredBy=".dots-menu">
                        <DropdownItem>공유</DropdownItem>
                        <DropdownItem slot="footer" class="text-red-600" on:click={btn_item_more_click(item.id)}>
                            삭제
                        </DropdownItem>
                        </Dropdown>
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