<script>
    let newMessage = '';
    export let messages = [];
    
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