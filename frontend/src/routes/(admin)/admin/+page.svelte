<script>
    import Table from '$lib/components/common/Table.svelte';
    import { Tabs, TabItem } from 'flowbite-svelte';

    import { get_llm, create_llm,update_llm } from "$lib/apis/admin";
    import { onMount } from 'svelte';
    import { addToast } from '$lib/common';
    let table_head=[
      {id:0,name:"source",type:"string",desc:"출처"},
      {id:1,name:"type",type:"string",desc:"타입"},
      {id:2,name:"name",type:"string",desc:"모델명"},
      {id:3,name:"description",type:"string",desc:"설명"},
      {id:4,name:"input_price",type:"number",desc:"Input Price"},
      {id:5,name:"output_price",type:"number",desc:"Output Price"},
      {id:6,name:"is_active",type:"boolean",desc:"활성화여부"}
    ]

    let table_body=[]
    let form_data={}
    let formModal = false;

    async function get_data()
    {
      let params = {}

      let success_callback = (json) => {
        table_body = json
      }

      let failure_callback = (json_error) => {
        addToast('error',json_error.detail)
      }

      await get_llm(params,success_callback, failure_callback)
    }
    
    onMount(async () => {
      await get_data()
    })

    onsubmit = async (event) => {
      event.preventDefault();
      let params = form_data
      formModal = false
      form_data = {}

      let success_callback = (json) => {
        addToast('success','저장되었습니다.')
        get_data()
      }

      let failure_callback = (json_error) => {
        addToast('error',json_error.detail)
      }

      if (Object.keys(params).length==0)
      {
        addToast('error','값을 입력해주세요.')
        return
      }

      if(event.target.name=="btn_new")
      { 
        await create_llm(params,success_callback, failure_callback)
      }
      else
      {
        await update_llm(params,success_callback, failure_callback)
      }
    }

</script>
<div class="form-tabs">
    <Tabs>
      <TabItem open title="모델">
        <Table btn_click={onsubmit} table_head={table_head} bind:table_body={table_body} is_editable={true} bind:form_data={form_data} bind:formModal={formModal}/>
      </TabItem>
    </Tabs>
    
</div>