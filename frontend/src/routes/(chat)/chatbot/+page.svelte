<script>
    import ChatBotDev from "$lib/components/chat/ChatBotDev.svelte";
    import ChatBotChat from "$lib/components/chat/ChatBotChat.svelte";
    import Sidebar from '$lib/components/common/Sidebar.svelte';
    import { onMount } from 'svelte';
    
    import { Button, Modal, FloatingLabelInput , Textarea, P } from 'flowbite-svelte';

    import { create_chatbot, get_chatbot_list_by_userid,get_chatbot} from "$lib/apis/chat";
    import { addToast } from '$lib/common';

    let bot_list = [{category: 'chat', items: []}];
    let chatbot_id = ''
    let bot_name=''
    let showModal = false;
    
    let table_head=[
        {id:0,name:"title",type:"text",desc:"챗봇명"},
        {id:1,name:"description",type:"text",desc:"설명"},
    ];

    let form_data={}
    let chatbot_data = {
        chatbot_id: '',
        bot_name: '',
        description: '',
        instruct_prompt: '',
        thought_prompt: '',
        user_llm_id: null,
        dept_llm_id: null,
        user_file_id: null,
        bottools_id: null,
        is_public: false,
        is_thought: false,
        temperature: 0.5,
        search_kwargs:{
                        k: 1,
                        lambda: 0.2,
                        retriever_score: 7.0
                    }
    }

    const createChat = async () => {
        showModal = true;
    }

    const btn_create_chat = async () => {
        showModal = false;
        let params;
        if (form_data['bot_name'] == '') {
            addToast('error','챗봇명을 입력해주세요.')
            return;
        }

        params = {
            bot_name:form_data['bot_name'],
            description:form_data['description'] ? form_data['description'] : null,
        }
        
        let success_callback = (json) => {
            addToast('info','생성 완료')
            chatbot_data['chatbot_id'] = json.id
            chatbot_id = json.id
            chatbot_data['bot_name'] = json.bot_name
            chatbot_data['description'] = json.description

            bot_list[0].items = [...bot_list[0].items,{id:json.id, label:json.bot_name}];

        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        await create_chatbot(params, success_callback, failure_callback);
    }

    const onclick = async (id) => {
        bot_name = bot_list.find(item => item.items.find(item => item.id == id)).items.find(item => item.id == id).label

        let params = {
            chatbot_id:id
        }

        let success_callback = (json) => {
            chatbot_data['chatbot_id'] = json.id
            chatbot_data['bot_name'] = json.bot_name
            chatbot_data['description'] = json.description
            chatbot_data['instruct_prompt'] = json.instruct_prompt
            chatbot_data['thought_prompt'] = json.thought_prompt
            chatbot_data['user_llm_id'] = json.user_llm_id
            chatbot_data['dept_llm_id'] = json.dept_llm_id
            chatbot_data['user_file_id'] = json.user_file_id
            chatbot_data['bottools_id'] = json.bottools_id
            chatbot_data['is_public'] = json.is_public
            chatbot_id = json.id

            if (json.thought_prompt == '') {
                chatbot_data['is_thought'] = false
            } else {
                chatbot_data['is_thought'] = true
            }   
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        
        await get_chatbot(params, success_callback, failure_callback);

    }

    const closeChat = async (id) => {
        let params = {
            id:id
        }
        let success_callback = (json) => {
            addToast('info','삭제 완료')
            bot_list[0].items = bot_list[0].items.filter(item => item.id != id)
        }
        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        await delete_chat(params, success_callback, failure_callback);
        chatbot_id = ''
    }

    async function get_data()
    {
        let params = {}

        let success_callback = (json) => {
            json.forEach(item => {
            // 아이템 추가
            bot_list[0].items = [...bot_list[0].items,{id:item.id, label:item.bot_name}];
            });
        
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        await get_chatbot_list_by_userid(params, success_callback, failure_callback);
    }   
    
    onMount(async () => {
      await get_data()
    })


</script>

<div class="flex h-[80vh]">
    <div class="w-64 flex-shrink-0">
        <Sidebar btn_item_more_click={closeChat} btn_add_button={createChat} btn_click={onclick}
                 bind:side_menus={bot_list}
                 create_btn_name="챗봇 생성"/>
    </div> 
    {#if chatbot_id}
    <div class="flex flex-1">
        <div class="instruct-container">
            <ChatBotDev bind:chatbot_data={chatbot_data} />
        </div>
        <div class="chat-container">
            <ChatBotChat bind:chatbot_data={chatbot_data} bind:chatbot_id={chatbot_id} />
        </div>
    </div>
    {/if}
</div>

<Modal bind:open={showModal} size="xs" autoclose={false} outsideclose={true} class="w-full" on:close={() => {form_data={};}}>
    <form class="flex flex-col space-y-3" action="#">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">챗봇 생성</h3>
        <FloatingLabelInput style="filled" id="floating_filled" name="floating_filled" type="text" bind:value={form_data['bot_name']}>
            {table_head[0].desc}
        </FloatingLabelInput>

        <Textarea style="width: 100%; height: 150px;" id="description" name="description" bind:value={form_data['description']} placeholder="설명" />

        <Button name={"btn_new"} type="submit" class="w-full1" on:click={btn_create_chat}>저장</Button>
    </form>
</Modal>
<style>
    .instruct-container {
        flex: 1;                     /* 전체 너비의 1/3 차지 */
        padding: 1rem;               
        border-right: 2px solid #c9ccd1;  /* 구분선 추가 */
    }
    .chat-container {
        flex: 2;                     /* 전체 너비의 2/3 차지 */
        padding: 1rem;               
    }
</style>