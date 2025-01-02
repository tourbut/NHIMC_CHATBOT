<script>
    import { Navbar, NavBrand, NavLi, NavUl, NavHamburger, Dropdown, DropdownItem, DropdownDivider, P } from 'flowbite-svelte';
    import { ChevronDownOutline } from 'flowbite-svelte-icons';
    import { v4 as uuidv4 } from 'uuid';

    import MessageInput from "$lib/components/common/MessageInput.svelte";
    import Message from "$lib/components/common//Message.svelte";
    import { send_message, get_messages } from "$lib/apis/chat";
    import { addToast } from '$lib/common';

    import { username } from '$lib/stores';
    import { get } from "svelte/store";

    export let chat_id = ''
    export let selected_llm={value:0,name:"모델선택",is_userllm:true}
    export let selected_userdocument={value:0,name:"None"}
    export let chat_title = ''

    let message_list= []
    let user_msg = '';
    
    const sendMessage = async () => {
        if (user_msg == '') {
            return;
        }

        if (selected_llm.value == 0) {
            addToast('error','모델을 선택해주세요.')
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
            name: '바르미',
            msg: '',
            thought: '',
            tools: '',
            time: new Date().toLocaleString(),
            is_user: false
        }

        message_list = [...message_list, message];
        message_list = [...message_list, res_msg];
        
        let params
        if (selected_llm.is_userllm==true)
        {
            params = {
            chat_id: chat_id,
            user_llm_id: selected_llm.value,
            document_id: selected_userdocument ? selected_userdocument.value : null,
            input: user_msg,
            }
        }
        else
        {
            params = {
            chat_id: chat_id,
            dept_llm_id: selected_llm.value,
            document_id: selected_userdocument ? selected_userdocument.value : null,
            input: user_msg,
            }
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
                message_list[message_list.length-1].msg = json.content
            }
            else{
                message_list[message_list.length-1].msg = json.content
                message_list[message_list.length-1].time = json.create_date
            }
        }
        await send_message(params, success_callback, failure_callback,streamCallback);
    }

    async function get_data()
    {        
        let params = {
            chat_id: chat_id
        }

        let success_callback = (json) => {
            message_list = json.map(item => {
                return {
                    id: uuidv4(),
                    name: item.name,
                    msg: item.content,
                    thought: item.thought,
                    tools: item.tools ? item.tools['retriever'] : null,
                    time: item.create_date,
                    is_user: item.is_user
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
<div>
    <div>
        <Navbar rounded color="form" class='px-2 py-1' >
        <NavHamburger />
        <NavBrand>{chat_title}</NavBrand>
        <NavUl >
          <NavLi class="cursor-pointer">
            Model : {selected_llm.name}
          </NavLi>  
          <NavLi class="cursor-pointer">
            File : {selected_userdocument ? selected_userdocument.name : 'None'}
          </NavLi>
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