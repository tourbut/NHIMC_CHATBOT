<script>
    import { marked } from 'marked';

    export let message = {
        id: null,
        text: '',
        sender: null,
    };
</script>

<div class={`flex ${message.sender === 'me' ? 'justify-end' : 'justify-start'}`}>
    <div class={`p-3 rounded-lg max-w-xs ${message.sender === 'me' ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'} markdown-content`}>
        {@html marked(message.text)}
    </div>
</div>

<style>
    /* Custom scrollbar styling */
    .flex::-webkit-scrollbar {
        width: 8px;
    }

    .flex::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    .flex::-webkit-scrollbar-thumb {
        background: #888;
    }

    .flex::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
