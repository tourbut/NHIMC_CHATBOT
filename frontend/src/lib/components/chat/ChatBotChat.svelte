<script>
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Dropdown, DropdownItem, DropdownDivider, P, Button, Tooltip } from 'flowbite-svelte';
    import { ChevronDownOutline, TrashBinOutline } from 'flowbite-svelte-icons';
    import { v4 as uuidv4 } from 'uuid';

    import MessageInput from "$lib/components/common/MessageInput.svelte";
    import Message from "$lib/components/common//Message.svelte";
    import { send_message_bot, get_messages,clear_messages } from "$lib/apis/chat";
    import { addToast } from '$lib/common';

    import { username } from '$lib/stores';
    import { get } from "svelte/store";

    export let chat_id = null
    export let chatbot_id = null
    let chat_or_chatbot_id = null
    export let chatbot_data = ''

    let message_list= []
    let user_msg = '';
    let is_loading = false;

    const sendMessage = async () => {
        if (user_msg == '') {
            return;
        }

        let message = {
            id: uuidv4(),
            name: get(username),
            msg: user_msg,
            time: new Date().toLocaleString(),
            is_user: true
        }

        let res_msg= {
            id: uuidv4(),
            name: '미드미',
            msg: '생각중... 잠시만 기다려주세요',
            thought: '',
            tools: '',
            time: new Date().toLocaleString(),
            is_user: false,
            is_done: false
        }

        message_list = [...message_list, message];
        message_list = [...message_list, res_msg];
        
        let params = {
                    chat_id: chatbot_data['chat_id'],
                    chatbot_id : chatbot_data['chatbot_id'],
                    input: user_msg,
                    }
        

        let success_callback = (json) => {
            console.log(json)
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        let streamCallback = (json) => {
            if (json.is_done){
                message_list[message_list.length-1].thought = json.thought
                message_list[message_list.length-1].tools = json.tools['retriever']
                message_list[message_list.length-1].msg = typeof json.content === 'object' ? JSON.stringify(json.content) : json.content
                message_list[message_list.length-1].time = new Date(json.create_date).toLocaleString()
            }
            else{
                message_list[message_list.length-1].msg = json.content
                message_list[message_list.length-1].time = new Date(json.create_date).toLocaleString()
            }
        }
        await send_message_bot(params, success_callback, failure_callback,streamCallback);
    }

    async function get_data(gubun,params)
    {        
        is_loading = false
        message_list=[]

        let success_callback = (json) => {
            message_list = json.map(item => {
                return {
                    id: uuidv4(),
                    name: item.name,
                    msg: item.content,
                    thought: item.thought,
                    tools: item.tools ? item.tools['retriever'] : null,
                    time: new Date(item.create_date).toLocaleString(),
                    is_user: item.is_user,
                    is_done: true
                }
            })
            is_loading = true
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        chat_or_chatbot_id = params.id
        if (gubun=='chatbot'){
            await get_messages(params, success_callback, failure_callback)
        }
        else if(gubun=='chat'){
            await get_messages(params, success_callback, failure_callback)
        }
    }

    const clearMessages = async () => {

        let params = {
            id:chat_or_chatbot_id
        }

        let success_callback = (json) => {
            message_list = []
            addToast('info','메시지가 삭제되었습니다.')
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        
        await clear_messages(params, success_callback, failure_callback)
    }

    $: if (chatbot_id) {
            get_data('chatbot',{id: chatbot_id})
        } 

    $: if (chat_id) {
            get_data('chat',{id: chat_id})
        }
        
    let messageListElement;
    
    $ : if (message_list.length > 0) {
            messageListElement.scrollTop = messageListElement.scrollHeight;
        }

</script>
{#if chatbot_data['chatbot_id']==''}
<div class="flex items-center justify-center h-full">
    <P>챗봇 설정을 저장하세요.</P>
</div>
{:else}
<div>
    <div>
        <Navbar rounded color="form" class='px-2 py-3' >
            {#if chatbot_data['chat_title']}
                <NavBrand>
                    {chatbot_data['chat_title']+ '('+chatbot_data['bot_name']+')'}
                </NavBrand>
            {:else}
                <NavBrand>{chatbot_data['bot_name']}</NavBrand>
            {/if}
            <NavUl ulClass="flex flex-col md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:text-sm md:font-medium">
            </NavUl>
            <div class="ms-auto flex items-center text-gray-500 dark:text-gray-400 sm:order-2">
                <button on:click={clearMessages}>
                    <TrashBinOutline />
                </button>
                <Tooltip placement="bottom" >
                    대화내용 삭제
                </Tooltip>
            </div>
        </Navbar>
    </div>

    <div class="flex flex-col gap-4">
        <div class="message-container" bind:this={messageListElement}>
            {#if !is_loading}
                <div class="flex items-center justify-center h-full">
                    <P>메시지를 불러오는 중입니다.</P>
                </div>
            {:else}
                {#each message_list as message}
                    <Message bind:message={message}/>
                {/each}
            {/if}
        </div>  
        <MessageInput bind:message={user_msg} sendMessage={sendMessage}/>
    </div>
</div>
{/if}
<style>
    .message-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;                /* Tailwind의 gap-4 */
        overflow-y: auto;         /* 내용이 넘칠 경우 수직 스크롤바 표시 */
        min-height: 69vh;         /* 최대 높이 60vh (화면 높이의 60%) */
        max-height: 69vh;         /* 최대 높이 60vh (화면 높이의 60%) */
    }
</style>