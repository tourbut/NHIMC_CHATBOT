<script>
    import Message from "./Messages/Message.svelte";
    let messages = [
        { id: 1, text: "안녕하세요~! **무엇이든** 물어보세요.", sender: 'bot' },
        { id: 2, text: '전자결재가 완료된 문서를 수정할 수 있나요?', sender: 'me' },
        { id: 3, text: '**아니요.** \n\n 전자결재가 완료된 문서는 원칙상 수정이 불가하며, 수정한 내용의 문서를 재작성하여 결재를 받아야 합니다.\n\n (의료정보기획부_FAQ)', sender: 'bot' },
        // Add more messages as needed
    ];
    let newMessage = '';

    function sendMessage() {
        if (newMessage.trim() !== '') {
            messages.push({ id: messages.length + 1, text: newMessage, sender: 'me' });
            newMessage = '';
        }
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter' && event.shiftKey === false) {
            sendMessage();
        }
    }
</script>

<div class="h-screen flex flex-col">
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
        {#each messages as message}
            <Message {message} />
        {/each}
    </div>
    <div class="p-4 border-t border-gray-300 flex items-center">
        <input
            type="text"
            bind:value={newMessage}
            class="flex-1 p-2 border border-gray-300 rounded-l-lg focus:outline-none"
            placeholder="Type your message..."
            on:keypress={handleKeyPress}
        />
        <button
            class="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-r-lg"
            on:click={sendMessage}
        >
            Send
        </button>
    </div>
</div>

<style>
    /* Custom scrollbar styling */
    .flex-1::-webkit-scrollbar {
        width: 8px;
    }

    .flex-1::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .flex-1::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }

    .flex-1::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
