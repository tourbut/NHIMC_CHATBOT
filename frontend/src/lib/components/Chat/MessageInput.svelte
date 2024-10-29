<script>
    import { Textarea, ToolbarButton } from 'flowbite-svelte';
    import { ImageOutline, FaceGrinOutline, PaperPlaneOutline } from 'flowbite-svelte-icons';

    export let message = '';
    export let sendMessage;

    let keydownHandler = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
            message = '';
        }
    };

    async function handleSubmit() {
        await sendMessage();
        message = ''; // 메시지를 비웁니다.
    }

</script>
  
<form on:submit|preventDefault={handleSubmit}>
    <div class="flex items-center px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-700">
        <!-- 기능보완후 추가
        <ToolbarButton color="dark" class="text-gray-500 dark:text-gray-400">
            <ImageOutline class="w-6 h-6" />
            <span class="sr-only">Upload image</span>
        </ToolbarButton>
        -->
        <Textarea id="chat" class="mx-4 bg-white dark:bg-gray-800" rows="1" placeholder="Your message..." bind:value={message} on:keydown={keydownHandler} />
        <ToolbarButton type="submit" color="blue" class="rounded-full text-primary-600 dark:text-primary-500">
            <PaperPlaneOutline class="w-6 h-6 rotate-45" />
            <span class="sr-only">Send message</span>
        </ToolbarButton>
    </div>
</form>