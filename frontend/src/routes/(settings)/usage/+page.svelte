<script>
    import { Tabs, TabItem } from 'flowbite-svelte';
    import { addToast } from '$lib/common';
    import { onMount } from 'svelte';
    import { get_userusage} from "$lib/apis/settings";
    import Table from '$lib/components/common/Table.svelte';
    import Combo from '$lib/components/common/Combo.svelte';

    let usage_table_head=[
      {id:0,name:"usage_date",type:"string",desc:"이용일자"},
      {id:1,name:"name",type:"string",desc:"사용자"},
      {id:2,name:"source",type:"string",desc:"출처"},
      {id:3,name:"llm_name",type:"string",desc:"모델명"},
      {id:4,name:"input_token",type:"integer",desc:"Input Token"},
      {id:5,name:"output_token",type:"integer",desc:"Output Token"},
      {id:6,name:"cost",type:"float",desc:"비용"},
    ];

    let ComboMenu = [
      { value: 'day', name: '일별 사용량' },
      { value: 'month', name: '월별 사용량' },
    ]
    
    let query_type = 'day'

    let usage_day=[];
    let usage_month=[];
    let usage_table_body=[];
    
    async function get_data()
    {
      let params = {}

      let success_callback = (json) => { 
        usage_day = json.map((item) => {
          return {
            usage_date: item.usage_date.substring(0,10),
            name: item.name,
            source: item.source,
            llm_name: item.llm_name,
            input_token: item.input_token,
            output_token: item.output_token,
            cost: item.cost
          }
        })

        usage_month = json.map((item) => {
          return {
            usage_date: item.usage_date.substring(0,7),
            name: item.name,
            source: item.source,
            llm_name: item.llm_name,
            input_token: item.input_token,
            output_token: item.output_token,
            cost: item.cost
          }
        })

        //usage_month를 usage_date , source, name으로 groupby해서 cost, token을 합산
        let result = usage_month.reduce((acc, item) => {
          let key = item.usage_date + item.source + item.name
          if (acc[key]) {
            acc[key].cost += item.cost
            acc[key].input_token += item.input_token
            acc[key].output_token += item.output_token
          } else {
            acc[key] = {
              usage_date: item.usage_date,
              name: item.name,
              source: item.source,
              llm_name: item.llm_name,
              cost: item.cost,
              input_token: item.input_token,
              output_token: item.output_token
            }
          }
          return acc
        }, {})
        usage_month = Object.values(result)

      }

      let failure_callback = (json_error) => {
        addToast('error',json_error.detail)
      }

      await get_userusage(params,success_callback, failure_callback)
    }
    onMount(async () => {
      await get_data()
    })

    $: if (query_type == 'day')
    {
        usage_table_head[0].desc = '이용일자'
        usage_table_body = usage_day
    }
    else
    {
        usage_table_head[0].desc = '이용월'
        //같은 월끼리 token cost sum

        usage_table_body=usage_month

    }

</script>
<div class='form-tabs'>  
    <Tabs>
        <TabItem open title="비용">
            <Combo bind:ComboMenu={ComboMenu} bind:selected_name={query_type} />
            <Table is_plus={false} bind:table_head={usage_table_head} bind:table_body={usage_table_body}/>
        </TabItem>
    </Tabs>
</div>