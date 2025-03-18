<script>
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Dropdown, DropdownItem, DropdownDivider, P } from 'flowbite-svelte';
    import { ChevronDownOutline } from 'flowbite-svelte-icons';
    import { v4 as uuidv4 } from 'uuid';

    import MessageInput from "$lib/components/common/MessageInput.svelte";
    import Message from "$lib/components/common//Message.svelte";
    import { send_message, get_messages } from "$lib/apis/textmining";
    import { addToast } from '$lib/common';

    import { username } from '$lib/stores';
    import { get } from "svelte/store";

    export let chat_id = ''
    export let instruct_id = ''
    export let selected_llm={value:0,name:"모델선택",is_userllm:true}
    export let selected_userdocument={value:0,name:"None"}
    export let chat_title = ''
    export let topic_name = ''
    let message_list= []
    let user_msg = '';
    
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
            time: new Date().toLocaleString(),
            is_user: false,
            is_done: false
        }

        message_list = [...message_list, message];
        message_list = [...message_list, res_msg];
        
        let params = {
            chat_id: chat_id,
                    instruct_id : instruct_id,
                    input: user_msg,
                    }

        let success_callback = (json) => {
            message_list[message_list.length-1].name = json.name
            message_list[message_list.length-1].msg = json.content
            message_list[message_list.length-1].thought = json.full_prompt
            message_list[message_list.length-1].is_done = true
            
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        
        await send_message(params, success_callback, failure_callback);
    }

    async function get_data()
    {        
        let params = {
            chat_id: chat_id
        }
        message_list=[]
        let success_callback = (json) => {
            message_list = json.map(item => {
                return {
                    id: uuidv4(),
                    name: item.name,
                    msg: item.content,
                    thought: item.full_prompt,
                    time: new Date(item.create_date).toLocaleString(),
                    is_user: item.is_user,
                    is_done: true
                }
            })

        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        await get_messages(params, success_callback, failure_callback);
    }

    let messageListElement;
    
    $: if (chat_id) {
            get_data();
        }

    $ : if (message_list.length > 0) {
            messageListElement.scrollTop = messageListElement.scrollHeight;
        }

</script>
{#if instruct_id==''}
<div class="flex items-center justify-center h-full">
    <P>텍스트마이닝 지시문을 적용해주세요.</P>
</div>
{:else}
<div>
    <div>
        <Navbar rounded color="form" class='px-2 py-3' >
            <NavBrand>{chat_title}</NavBrand>
            <NavUl ulClass="flex flex-col md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:text-sm md:font-medium">
                {topic_name}
            </NavUl>
      </Navbar>
    </div>

    <div class="flex flex-col gap-4">
        <div class="message-container" bind:this={messageListElement}>
            {#each message_list as message}
                <Message bind:message={message}/>
            {/each}
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