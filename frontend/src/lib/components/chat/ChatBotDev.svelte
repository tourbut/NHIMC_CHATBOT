<script>
    import { onMount } from 'svelte';
    import { addToast } from '$lib/common';
    import { FloatingLabelInput, Textarea, Label, Modal, Radio, P, Select, Checkbox, Range} from 'flowbite-svelte';
    import { Input, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, Button, Tooltip} from 'flowbite-svelte';
    import { PlusOutline, EditOutline, ChevronDownOutline } from 'flowbite-svelte-icons';
    import Combo from '$lib/components/common/Combo.svelte';
    import {update_chatbot, get_deptllm, get_botdocuments} from "$lib/apis/chat";


    export let chatbot_data = {
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
                    },
        is_agent: false,
    }

    let dept_llm_list = []
    let user_file_list = [{value:null, name:'문서 없음', desc:''}]
    let is_detail_open = false

    export let bot_selector = 'normal'

    async function get_data(){

        let params = {}

        let deptllm_success_callback = (json) => {
            dept_llm_list = json.map((item) => {
                return {value:item.id, name:item.name}
            })
        }
        
        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        let documents_success_callback = (json) => {
            
            let file_list = json.map((item) => {
                let name = item.title + ' (요청: ' + item.request_dept_nm + ')'

                return {value:item.user_file_id, name:name, desc:item.description}
            })

            user_file_list = [...user_file_list, ...file_list]
        }

        await get_deptllm(params, deptllm_success_callback, failure_callback);
        await get_botdocuments(params, documents_success_callback, failure_callback);
    }
    
    const btn_update_chatbot = async () => {

        let params = {
            id: chatbot_data['chatbot_id'],
            bot_name: chatbot_data['bot_name'],
            description: chatbot_data['description'],
            instruct_prompt: chatbot_data['instruct_prompt'],
            thought_prompt: chatbot_data['thought_prompt'],
            user_llm_id: chatbot_data['user_llm_id'],
            dept_llm_id: chatbot_data['dept_llm_id'],
            user_file_id: chatbot_data['user_file_id'],
            bottools_id: chatbot_data['bottools_id'],
            is_public: chatbot_data['is_public'],
            temperature: chatbot_data['temperature'],
            search_kwargs: chatbot_data['search_kwargs'],
            is_agent: chatbot_data['is_agent'],
        }

        let success_callback = (json) => {
            addToast('info','챗봇 저장 완료')
            chatbot_data['chatbot_id'] = json.id
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        await update_chatbot(params, success_callback, failure_callback);
    }

    onMount(() => {
        get_data();
    });

    $ : if(bot_selector == 'normal'){
        chatbot_data['is_thought'] = false
        chatbot_data['is_agent'] = false
        chatbot_data['thought_prompt'] = ''
    }else if(bot_selector == 'thought'){
        chatbot_data['is_thought'] = true
        chatbot_data['is_agent'] = false
    }else if(bot_selector == 'agent'){
        chatbot_data['is_thought'] = false
        chatbot_data['is_agent'] = true
        chatbot_data['thought_prompt'] = ''
        chatbot_data['instruct_prompt'] = ''
    }
</script>
<div class="instruct-div-scroll">
    <div class="mb-2">
        <FloatingLabelInput style="filled" size="small" type="text" bind:value={chatbot_data['bot_name']}  >
            지시문 제목
        </FloatingLabelInput>
    </div>
    <div class="mt-2">
        <Label class="block mb-2">설명</Label>
        <Textarea class="min-h-[50px] max-h-[100px]" bind:value={chatbot_data['description']} placeholder="설명 입력" />
    </div> 
    <div class="mt-2 flex-container">
        <Label class="mr-2">모델</Label>
        <div class="fill-space">
        <Combo underline={true} placeholder="모델 선택" ComboMenu={dept_llm_list} bind:selected_name={chatbot_data['dept_llm_id']}/>
        </div>
    </div>
    <div class="mt-2">
        <Label class="block mb-2">프롬프트 작성</Label>
            <ul class="items-center w-full rounded-lg border border-gray-200 sm:flex dark:bg-gray-800 dark:border-gray-600 divide-x rtl:divide-x-reverse divide-gray-200 dark:divide-gray-600">
                <li class="w-full"><Radio bind:group={bot_selector} class="p-3" value="normal">일반</Radio></li>
                <li class="w-full"><Radio bind:group={bot_selector} class="p-3" value="thought">추론</Radio></li>
                <li class="w-full"><Radio bind:group={bot_selector} class="p-3" value="agent">에이전트</Radio></li>
            </ul>
        {#if (chatbot_data['is_agent'] == false)}
            {#if (chatbot_data['is_thought'])}
            <div class="mt-2 ml-2 bg-gray-100 dark:bg-gray-600 rounded-lg p-1">
                <Label class="block mb-2">생각모델 지시문</Label>
                <Textarea class="min-h-[100px] max-h-[150px]" bind:value={chatbot_data['thought_prompt']} placeholder="명령어 입력" />
            </div>
            {/if}
            <div class="mt-2 ml-2 bg-gray-100 dark:bg-gray-600 rounded-lg p-1">
                <Label class="block mb-2">지시문</Label>
                <Textarea class="min-h-[100px] max-h-[150px]" bind:value={chatbot_data['instruct_prompt']} placeholder="명령어 입력" />
            </div>
        {/if}
    </div>
    {#if (chatbot_data['is_agent'] == false)}
    <div class="mt-2">
        <div class="flex justify-between">
            <Label class="block mb-0">세부 설정</Label>
            <button class="" on:click={() => is_detail_open = !is_detail_open} >
                <ChevronDownOutline class="w-7 h-7 mr-1 text-gray-500" />
            </button>
        </div>
        {#if (is_detail_open)}
        <div class="mt-2 ml-2 bg-gray-100 dark:bg-gray-600 rounded-lg p-1">
            <Label class="block mb-2">창의성 정도({chatbot_data['temperature']})</Label>
            <Range bind:value={chatbot_data['temperature']} min="0.1" max="1.0" step="0.1" size="sm" />
        </div>
        <div class="mt-2 ml-2 bg-gray-100 dark:bg-gray-600 rounded-lg p-1">
            <Label class="block mb-2">문서 검색수({chatbot_data['search_kwargs']['k']})</Label>
            <Range bind:value={chatbot_data['search_kwargs']['k']} min="1" max="5" step="1" size="sm" />
        </div>
        <div class="mt-2 ml-2 bg-gray-100 dark:bg-gray-600 rounded-lg p-1">
            <Label class="block mb-2">문서 판별점수({chatbot_data['search_kwargs']['retriever_score']})</Label>
            <Range bind:value={chatbot_data['search_kwargs']['retriever_score']} min="0" max="10" step="0.1" size="sm" />
        </div>
        {/if}
    </div>
    {/if}
    <div class="mt-2 flex-container">
        <Label class="mr-2">참고 문서</Label>
        <div class="fill-space">
            <Combo underline={true} placeholder="문서 선택" ComboMenu={user_file_list} bind:selected_name={chatbot_data['user_file_id']}/>
        </div>
    </div>
    <div class="mt-2 mb-2 flex-container">
        <Label class="mr-2">공개 여부</Label>
        <Checkbox bind:checked={chatbot_data['is_public']} />
    </div>
    <Button type="submit" class="w-full" on:click={btn_update_chatbot}>저장</Button>
    
</div>

<style>

  .flex-container {
    display: flex;
    align-items: center;
  }
  .fill-space {
    flex-grow: 1;
  }
  .instruct-div-scroll {
    max-height: 800px; /* 원하는 최대 높이로 설정 */
    overflow-y: auto;
  }
  
</style>