<script>
    import MiningChat from "$lib/components/textmining/MiningChat.svelte";
    import InstructDev from "$lib/components/textmining/InstructDev.svelte";
    import Sidebar from '$lib/components/common/Sidebar.svelte';
    import { onMount } from 'svelte';
    
    import { Button, Modal, FloatingLabelInput , Textarea, P } from 'flowbite-svelte';

    import { create_tmchat, get_tmchats,get_tmchat,get_tminstruct} from "$lib/apis/textmining";
    import { addToast } from '$lib/common';

    let chat_list = [{category: 'chat', items: []}];
    let chat_id = ''
    let chat_title=''
    let topic_name=''
    let showModal = false;
    let instruct_id= ''
    
    let table_head=[
        {id:0,name:"title",type:"text",desc:"채팅방명"},
        {id:1,name:"description",type:"text",desc:"설명"},
    ];

    let form_data={}
    let instruct_data = {
        instruct_id: '',
        title: '',
        memo: '',
        topic_id: '',
        mining_llm_id:'',
        instruct_prompt:'',
        response_prompt:'',
        schema_id:''
    }
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

        params = {
            title:form_data['title'],
            description:form_data['description'] ? form_data['description'] : null,
        }
        
        let success_callback = (json) => {
            addToast('info','생성 완료')

            chat_title=json.title
            chat_id = json.id
            chat_list[0].items = [...chat_list[0].items, {id: json.id, label: json.title, herf: '', caption: ''}];
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        await create_tmchat(params, success_callback, failure_callback);
    }

    const onclick = async (id) => {
        chat_id = id
        chat_title = chat_list.find(item => item.items.find(item => item.id == id)).items.find(item => item.id == id).label
        instruct_id = chat_list.find(item => item.items.find(item => item.id == id)).items.find(item => item.id == id).instruct_id
        let params = {
            tmchat_id:id
        }

        let success_callback = (json) => {
            instruct_data['instruct_id'] = json.instruct_id ? json.instruct_id : ''
        }
        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        await get_tmchat(params, success_callback, failure_callback);
        
        if (instruct_id) {
            
            let param_instruct = {
                tminstruct_id: instruct_id
                }

            let instruct_success_callback = (json) => {
                instruct_data['instruct_id'] = json.id ? json.id : ''
                instruct_data['title'] = json.title ? json.title : ''
                instruct_data['memo'] = json.memo ? json.memo : ''
                instruct_data['topic_id'] = json.topic_id ? json.topic_id : ''
                instruct_data['mining_llm_id'] = json.mining_llm_id ? json.mining_llm_id : ''
                instruct_data['instruct_prompt'] = json.instruct_prompt ? json.instruct_prompt : ''
                instruct_data['response_prompt'] = json.response_prompt ? json.response_prompt : ''
                instruct_data['schema_id'] = json.output_schema_id ? json.output_schema_id : ''
            }

            await get_tminstruct(param_instruct, instruct_success_callback, failure_callback);
        }
        else {
            instruct_data = {
                instruct_id: '',
                title: '',
                memo: '',
                topic_id: '',
                mining_llm_id:'',
                instruct_prompt:'',
                response_prompt:'',
                schema_id:''
            }
        }

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
            let tmp_item = {id: item.id, label: item.title, herf: '', caption: item.topic_name ? item.topic_name : '',instruct_id:item.instruct_id};
            chat_list[0].items = [...chat_list[0].items,tmp_item];
            });
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        await get_tmchats(params, success_callback, failure_callback);
    }   
    
    onMount(async () => {
      await get_data()
    })


</script>

<div class="flex h-[80vh]">
    <div class="w-64 flex-shrink-0">
        <Sidebar btn_item_more_click={closeChat} btn_add_button={createChat} btn_click={onclick}
                 bind:side_menus={chat_list}/>
    </div> 
    {#if chat_id}
    <div class="flex flex-1">
        <div class="instruct-container">
            <InstructDev bind:chat_id={chat_id} bind:instruct_data={instruct_data}
                         bind:selected_topic={instruct_data['topic_id']} 
                         bind:selected_schema={instruct_data['schema_id']} 
                         bind:selected_tmllm={instruct_data['mining_llm_id']}
                         bind:topic_name={topic_name} />
        </div>
        <div class="chat-container">
            <MiningChat bind:instruct_id={instruct_data['instruct_id']} bind:chat_id={chat_id} 
                        bind:chat_title={chat_title} bind:topic_name={topic_name} />
        </div>
    </div>
    {/if}
</div>

<Modal bind:open={showModal} size="xs" autoclose={false} outsideclose={true} class="w-full" on:close={() => {form_data={};}}>
    <form class="flex flex-col space-y-3" action="#">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">텍스트마이닝 개발 생성</h3>
        <FloatingLabelInput style="filled" id="floating_filled" name="floating_filled" type="text" bind:value={form_data['title']}>
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