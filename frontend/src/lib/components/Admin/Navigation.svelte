<script>
    export let menus = [
      { name: "Home", href: "/" },
      { name: "사용자관리", href: "/" },
      { name: "채팅관리", href: "/" },
      { name: "파일관리", href: "/" },
      { name: "프롬프트관리", href: "/" },
      { name: "사용량조회", href: "/" }
    ];
</script>
  
<nav class="bg-gray-800 p-4">
    <div class="container mx-auto flex justify-between items-center">
        <div class="space-x-4">
        {#each menus as menu}
            <a href={menu.href} class="text-white hover:text-gray-400">
            {menu.name}
            </a>
        {/each}
        </div>
    </div>
</nav>