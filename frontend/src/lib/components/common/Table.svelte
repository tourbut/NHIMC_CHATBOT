<script>
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    import { Button, Label, Input, FloatingLabelInput , Checkbox } from 'flowbite-svelte';
    import { Toolbar, ToolbarButton, ToolbarGroup } from 'flowbite-svelte';
    import { PlusOutline } from 'flowbite-svelte-icons';
    import Modal from '$lib/components/common/Modal.svelte';
    import Combo_Modal from '$lib/components/common/Combo_Modal.svelte';

    export let table_head=[
        {id:0,name:"col1",type:"string",desc:"샘플컬럼1"},
        {id:1,name:"col2",type:"boolean",desc:"샘플컬럼2"}
    ];

    export let table_body=[];
    export let is_editable=false;
    export let btn_click;
    export let form_data={}
    export let formModal = false;
    export let btn_id=0;
    export let is_combo_modal=false;
    export let is_plus=true;
    let is_new=false;


    function btn_edit(data)  {
        form_data=data;
        for (let i=0; i<table_head.length; i++)
        {
            if (table_head[i].type === 'combo')
            {
                for (let j=0; j<table_head[i].combo.length; j++)
                {
                    if (table_head[i].combo[j].name === data[table_head[i].name])
                    {
                        form_data[table_head[i].name]=table_head[i].combo[j].value;
                    }
                }
            }
        }
        formModal = true;
        is_new=false;
    }


</script>

<div>
    {#if (is_plus)}
    <div>
    <Toolbar style="background-color: transparent;">
        <ToolbarButton on:click={() => (formModal = true, is_new=true)}><PlusOutline class="w-4 h-4" /></ToolbarButton>
    </Toolbar>
    </div>
    {/if}
    <div>
    <Table hoverable={true}>
        <TableHead>
            {#each table_head as item}
                <TableHeadCell class="text-center" padding="px-3 py-3">{item.desc}</TableHeadCell>
            {/each}
            {#if is_editable}
                <TableHeadCell class="text-center" padding="px-3 py-3"></TableHeadCell>
            {/if}
        </TableHead>
        <TableBody tableBodyClass="divide-y">
            {#each table_body as item}
                <TableBodyRow>
                    {#each table_head as head}
                    {#if (head.type === 'boolean')}
                    <TableBodyCell class="text-center">
                        <Checkbox disabled bind:checked={item[head.name]} />
                    </TableBodyCell>
                    {:else if (head.type === 'integer')}
                    <TableBodyCell class="text-right">{item[head.name].toLocaleString()}</TableBodyCell>
                    {:else if (head.type === 'float')}
                    <TableBodyCell class="text-right">{item[head.name].toFixed(6)}</TableBodyCell>
                    {:else if (head.type === 'date')}
                    <TableBodyCell class="text-center">{new Date(item[head.name]).toLocaleDateString()}</TableBodyCell>
                    {:else}
                    <TableBodyCell class="text-center">{item[head.name]}</TableBodyCell>
                    {/if}
                    {/each}
                    {#if is_editable}
                        <TableBodyCell>
                            <button on:click={btn_edit(item)} class="font-medium text-primary-600 hover:underline dark:text-primary-500">
                                Edit
                            </button>
                        </TableBodyCell>
                    {/if}
                </TableBodyRow>
            {/each}
        </TableBody>
    </Table>
    </div>
</div>
{#if (is_combo_modal)}
<Combo_Modal bind:is_new={is_new} bind:table_head={table_head} bind:formModal={formModal} 
             bind:form_data={form_data} bind:btn_id={btn_id} btn_click={btn_click}/>
{:else}
<Modal bind:is_new={is_new} bind:table_head={table_head} bind:formModal={formModal} 
       bind:form_data={form_data} bind:btn_id={btn_id} btn_click={btn_click}/>
{/if}