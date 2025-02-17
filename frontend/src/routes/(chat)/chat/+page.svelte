<script>
    import Chat from "$lib/components/chat/Chat.svelte";
    import Sidebar from '$lib/components/common/Sidebar.svelte';
    import { onMount } from 'svelte';
    
    import { Button, Modal, Label, Input, FloatingLabelInput , Checkbox,Select, Radio } from 'flowbite-svelte';
    import Combo from '$lib/components/common/Combo.svelte';

    import { create_chat, get_chat_list, delete_chat, get_chat, get_chatbot_list_by_public} from "$lib/apis/chat";
    import { addToast } from '$lib/common';
	import ChatBotChat from "$lib/components/chat/ChatBotChat.svelte";

    let chat_list = [{category: 'chat', items: []}];

    let chat_title=''
    let showModal = false;
    let chatbot_list = []
    let chat_id = ''
    let chatbot_id = ''
    let chatbot_data = {
        chat_id: '',
        chatbot_id: '',
        chat_title: ''
    }
    let selected_chatbot={value:0,name:"업무도우미 선택"}
    let table_head=[
        {id:0,name:"title",type:"text",desc:"채팅방명"},
        {id:1,name:"chatbot_id",type:"combo",desc:"업무도우미",combo:chatbot_list}
    ];

    let form_data={}
    const createChat = async () => {
        showModal = true;
    }

    const btn_create_chat = async () => {
        showModal = false;
        let params;
        if (form_data['title'] == '') {
            addToast('error','채팅방명을 입력해주세요.')
            return;
        }
        if (form_data['chatbot_id'] == null || form_data['chatbot_id'] == '') {
            addToast('error','업무도우미를 선택하세요.')
            return;
        }

        params = {
            title:form_data['title'],
            chatbot_id:form_data['chatbot_id'] ? form_data['chatbot_id'] : null
        }
        
        let success_callback = (json) => {
            addToast('info','생성 완료')
            
            selected_chatbot = chatbot_list.find(item => item.value == json.chatbot_id)
            chatbot_data = {
                chat_id:json.id,
                chat_title: json.title,
                chatbot_id:json.chatbot_id
            }
            chat_list[0].items = [...chat_list[0].items, {id: json.id, label: json.title, herf: '', caption: selected_chatbot ? selected_chatbot.name : ''}];
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        await create_chat(params, success_callback, failure_callback);
    }

    const onclick = async (id) => {
        chat_title = chat_list.find(item => item.items.find(item => item.id == id)).items.find(item => item.id == id).label
        let params = {
            chat_id:id
        }

        let success_callback = (json) => {
            chatbot_data = {
                chat_id :chat_id,
                chatbot_id: json.chatbot_id,
                chat_title: chat_title
            }
            chat_id = id
            chatbot_id = json.chatbot_id
        }
        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        await get_chat(params, success_callback, failure_callback);

    }

    const closeChat = async (id) => {
        let params = {
            id:id
        }
        let success_callback = (json) => {
            addToast('info','삭제 완료')
            chat_list[0].items = chat_list[0].items.filter(item => item.id != id)
        }
        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        await delete_chat(params, success_callback, failure_callback);
        chat_id = ''
    }

    async function get_data()
    {
        let params = {}

        let success_callback = (json) => {
        json.forEach(item => {
            // 아이템 추가
            selected_chatbot = chatbot_list.find(item_ => item_.value == item.chatbot_id)
            chat_list[0].items = [...chat_list[0].items,{id: item.id, label: item.title, herf: '',caption: selected_chatbot ? selected_chatbot.name : ''}];
            });
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        let chatbot_success_callback = (json) => {
            chatbot_list= json.map(item => {return {value:item.id,name:item.bot_name}}) 
            table_head[1].combo=chatbot_list
        }

        await get_chatbot_list_by_public(params,chatbot_success_callback,failure_callback);

        await get_chat_list(params, success_callback, failure_callback);

    }   
    
    onMount(async () => {
      await get_data()
    })

</script>

<div class="flex h-[80vh] ">
    <div class="w-64 flex-shrink-0">
        <Sidebar btn_item_more_click={closeChat} btn_add_button={createChat} btn_click={onclick}
                 bind:side_menus={chat_list}/>
    </div> 
    <div class="chat-container">
        {#if chat_id}
            <ChatBotChat bind:chatbot_data={chatbot_data} bind:chat_id={chat_id}/>
        {/if}
    </div>
</div>

<Modal bind:open={showModal} size="xs" autoclose={false} outsideclose={true} class="w-full" on:close={() => {form_data={};}}>
    <form class="flex flex-col space-y-3" action="#">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">채팅방 생성</h3>
        <FloatingLabelInput style="filled" id="floating_filled" name="floating_filled" type="text" bind:value={form_data['title']}>
            {table_head[0].desc}
        </FloatingLabelInput>
        <Label class="text-gray-500 dark:text-gray-400 mt-4">
            {table_head[1].desc} 
            <Combo is_dropcombo={false} ComboMenu={table_head[1].combo} bind:selected_name={form_data['chatbot_id']} />
        </Label>
        <Button name={"btn_new"} type="submit" class="w-full1" on:click={btn_create_chat}>저장</Button>
    </form>
</Modal>
<style>
   .chat-container {
        flex: 1;                     /* 남은 공간을 차지하도록 설정 */
        margin-left: auto;           /* 좌우 중앙 정렬 */
        margin-right: auto;          /* 좌우 중앙 정렬 */
        padding: 1rem;               /* padding: 1rem (Tailwind의 p-4에 해당) */
        max-width: 70rem;            /* 최대 너비 64rem (Tailwind의 max-w-5xl에 해당) */
    }
</style>