<script>
    import Profile from "./Profile.svelte";
    let chats = [
        { id: 1, name: '(조직문화부) 부서별 FAQ', lastMessage: '전자결재 문서를 수정할수 있나요?' },
        { id: 2, name: '(의료정보기획부) DW 사용법', lastMessage: '데이터 추가하는 방법은?' },
        { id: 3, name: '기타 등등 추가', lastMessage: '' },
        // Add more chat items as needed
    ];

    let user = {
        name: '신성철',
        dept_name: '의료정보기획부' // Placeholder avatar image
    };
</script>

<div class="h-screen w-64 bg-gray-800 text-white flex flex-col">
    
    <img src="/logo.png" alt="Logo" class="w-60 h-20 mx-auto mt-4 mb-8"/>
    <!--
    <div class="p-4 border-t border-gray-700">
        <button class="form-button">New Chat</button>
    </div>
    -->
    <div class="p-4 text-lg font-semibold border-b border-gray-700">일산병원 챗봇 목록</div>
    <ul class="flex-1 overflow-y-auto">
        {#each chats as chat}
            <li class="p-4 border-b border-gray-700 hover:bg-gray-700 cursor-pointer">
                <div class="font-medium">{chat.name}</div>
                <div class="text-sm text-gray-400">{chat.lastMessage}</div>
            </li>
        {/each}
    </ul>
    <Profile {user} />
</div>

<style>
    /* Custom scrollbar styling */
    ul::-webkit-scrollbar {
        width: 8px;
    }

    ul::-webkit-scrollbar-track {
        background: #2d3748; /* Gray 800 */
    }

    ul::-webkit-scrollbar-thumb {
        background-color: #4a5568; /* Gray 700 */
        border-radius: 4px;
    }
</style>
