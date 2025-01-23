<script>
    import { marked } from 'marked'
    import { Popover, Avatar, P } from 'flowbite-svelte';
    import { LightbulbOutline, ClipboardOutline, FileOutline } from 'flowbite-svelte-icons';
    
    export let message = {
        id: '1',
        name: 'Jese',
        msg: 'Hello, how can I help you?',
        thought: 'thought',
        tools: 'tools',
        time: '2024.02.20. 14:30:22',
        is_user: true,
        is_done: false
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
       <P id={message.id} class="text-sm font-normal py-2.5  prose">{@html marked(message.msg)}</P>
    </div>
</div>
{:else}
<div class="flex items-start gap-2.5">
    {#if message.name == '바르미'}
        <Avatar src="/바르미_상반신.png" size="sm"/>
    {:else if message.name == '미드미'}
        <Avatar src="/미드미_상반신.png" size="sm"/>
    {:else}
        <Avatar src="/바르미_상반신.png" size="sm"/>
    {/if}
    <div class="min-w-[350px] relative flex flex-col w-auto max-w-half leading-1.5 p-4 border-gray-200 bg-gray-100 rounded-e-xl rounded-es-xl dark:bg-gray-700">
        <div class="flex items-center space-x-2 rtl:space-x-reverse relative">
            <span class="text-sm font-semibold text-gray-900 dark:text-white">{message.name}</span>
            <span class="text-sm font-normal text-gray-500 dark:text-gray-400">{message.time}</span>
            {#if message.thought}
            <div class="flex items-center text-sm font-light text-gray-500 dark:text-gray-400">
                <LightbulbOutline id={'thought'+message.id} />
                <Popover class="w-64 text-sm font-light" title="생각" triggeredBy={'#thought'+message.id} placement="bottom-start">
                    <div class='popover_content'>
                        {@html marked(message.thought)}
                    </div>
                </Popover>
            </div>
            {/if}
            {#if message.tools}
            <div class="flex items-center text-sm font-light text-gray-500 dark:text-gray-400">
                <FileOutline id={'tools'+message.id} />
                <Popover class="w-80 text-sm font-light" title="문서" triggeredBy={'#tools'+message.id} placement="bottom-start">
                    <div class='popover_content'>
                        {@html marked(message.tools)}
                    </div>
                </Popover>
            </div>
            {/if}
            {#if message.msg && message.is_done}
            <button on:click={copyToClipboard} class="absolute right-0 text-gray-900 dark:text-gray-400 m-0.5 hover:bg-gray-200 dark:bg-gray-700  dark:hover:bg-gray-800 rounded-lg py-2 px-2.5 inline-flex items-center justify-center">
                <span id="default-message" class="inline-flex items-center">
                    <ClipboardOutline />
                    <span class="text-xs font-semibold">Copy</span>
                </span>
            </button>
            {/if}
        </div>
        <P id={message.id} class="text-sm font-normal py-2.5  prose">{@html marked(message.msg)}</P>
    </div>
</div>
{/if}

<style>
    .popover_content {
        max-height: 10rem;
        overflow: auto;
    }
</style>