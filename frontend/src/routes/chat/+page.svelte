<script>
    import Chat from "$lib/components/chat/Chat.svelte";
    import Sidebar from '$lib/components/common/Sidebar.svelte';
    import { onMount } from 'svelte';
    
    import { Button, Modal, Label, Input, FloatingLabelInput , Checkbox,Select, Radio } from 'flowbite-svelte';
    import Combo from '$lib/components/common/Combo.svelte';

    import { create_chat, get_userllm,get_deptllm, get_chat_list, delete_chat, get_chat, get_documents} from "$lib/apis/chat";
    import { addToast } from '$lib/common';

    let chat_list = [{category: 'chat', items: []}];
    let chat_id = ''
    let chat_title=''
    let showModal = false;
    let userllm_list = []
    let deptllm_list = []
    let userdocument_list = []
    let selected_llm={value:0,name:"모델선택",is_userllm:true}
    let selected_userdocument={value:0,name:"문서선택"}
    let table_head=[
        {id:0,name:"title",type:"text",desc:"채팅방명"},
        {id:1,group:"1",name:"userllm_id",type:"combo",desc:"유저_모델선택",combo:userllm_list},
        {id:2,group:"1",name:"deptllm_id",type:"combo",desc:"부서_모델선택",combo:deptllm_list},
        {id:3,name:"userdocument_id",type:"combo",desc:"파일선택",combo:userdocument_list}
    ];


    let form_data={}
    let radio_group = 'dept';
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
            user_llm_id:form_data['userllm_id'] ? form_data['userllm_id'] : null,
            dept_llm_id:form_data['deptllm_id'] ? form_data['deptllm_id'] : null,
            user_file_id:form_data['userdocument_id'] ? form_data['userdocument_id'] : null
        }
        
        let success_callback = (json) => {
            addToast('info','생성 완료')
            if (json.user_llm_id == null) {
                selected_llm = deptllm_list.find(item => item.value == json.dept_llm_id)
                selected_llm.is_userllm = false
            } else {
                selected_llm = userllm_list.find(item => item.value == json.user_llm_id)
                selected_llm.is_userllm = true
            }
            
            selected_userdocument = userdocument_list.find(item => item.value == json.user_file_id)

            chat_title=json.title
            chat_id = json.id
            chat_list[0].items = [...chat_list[0].items, {id: json.id, label: json.title, herf: '', caption: selected_userdocument ? selected_userdocument.name : ''}];
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        await create_chat(params, success_callback, failure_callback);
    }

    const onclick = async (id) => {
        chat_id = id
        chat_title = chat_list.find(item => item.items.find(item => item.id == id)).items.find(item => item.id == id).label
        let params = {
            chat_id:id
        }

        let success_callback = (json) => {
            if (json.user_llm_id == null) {
                selected_llm = deptllm_list.find(item => item.value == json.dept_llm_id)
                selected_llm.is_userllm = false
            } else {
                selected_llm = userllm_list.find(item => item.value == json.user_llm_id)
                selected_llm.is_userllm = true
            }

            selected_userdocument = userdocument_list.find(item => item.value == json.user_file_id)
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
            selected_userdocument = userdocument_list.find(item_ => item_.value == item.user_file_id)
            chat_list[0].items = [...chat_list[0].items,{id: item.id, label: item.title, herf: '',caption: selected_userdocument ? selected_userdocument.name : ''}];
            });
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        let userllm_success_callback = (json) => {
            userllm_list= json.map(item => {return {value:item.id,name:item.name}})
            table_head[1].combo=userllm_list
        }

        let deptllm_success_callback = (json) => {
            deptllm_list= json.map(item => {return {value:item.id,name:item.name}})
            table_head[2].combo=deptllm_list
        }
        let documents_success_callback = (json) => {
            userdocument_list= json.map(item => {return {value:item.user_file_id,name:item.title}}) 
            table_head[3].combo=userdocument_list
        }

        await get_documents(params,documents_success_callback,failure_callback);

        await get_userllm(params, userllm_success_callback, failure_callback);

        await get_deptllm(params, deptllm_success_callback, failure_callback);

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
            <Chat bind:chat_id={chat_id} 
                  bind:selected_llm={selected_llm}
                  bind:selected_userdocument={selected_userdocument} 
                  bind:chat_title={chat_title}/>
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
            모델 선택
            <div class="flex gap-3 mt-1">
                <Radio bind:group={radio_group} value="dept">부서모델</Radio>
                <Radio bind:group={radio_group} value="user">유저모델</Radio>
            </div>
            <div class="mt-2">
            {#if radio_group == 'dept'}
                <Combo is_dropcombo={false} ComboMenu={table_head[2].combo} bind:selected_name={form_data['deptllm_id']} />
            {:else}
                <Combo is_dropcombo={false} ComboMenu={table_head[1].combo} bind:selected_name={form_data['userllm_id']} />
            {/if}
        </div>
        </Label>

        <Label class="text-gray-500 dark:text-gray-400 mt-4">
            {table_head[3].desc} 
            <Combo is_dropcombo={false} ComboMenu={table_head[3].combo} bind:selected_name={form_data['userdocument_id']} />
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