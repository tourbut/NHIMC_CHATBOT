<script>
    import Table from '$lib/components/common/Table.svelte';
    import { Tabs, TabItem } from 'flowbite-svelte';

    import { get_llm, get_dept, get_apikey,get_deptllm,get_deptusage,
             create_llm,create_apikey,create_deptllm,
             update_llm, update_apikey,update_deptllm } from "$lib/apis/admin";

    import {get_tmllm,create_tmllm} from "$lib/apis/textmining";
    import { onMount } from 'svelte';
    import { addToast } from '$lib/common';
    let table_head=[
      {id:0,name:"source",type:"string",desc:"출처"},
      {id:1,name:"type",type:"string",desc:"타입"},
      {id:2,name:"name",type:"string",desc:"모델명"},
      {id:3,name:"description",type:"string",desc:"설명"},
      {id:4,name:"input_price",type:"number",desc:"Input Price"},
      {id:5,name:"output_price",type:"number",desc:"Output Price"},
      {id:6,name:"url",type:"string",desc:"URL"},
      {id:7,name:"is_active",type:"boolean",desc:"활성화여부"}
    ]

    let api_table_head=[
      {id:0,name:"dept_id",type:"combo",desc:"부서명",combo:[]},
      {id:1,name:"api_name",type:"string",desc:"API명"},
      {id:2,name:"api_key",type:"password",desc:"Key"},
      {id:3,name:"active_yn",type:"boolean",desc:"활성화여부"},
    ];
    
    let llm_table_head=[
      {id:0,name:"dept_id",type:"combo",desc:"부서명",combo:[]},
      {id:1,name:"llm_id",type:"combo",desc:"모델",combo:[]},
      {id:2,name:"api_id",type:"combo_password",desc:"Key",combo:[]},
      {id:3,name:"active_yn",type:"boolean",desc:"활성화여부"},
    ]

    let tmllm_table_head=[
      {id:0,name:"llm_id",type:"combo",desc:"모델",combo:[]},
      {id:1,name:"active_yn",type:"boolean",desc:"활성화여부"},
    ]

    let api_table_body=[];
    let llm_table_body=[];
    let tmllm_table_body=[];


    let table_body=[]
    let form_data={}
    let formModal = false;

    let combo_dept = []
    
    async function get_data()
    {
      let params = {}

      let success_callback = (json) => {
        table_body = json
      }

      let dept_success_callback = (json) => {
        combo_dept = json.map(item => {return {value:item.id,name:item.dept_nm}})
        api_table_head[0].combo=combo_dept
      }

      let api_success_callback = (json) => {
        api_table_body = json.map(item => {
          
          return {
            id:item.id,
            dept_id:combo_dept.find(dept => dept.value==item.dept_id).name,
            api_name:item.api_name,
            api_key:item.api_key,
            active_yn:item.active_yn
          }
        }) 
      }

      let deptllm_success_callback = (json) => {
        
        llm_table_head[0].combo=combo_dept
        llm_table_head[1].combo=table_body.map(item => {return {value:item.id,name:item.name}})
        llm_table_head[2].combo=api_table_body.filter(item => item.active_yn).map(item => {return {value:item.id,name:item.api_key,dept_id:item.dept_id}})


        llm_table_body = json.map(item => {
          
          return {
            id:item.id,
            dept_id:combo_dept.find(dept => dept.value==item.dept_id).name,
            llm_id:table_body.find(llm => llm.id==item.llm_id).name,
            api_id:api_table_body.find(api => api.id==item.api_id).api_key,
            active_yn:item.active_yn
          }
        }) 
      }

      let tmllm_success_callback = (json) => {
        tmllm_table_head[0].combo=table_body.map(item => {return {value:item.id,name:item.name}})
        tmllm_table_body = json.map(item => {
          
          return {
            id:item.id,
            llm_id:table_body.find(llm => llm.id==item.llm_id).name,
            active_yn:item.active_yn
          }
        }) 
      } 

      let failure_callback = (json_error) => {
        addToast('error',json_error.detail)
      }

      await get_llm(params,success_callback, failure_callback)
      await get_dept(params,dept_success_callback, failure_callback)
      await get_apikey(params,api_success_callback, failure_callback)
      await get_deptllm(params,deptllm_success_callback, failure_callback)
      await get_tmllm(params,tmllm_success_callback, failure_callback)
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

      if (event.target.id == 0) //모델
      { 
        if(event.target.name=="btn_new")
        { 
          await create_llm(params,success_callback, failure_callback)
        }
        else
        {
          await update_llm(params,success_callback, failure_callback)
        }
      }
      else if (event.target.id == 1) //부서 API
      {
        if(event.target.name=="btn_new")
        { 
          await create_apikey(params,success_callback, failure_callback)
        }
        else
        {
          await update_apikey(params,success_callback, failure_callback)
        }
      }
      else if (event.target.id == 2) //부서별 모델
      {
        if(event.target.name=="btn_new")
        { 
          await create_deptllm(params,success_callback, failure_callback)
        }
        else
        {
          await update_deptllm(params,success_callback, failure_callback)
        }
      }
      else if (event.target.id == 3) //텍스트마이닝 모델
      {
        if(event.target.name=="btn_new")
        { 
          await create_tmllm(params,success_callback, failure_callback)
        }
        else
        {
          await update_tmllm(params,success_callback, failure_callback)
        }
      }
    }

    //form_data의 dept_id가 변경될때 해당 되는 api_key만 재정렬
    $: if (form_data.dept_id)
    {
      llm_table_head[2].combo=api_table_body.filter(item => item.dept_id==combo_dept.find(dept => dept.value==form_data.dept_id).name).map(item => {return {value:item.id,name:item.api_key,dept_id:item.dept_id}})
    }

</script>
<div class="form-page">
    <Tabs>
      <TabItem open title="모델">
        <Table btn_id=0 btn_click={onsubmit} table_head={table_head} is_editable={true}  
               bind:table_body={table_body} bind:form_data={form_data} 
               bind:formModal={formModal}/>
      </TabItem>
      <TabItem title="부서 API 등록">
        <Table btn_id=1 btn_click={onsubmit} is_editable={true} is_combo_modal={true}
               bind:table_head={api_table_head} bind:table_body={api_table_body} 
               bind:form_data={form_data} bind:formModal={formModal}/>
      </TabItem>
      <TabItem title="부서별 모델 설정">
          <Table btn_id=2 btn_click={onsubmit} is_combo_modal={true} is_editable={true} 
                 bind:table_head={llm_table_head} bind:table_body={llm_table_body} bind:form_data={form_data} bind:formModal={formModal}/>
      </TabItem> 
      <TabItem title="텍스트마이닝 모델 설정">
          <Table btn_id=3 btn_click={onsubmit} is_combo_modal={true} is_editable={true} 
                 bind:table_head={tmllm_table_head} bind:table_body={tmllm_table_body} bind:form_data={form_data} bind:formModal={formModal}/>
      </TabItem> 
    </Tabs>
    
</div>