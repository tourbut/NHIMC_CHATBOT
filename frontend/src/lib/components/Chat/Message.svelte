<script>
    import { marked } from 'marked'
    import { Popover, P, A } from 'flowbite-svelte';
    import { LightbulbOutline, ClipboardOutline} from 'flowbite-svelte-icons';
    
    export let message = {
        id: '1',
        name: 'Jese',
        addtional_info: 'addtional_info',
        msg: 'Hello, how can I help you?',
        time: '2024.02.20. 14:30:22',
        is_user: true
    }

    function copyToClipboard() {
    const messageText = document.getElementById(message.id).innerText;
    navigator.clipboard.writeText(messageText).then(() => {
        alert('Message copied to clipboard!');
    }).catch(err => {
        console.error('Could not copy text: ', err);
    });
}
</script>

{#if message.is_user}
<div class="flex items-start gap-2.5 justify-end">
    <div class="flex flex-col w-auto max-w-[320px] leading-1.5 p-4 border-gray-200 bg-gray-100 rounded-e-xl rounded-es-xl dark:bg-gray-700">
       <div class="flex items-center space-x-2 rtl:space-x-reverse">
          <span class="text-sm font-semibold text-gray-900 dark:text-white">{message.name}</span>
          <span class="text-sm font-normal text-gray-500 dark:text-gray-400">{message.time}</span>
       </div>
       <p id={message.id} class="text-sm font-normal py-2.5 text-gray-900 dark:text-white" style="white-space: pre-wrap;">{message.msg}</p>
    </div>
</div>
{:else}
<div class="flex items-start gap-2.5">
    <img class="w-8 h-8 rounded-full" src="/Knowslog_logo.png" alt="Knowslog">
    <div class="min-w-30 relative flex flex-col w-auto max-w-half leading-1.5 p-4 border-gray-200 bg-gray-100 rounded-e-xl rounded-es-xl dark:bg-gray-700">
        <div class="flex items-center space-x-2 rtl:space-x-reverse relative">
            <span class="text-sm font-semibold text-gray-900 dark:text-white">{message.name}</span>
            <span class="text-sm font-normal text-gray-500 dark:text-gray-400">{message.time}</span>
            {#if message.addtional_info}
            <div class="flex items-center text-sm font-light text-gray-500 dark:text-gray-400">
                <LightbulbOutline id="b1" />
            </div>
            {/if}
            <button on:click={copyToClipboard} class="absolute right-0 text-gray-900 dark:text-gray-400 m-0.5 hover:bg-gray-200 dark:bg-gray-700  dark:hover:bg-gray-800 rounded-lg py-2 px-2.5 inline-flex items-center justify-center">
                <span id="default-message" class="inline-flex items-center">
                    <ClipboardOutline />
                    <span class="text-xs font-semibold">Copy</span>
                </span>
            </button>
        </div>
        <Popover class="w-64 text-sm font-light" title="생각" triggeredBy="#b1" placement="bottom-start">{message.addtional_info}</Popover>
        <p id={message.id} class="text-sm font-normal py-2.5 text-gray-900 dark:text-white prose" style="white-space: pre-wrap;">{@html marked(message.msg)}</p>
    </div>
</div>
{/if}