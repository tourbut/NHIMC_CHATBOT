<script>
    import Chat from "$lib/components/chat/Chat.svelte";
    import Sidebar from '$lib/components/common/Sidebar.svelte';
    import { onMount } from 'svelte';
    import ComboModal from "$lib/components/common/Combo_Modal.svelte";
    import { create_chat, get_userllm, get_chat_list, delete_chat, get_chat, get_documents} from "$lib/apis/chat";
    import { addToast } from '$lib/common';

    let chat_list = []
    let chat_id = ''
    let showModal = false;
    let dataLoaded = false;
    let userllm_list = []
    let userdocument_list = []
    let selected_userllm={value:0,name:"모델선택"}
    let selected_userdocument={value:0,name:"문서선택"}
    let table_head=[
        {id:0,name:"userllm_id",type:"combo",desc:"모델선택",combo:userllm_list},
        {id:1,name:"userdocument_id",type:"combo",desc:"파일선택",combo:userdocument_list},
        {id:2,name:"title",type:"text",desc:"채팅방명"}
    ];


    let form_data={}

    const createChat = async () => {
        showModal = true;
    }

    const btn_create_chat = async () => {
        showModal = false;

        let params = {
            title:form_data['title'],
            user_llm_id:form_data['userllm_id']
        }
        
        let success_callback = (json) => {

            addToast('info','생성 완료')
            selected_userllm = userllm_list.find(item => item.value == json.user_llm_id)
            chat_id = json.id
            chat_list[0].items.push({
                id: json.id,
                label: json.title,  // title이 없을 경우 'Untitled'로 설정
                herf: '',            // id 기반 URL 설정
                caption: ''
            });
        }
        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        await create_chat(params, success_callback, failure_callback);
    }

    const onclick = async (id) => {
        chat_id = id

        let params = {
            chat_id:id
        }

        let success_callback = (json) => {
            selected_userllm = userllm_list.find(item => item.value == json.user_llm_id)
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
            chat_list.forEach(item => {
            item.items = item.items.filter(item => item.id != id)
            });
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
                // 카테고리로 그룹화된 객체를 찾음
                let categoryGroup = chat_list.find(group => group.category === item.category);

                // 해당 카테고리가 없으면 새로 추가
                if (!categoryGroup) {
                    categoryGroup = { category: item.category, items: [] };
                    chat_list.push(categoryGroup);
                };

                // 아이템 추가
                categoryGroup.items.push({
                  id: item.id,
                  label: item.title || 'Untitled',  // title이 없을 경우 'Untitled'로 설정
                  herf: '',            // id 기반 URL 설정
                  caption: item.url
                });
            });
            dataLoaded=true
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        
        let userllm_success_callback = (json) => {
            userllm_list= json.map(item => {return {value:item.id,name:item.name}})
            table_head[0].combo=userllm_list
        }

        let documents_success_callback = (json) => {
            userdocument_list= json.map(item => {return {value:item.collection_id,name:item.title}}) 
            console.log(userdocument_list)
            table_head[1].combo=userdocument_list
        }

        await get_userllm(params, userllm_success_callback, failure_callback);

        await get_chat_list(params, success_callback, failure_callback);

        await get_documents(params,documents_success_callback,failure_callback)
    }   
    
    onMount(async () => {
      await get_data()
    })
    
</script>

<div class="flex h-screen overflow-hidden">
    <div class="w-64 flex-shrink-0">
        {#if dataLoaded}
            <Sidebar btn_item_more_click={closeChat} btn_add_button={createChat} bind:side_menus={chat_list} btn_click={onclick}/>
        {/if}
    </div> 
    <div class="chat-container">
        {#if chat_id}
            <Chat bind:chat_id={chat_id} 
                  bind:userllm_list={userllm_list}
                  bind:userdocument_list={userdocument_list} 
                  bind:selected_userllm={selected_userllm}
                  bind:selected_userdocument={selected_userdocument} />
        {/if}
    </div>
</div>
<ComboModal header={"채팅방생성"} bind:table_head={table_head} formModal={showModal} bind:form_data={form_data} btn_click={btn_create_chat} > </ComboModal>

<style>
   .chat-container {
        flex: 1;                     /* 남은 공간을 차지하도록 설정 */
        margin-left: auto;           /* 좌우 중앙 정렬 */
        margin-right: auto;          /* 좌우 중앙 정렬 */
        padding: 1rem;               /* padding: 1rem (Tailwind의 p-4에 해당) */
        min-height: 85vh;           /* 브라우저 높이와 동일하게 설정 */
        max-height: 85vh;           /* 브라우저 높이와 동일하게 설정 */
        max-width: 64rem;            /* 최대 너비 64rem (Tailwind의 max-w-5xl에 해당) */
    }
</style>