<script>
    import { onMount } from 'svelte';
    import { addToast } from '$lib/common';
    import { FloatingLabelInput, Textarea, Label, Modal, Radio, P, Select} from 'flowbite-svelte';
    import { Input, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, Button, Tooltip} from 'flowbite-svelte';
    import { PlusOutline, EditOutline } from 'flowbite-svelte-icons';
    
    import Combo from '$lib/components/common/Combo.svelte';
    import {get_topics, get_tmllm, get_tmoutputschemas,
            create_topic,create_tmoutputschema, create_tminstruct,
            update_tmchat,update_tminstruct,update_tmoutputschema,update_topic} from "$lib/apis/textmining";

    export let chat_id = ''
    export let instruct_data = {
        instruct_id: '',
        title: '',
        memo: '',
        topic_id: '',
        mining_llm_id:'',
        instruct_prompt:'',
        response_prompt:'',
        schema_id:''
    }
    export let topic_name=''
    let showTopicModal = false;
    
    let topic_head=[
        {id:0,name:"id",type:"text",desc:"ID"},
        {id:1,name:"topic_name",type:"text",desc:"주제명"},
        {id:2,name:"contents",type:"text",desc:"설명"},
    ];

    let topic_data={
        id: '',
        topic_name : '',
        contents:''
    }

    let topic_list = []
    export let selected_topic = ''
    let is_topic_fix = false

    let tmllm_list = []
    export let selected_tmllm = ''

    let schema_list=[]
    let combo_schema_list=[]
    export let selected_schema = ''
    let is_schema_fix = false

    let showSchemaModal = false;
    let schema_head=[
        {id:0,name:"id",type:"text",desc:"ID"},
        {id:1,name:"schema_name",type:"text",desc:"스키마명"},
        {id:2,name:"schema_version",type:"text",desc:"버전"},
        {id:3,name:"schema_desc",type:"text",desc:"설명"},
        {id:4,name:"attr",type:"list",desc:"속성 목록"}
    ];

    let schema_data={
        id : '',
        schema_name:'',
        schema_version:'',
        schema_desc:'',
        attr:[{ seq:0, attr_name: '', attr_type: '', attr_desc: '' }]
    }
    let schema_attr_data=[{ seq:0, attr_name: '', attr_type: '', attr_desc: '' }]

    let attr_type = [
        {value: 'str', name: 'Str'},
        {value: 'int', name: 'Int'},
        {value: 'float', name: 'Float'}
    ];

    function init_data() {

        topic_data={
            id: '',
            topic_name : '',
            contents:''
        }   

        schema_data={
            id : '',
            schema_name:'',
            schema_version:'',
            schema_desc:'',
            attr:[{ seq:0, attr_name: '', attr_type: '', attr_desc: '' }]
        }
    }

    async function get_data(){

        let params = {}

        let topic_success_callback = (json) => {
            json.forEach(item => {
                topic_list = [...topic_list,{value: item.id, name: item.topic_name, contents: item.contents}]
            });
        }

        let tmllm_success_callback = (json) => {
            json.forEach(item => {
                tmllm_list = [...tmllm_list,{value: item.id, name: item.name}]
            });
        }
        
        let schema_success_callback = (json) => {
            json.forEach(item => {
                schema_list = [...schema_list,{value: item.id, 
                                            name: item.schema_name, 
                                            topic: item.topic_id,
                                            schema_version : item.schema_version,
                                            schema_desc: item.schema_desc,
                                            attr: item.attr}]
            });
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        await get_topics(params, topic_success_callback, failure_callback);
        await get_tmllm(params, tmllm_success_callback, failure_callback);
        await get_tmoutputschemas(params, schema_success_callback, failure_callback);
    }

    function addNewRow() {
        schema_data['attr'] = [...schema_data['attr'], {
        seq: schema_data['attr'].length,
        attr_name: '',
        attr_type: '',
        attr_desc: ''
    }];
    }

    function handleInput(event, index, field) {
        const newData = [...schema_data['attr']];
        newData[index][field] = event.target.value;
        schema_data['attr'] = newData;
    }    
    
    const btn_create_topic = async () => {
        let params = {
            topic_name: topic_data['topic_name'],
            contents: topic_data['contents']
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        if (is_topic_fix) {
            console.log('fix')

            params['id'] = selected_topic

            let success_callback = (json) => {
                addToast('info','수정 완료')
                topic_list = topic_list.map(item => {
                    if (item.value == json.id) {
                        return {value: json.id, name: json.topic_name, contents: json.contents}
                    }
                    else {
                        return item
                    }
                })
            }
            await update_topic(params, success_callback, failure_callback);
            
            is_topic_fix = false;
        }
        else {
            let success_callback = (json) => {
                addToast('info','생성 완료')
                showTopicModal = false;
                topic_list = [...topic_list,{value: json.id, name: json.topic_name, contents: json.contents}]
                selected_topic = json.id
            }
            await create_topic(params, success_callback, failure_callback);
        }
    }

    const btn_create_schema = async () => {
        if (instruct_data['topic_id'] == '') {
            addToast('error','주제를 선택해주세요.')
            return;
        }

        if (schema_data['schema_name'] == '') {
            addToast('error','스키마명을 입력해주세요.')
            return;
        }

        if (schema_data['schema_version'] == '') {
            addToast('error','버전을 입력해주세요.')
            return;
        }

        if (schema_data['schema_desc'] == '') {
            addToast('error','설명을 입력해주세요.')
            return;
        }

        if (schema_data['attr'].length == 0) {
            addToast('error','속성을 입력해주세요.')
            return;
        }

        let params = {
            schema_name: schema_data['schema_name'],
            schema_version: schema_data['schema_version'],
            schema_desc: schema_data['schema_desc'],
            topic_id: instruct_data['topic_id'],
            attr: schema_data['attr']
        }

        let success_callback = (json) => {
            addToast('info','생성 완료')
            showSchemaModal = false;
            schema_list = [...schema_list,{value: json.id, name: json.schema_name, 
                topic: json.topic_id, schema_version : json.schema_version, schema_desc: json.schema_desc,attr: json.attr}]
            
            combo_schema_list = schema_list.filter(item => item.topic == instruct_data['topic_id'])
            selected_schema = json.id
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }

        if (is_schema_fix) {
            params['id'] = selected_schema
            is_schema_fix = false;
            
            let success_update_callback = (json) => {
                addToast('info','수정 완료')
                schema_list = schema_list.map(item => {
                    if (item.value == json.id) {
                        return {value: json.id, name: json.schema_name, 
                            topic: json.topic_id, schema_version : json.schema_version, schema_desc: json.schema_desc,attr: json.attr}
                    }
                    else {
                        return item
                    }
                })
            }

            await update_tmoutputschema(params, success_update_callback, failure_callback);
        }
        else {
            await create_tmoutputschema(params, success_callback, failure_callback);
        }

    }

    const btn_create_or_replace_instruct = async () => {

        let params = {
            title: instruct_data['title'],
            memo: instruct_data['memo'],
            topic_id: instruct_data['topic_id'],
            mining_llm_id: instruct_data['mining_llm_id'],
            instruct_prompt: instruct_data['instruct_prompt'],
            response_prompt: instruct_data['response_prompt'],
            output_schema_id: instruct_data['schema_id'],
            chat_id: chat_id
        }

        let success_callback = (json) => {
            addToast('info','지시문 적용 완료')
            instruct_data['instruct_id'] = json.instruct_id
        }

        let failure_callback = (json_error) => {
            addToast('error',json_error.detail)
        }
        
        if (instruct_data['instruct_id'] == '') {
            await create_tminstruct(params, success_callback, failure_callback);
        }
        else {
            params['id'] = instruct_data['instruct_id']
            await update_tminstruct(params, success_callback, failure_callback);
        }
    }

    function showModal(name){
        if(name == 'topic_add'){
            is_topic_fix = false;
            showTopicModal = true;
        }
        else if(name == 'schema_add'){
            if (instruct_data['topic_id'] == '') {
                addToast('error','주제를 선택해주세요.')
                return;
            }
            is_schema_fix = false;
            showSchemaModal = true;
        }
        else if(name == 'topic_fix'){
            is_topic_fix = true;
            showTopicModal = true;
            let tmp_topic = topic_list.find(item => item.value == selected_topic)
            topic_data = {id: selected_topic, topic_name: tmp_topic.name, contents:tmp_topic.contents}

        }
        else if(name == 'schema_fix'){
            if (instruct_data['topic_id'] == '') {
                addToast('error','주제를 선택해주세요.')
                return;
            }
            
            
            is_schema_fix = true;
            showSchemaModal = true;

            let tmp_schema = schema_list.find(item => item.value == selected_schema)
            schema_data = {id: selected_schema, schema_name: tmp_schema.name, schema_version: tmp_schema.schema_version, schema_desc: tmp_schema.schema_desc, attr: tmp_schema.attr}
            
        }   
    }

    onMount(() => {
        get_data();
    });

    $: if (selected_topic) {
        instruct_data['topic_id'] = selected_topic
        
        if(topic_list.length > 0) {
            topic_name  = topic_list.find(item => item.value == selected_topic).name
        }
        else {
            topic_name = ''
        }
        
        if(schema_list.length > 0) {
            combo_schema_list = schema_list.filter(item => item.topic == selected_topic)
        }
    }

    $: if(selected_schema){
        instruct_data['schema_id'] = selected_schema
        if (schema_list.length > 0) {
            schema_attr_data = schema_list.find(item => item.value == selected_schema).attr
        }

    }

    $: if (selected_tmllm) {
        instruct_data['mining_llm_id'] = selected_tmllm
    }

</script>
<div class="instruct-div-scroll">
    <div class="mb-2">
        <FloatingLabelInput style="filled" size="small" type="text" bind:value={instruct_data['title']} disabled >
            지시문 제목
        </FloatingLabelInput>
    </div>
    <div class="mt-1 flex-container">
        <Label class="mr-2">모델</Label>
        <div class="fill-space">
        <Combo underline={true} placeholder="모델 선택" ComboMenu={tmllm_list} bind:selected_name={selected_tmllm}/>
        </div>
    </div>  
    <div class="mt-1">
        <div class="block mb-2 flex justify-between items-center">
            <Label>
                원문
            </Label>
            <div>
                {#if selected_topic}
                    <button id="fix-topic" class="hover-button" on:click={() => {showModal('topic_fix')}} >
                        <EditOutline class="w-4 h-4 text-primary-700" />
                    </button>
                {:else}
                    <button id="fix-topic" class="hover-button" disabled>
                        <EditOutline class="w-4 h-4 text-gray-300" />
                    </button>
                {/if}
                <button id="add-topic" class="hover-button" on:click={() => {showModal('topic_add')}}>
                    <PlusOutline class="w-4 h-4 text-primary-700" />
                </button>
            </div>
            <Tooltip triggeredBy="#fix-topic">수정</Tooltip>
            <Tooltip triggeredBy="#add-topic">추가</Tooltip>
        </div>
        <Combo placeholder="원문 선택" ComboMenu={topic_list} bind:selected_name={selected_topic}/>
    </div>  
    <div class="mt-1">
        <Label class="block mb-">프롬프트 작성</Label>
        <div class="mt-2">
            <Textarea class="min-h-[100px] max-h-[150px]" bind:value={instruct_data['instruct_prompt']} placeholder="명령어 입력" />
        </div>
    </div>
    <div class="mt-1">
        <div class="block mb-2 flex justify-between items-center">
            <Label >스키마
            </Label>
            <div>
                {#if selected_schema}
                    <button id="fix-schema" class="hover-button" on:click={() => {showModal('schema_fix')}}>
                        <EditOutline class="w-4 h-4 text-primary-700" />
                    </button>
                {:else}
                    <button id="fix-schema" class="hover-button" disabled>
                        <EditOutline class="w-4 h-4 text-gray-300" />
                    </button>
                {/if}
                <button id="add-schema" class="hover-button" on:click={() => {showModal('schema_add')}}>
                    <PlusOutline class="w-4 h-4 text-primary-700" />
                </button>
            </div>
            <Tooltip triggeredBy="#fix-schema">수정</Tooltip>
            <Tooltip triggeredBy="#add-schema">추가</Tooltip>
        </div>
        <div>
            <Combo placeholder="스키마 선택" ComboMenu={combo_schema_list} bind:selected_name={selected_schema} />
        </div>
        <div class="mt-1 max-height-scroll">
            <Table class="w-full" shadow>
                <TableHead class="sticky">
                    <TableHeadCell class="text-center">속성명</TableHeadCell>
                    <TableHeadCell class="text-center">타입</TableHeadCell>
                    <TableHeadCell class="text-center">설명</TableHeadCell>
                </TableHead>
                <TableBody>
                {#each schema_attr_data as row, index}
                    <TableBodyRow>
                        <TableBodyCell>
                            {row.attr_name}
                        </TableBodyCell>
                        <TableBodyCell>
                            {row.attr_type} 
                        </TableBodyCell>
                        <TableBodyCell>
                            {row.attr_desc}
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
                </TableBody>
            </Table>
        </div>
    </div>
    <div class="mt-1">
        <Label class="block mb-2">메모</Label>
        <Textarea class="min-h-[50px] max-h-[100px]" bind:value={instruct_data['memo']} placeholder="메모 입력" />
    </div> 
    <Button type="submit" class="w-full" on:click={btn_create_or_replace_instruct}>지시문 적용</Button>
</div>

<!-- 원문 생성 모달 -->
<Modal bind:open={showTopicModal} size="xs" autoclose={true} outsideclose={true} class="w-full" on:close={init_data}>
    <form class="flex flex-col space-y-3" action="#">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">
            {#if is_topic_fix}
                원문 수정
            {:else}
                원문 생성
            {/if}
            </h3>
        <FloatingLabelInput style="filled" id="floating_filled" name="floating_filled" type="text" bind:value={topic_data['topic_name']}>
            {topic_head[1].desc}
        </FloatingLabelInput>
        <Label>
            <P class="block mb-2"> {topic_head[2].desc} </P>
            <Textarea class="min-h-[100px] max-h-[200px]" id="contents" name="contents" bind:value={topic_data['contents']} placeholder="설명 입력" />
        </Label>
        <Button name={"btn_new"} type="submit" class="w-full1" on:click={btn_create_topic}>
        {#if is_topic_fix}
            수정
        {:else}
            저장
        {/if}
        </Button>
    </form>
</Modal>

<!-- 스키마 생성 모달 -->
<Modal bind:open={showSchemaModal} size="md" autoclose={true} outsideclose={true} class="w-full" on:close={init_data}>
    <form class="flex flex-col space-y-3" action="#">
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">
            {#if is_schema_fix}
                스키마 수정
            {:else}
                스키마 생성
            {/if}</h3>
        <div class="flex gap-2">
            <div class="flex-[5]">
                <FloatingLabelInput style="filled" id="floating_filled" name="floating_filled" type="text" bind:value={schema_data['schema_name']}>
                    {schema_head[1].desc}
                </FloatingLabelInput>
            </div>
            <div class="flex-1">
                <FloatingLabelInput  style="filled" id="floating_filled" name="floating_filled" type="text" bind:value={schema_data['schema_version']}>
                    {schema_head[2].desc}
                </FloatingLabelInput>
            </div>
        </div>
        <Label>
            <P class="block mb-2"> {topic_head[2].desc} </P>
            <Textarea class="min-h-[100px] max-h-[200px]" id="contents" name="contents" bind:value={schema_data['schema_desc']} placeholder="설명 입력" />
        </Label>

        <div class="relative overflow-x-auto w-full" >
            <div class="min-h-[300px] max-h-[300px] overflow-y-auto">
                <Table class="w-full">
                    <TableHead class="sticky">
                        <TableHeadCell class="w-[40px] text-center">
                            <button class="hover-button" on:click={addNewRow}>
                                <PlusOutline class="w-4 h-4 text-primary-700" />
                            </button>
                        </TableHeadCell>
                        <TableHeadCell class="w-[30%] text-center">속성명</TableHeadCell>
                        <TableHeadCell class="w-[20%] text-center">타입</TableHeadCell>
                        <TableHeadCell class="w-[calc(50%-40px)] text-center">설명</TableHeadCell>
                    </TableHead>
                    <TableBody>
                    {#each schema_data['attr'] as row, index}
                        <TableBodyRow>
                            <TableBodyCell class="text-center">
                                {index}
                            </TableBodyCell>
                            <TableBodyCell>
                                <FloatingLabelInput type="text" value={row.attr_name}
                                on:input={(e) => handleInput(e, index, 'attr_name')} 
                                class="w-full" />
                            </TableBodyCell>
                            <TableBodyCell>
                                <Select underline size="md"  placeholder="" value={row.attr_type} items={attr_type} 
                                on:change={(e) => handleInput(e, index, 'attr_type')}
                                class="w-full"  />
                            </TableBodyCell>
                            <TableBodyCell>
                                <FloatingLabelInput type="text" value={row.attr_desc}
                                on:input={(e) => handleInput(e, index, 'attr_desc')} 
                                class="w-full" />
                            </TableBodyCell>
                        </TableBodyRow>
                    {/each}
                    </TableBody>
                </Table>
            </div>
        </div>    
        <Button name={"btn_new"} type="submit" class="w-full1" on:click={btn_create_schema}>
        {#if is_schema_fix}
            수정
        {:else}
            저장
        {/if}
        </Button>
    </form>
</Modal>


<style>
    .hover-button:hover :global(.text-primary-700) {
        /* 색상 반전 효과 */
        filter: invert(1);
    }
  .flex-container {
    display: flex;
    align-items: center;
  }
  .fill-space {
    flex-grow: 1;
  }
  .max-height-scroll {
    min-height: 100px; /* 원하는 최대 높이로 설정 */
    max-height: 250px; /* 원하는 최대 높이로 설정 */
    overflow-y: auto;
  }
  .instruct-div-scroll {
    max-height: 800px; /* 원하는 최대 높이로 설정 */
    overflow-y: auto;
  }
  
</style>