<script>
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger} from 'flowbite-svelte';
    import { Dropdown, DropdownItem, DropdownDivider} from 'flowbite-svelte';
    import { ChevronDownOutline } from 'flowbite-svelte-icons';
    import { APP_NAME,username,user_token,is_admin } from '$lib/stores';
    import { DarkMode } from 'flowbite-svelte';
    const logout = async () => {
        username.set("");
        user_token.set("");
    }
    let fluid = false;
</script>
<Navbar {fluid} class="text-black" rounded color="form" let:NavContainer>
    <NavContainer class="mb-px mt-px px-1" {fluid}>
    <NavBrand href="/">
        <img src="/logo.png" class="me-3" alt="국민건강보험 일산병원" />
        <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">{$APP_NAME}</span>
    </NavBrand>
    <NavHamburger  />
    <NavUl >
        <NavLi href="/">Home</NavLi>
        {#if $username}
        <NavLi href="/chat">Chat</NavLi>
        <NavLi class="cursor-pointer">
            Settings<ChevronDownOutline class="w-6 h-6 ms-2 text-primary-800 dark:text-white inline" />
        </NavLi>    
        <Dropdown class="w-44 z-20">
            <!-- <DropdownItem href="/detail">개인정보</DropdownItem> -->
            <DropdownItem href="/llms">LLM설정</DropdownItem>
            <DropdownItem href="/usage">사용량조회</DropdownItem>
            <DropdownDivider />
            {#if $is_admin}
            <DropdownItem href="/admin">Admin</DropdownItem>
            <DropdownItem href="/archive">FileUpload</DropdownItem>
            {/if}
            <DropdownItem on:click={logout}>Logout</DropdownItem>
        </Dropdown>
        {/if}
    </NavUl>
    <div class="ms-auto flex items-center text-gray-500 dark:text-gray-400 sm:order-2">
        <DarkMode class="text-primary-500 dark:text-primary-600 border dark:border-gray-800" />
    </div>
    </NavContainer>
</Navbar>

