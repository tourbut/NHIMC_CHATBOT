<script>
    import { Tabs, TabItem } from 'flowbite-svelte';
    import Table from '$lib/components/common/Table.svelte';
    import { addToast } from '$lib/common';
    import { onMount } from 'svelte';
    import { get_apikey,get_userllm,get_llm} from "$lib/apis/settings";
    import { create_apikey, update_apikey, create_userllm, update_userllm} from '$lib/apis/settings';
    
    let form_data={}
    let formModal = false;
    let api_table_body=[];
    let llm_table_body=[];

    let api_table_head=[
      {id:0,name:"api_name",type:"string",desc:"API명"},
      {id:1,name:"api_key",type:"string",desc:"Key"},
      {id:2,name:"active_yn",type:"boolean",desc:"활성화여부"},
    ];
    
    let llm_table_head=[
      {id:0,name:"name",type:"combo",desc:"모델",combo:[]},
      {id:1,name:"api_key",type:"combo",desc:"Key",combo:[]},
      {id:2,name:"active_yn",type:"boolean",desc:"활성화여부"},
    ]

    async function get_data()
    {
      let params = {}

      let success_callback_llm = (json) => {
        let combo_llm = json.map(item => {return {value:item.id,name:item.name}})
        llm_table_head[0].combo=combo_llm
      }
      let success_callback_api = (json) => {
        api_table_body = json
        let combo_api = json.map(item => {return {value:item.id,name:item.api_key}})
        llm_table_head[1].combo=combo_api
      }
      let success_callback_userllm = (json) => {
        llm_table_body = json
      }
      let failure_callback = (json_error) => {
        addToast('error',json_error.detail)
      }

      await get_llm(params,success_callback_llm, failure_callback)
      await get_apikey(params,success_callback_api, failure_callback)
      await get_userllm(params,success_callback_userllm, failure_callback)
    }

    onMount(async () => {
      await get_data()
    })

    onsubmit = async (event) => {
      event.preventDefault();

      let params = form_data

      let success_callback = (json) => {
        addToast('success','저장되었습니다.')
        get_data()
        formModal = false
      }

      let failure_callback = (json_error) => {
        addToast('error',json_error.detail[0].msg)
      }

      if (Object.keys(params).length==0)
      {
        addToast('error','값을 입력해주세요.')
        return
      }
      if(event.target.name=="btn_new")
      { 
        if (event.target.id == 0)
        {
            await create_apikey(params,success_callback, failure_callback)
        }
        else if (event.target.id == 1)
        {
          params={
                  llm_id:params.name,
                  api_id:params.api_key,
                  active_yn:params.active_yn
                }
          await create_userllm(params,success_callback, failure_callback)
        }
      }
      else
      {  if (event.target.id == 0)
        {
            await update_apikey(params,success_callback, failure_callback)
        }
        else if (event.target.id == 1)
        {
          params={
                  id:params.id,
                  llm_id:params.name,
                  api_id:params.api_key,
                  active_yn:params.active_yn
                }
          await update_userllm(params,success_callback, failure_callback)
        }
      }
    }

</script>
<div class='form-tabs'>  
    <Tabs>
        <TabItem open title="API 등록">
            <Table btn_id=0 btn_click={onsubmit} is_editable={true} 
                   bind:table_head={api_table_head} bind:table_body={api_table_body} bind:form_data={form_data} bind:formModal={formModal}/>
        </TabItem>
        <TabItem title="모델설정">
            <Table btn_id=1 btn_click={onsubmit} is_combo_modal={true} is_editable={true} 
                   bind:table_head={llm_table_head} bind:table_body={llm_table_body} bind:form_data={form_data} bind:formModal={formModal}/>
        </TabItem> 
    </Tabs>
</div>