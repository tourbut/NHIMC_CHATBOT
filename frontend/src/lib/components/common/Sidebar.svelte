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
    <Sidebar class="max-h-screen"> <!-- 화면 전체 높이를 최대값으로 설정 -->
        <SidebarWrapper class="h-full overflow-y-auto max-h-[calc(88vh-2rem)]"> <!-- 스크롤 가능한 영역 설정 -->
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
                    <div class="flex items-center justify-between w-full px-3">
                        <SidebarItem 
                                spanClass="w-[180px] h-[20px] overflow-hidden" 
                                id={item.id} 
                                label={item.label} 
                                href={item.herf} 
                                on:click={() => {btn_click(item.id); is_hidden = true;}}
                            />
                            <Tooltip target={item.id} placement="bottom">
                                <P color="text-white-700" size="sm" weight="black">{item.label}</P>
                                {#if item.caption}
                                    <P color="text-white-700" size="xs">({item.caption})</P>
                                {/if}
                            </Tooltip>
                        <DotsHorizontalOutline class="dots-menu dark:text-white w-6 h-6 cursor-pointer" />
                    </div>
                    <Dropdown triggeredBy=".dots-menu" class="w-[100px]">
                    <DropdownItem>공유</DropdownItem>
                    <DropdownItem slot="footer" class="text-red-600" on:click={btn_item_more_click(item.id)}>
                        삭제
                    </DropdownItem>
                    </Dropdown>
                    {/each}
                {/each}
            </SidebarGroup>
        </SidebarWrapper>
    </Sidebar>
</div>

<style>
    /* 스크롤바 스타일링 (선택사항) */
    :global(.overflow-y-auto::-webkit-scrollbar) {
        width: 4px;
    }
    
    :global(.overflow-y-auto::-webkit-scrollbar-track) {
        background: transparent;
    }
    
    :global(.overflow-y-auto::-webkit-scrollbar-thumb) {
        background: #888;
        border-radius: 2px;
    }
    
    :global(.overflow-y-auto::-webkit-scrollbar-thumb:hover) {
        background: #555;
    }
</style>