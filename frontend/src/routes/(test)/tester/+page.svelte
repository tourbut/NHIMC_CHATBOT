<script>
    let messages = [
        { id: 1, text: 'Hello!', sender: 'other' },
        { id: 2, text: 'Hi, how are you?', sender: 'me' },
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
        if (event.key === 'Enter') {
            sendMessage();
        }
    }
</script>

<div class="h-screen flex flex-col">
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
        {#each messages as message}
            <div class={`flex ${message.sender === 'me' ? 'justify-end' : 'justify-start'}`}>
                <div class={`p-3 rounded-lg max-w-xs ${message.sender === 'me' ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'}`}>
                    {message.text}
                </div>
            </div>
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
