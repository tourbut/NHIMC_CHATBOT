<script>
    import { Button, Modal, Label, Input, FloatingLabelInput , Checkbox } from 'flowbite-svelte';
    export let table_head=[
        {id:0,name:"col1",type:"string",desc:"샘플컬럼1"},
        {id:1,name:"col2",type:"boolean",desc:"샘플컬럼2"}
    ];

    export let btn_click;
    export let form_data={}
    export let formModal = false;
    export let btn_id=0;
    
    export let is_new=false;

</script>

<Modal bind:open={formModal} size="xs" autoclose={false} outsideclose={true} class="w-full" on:close={() => form_data={}}>
    <form class="flex flex-col space-y-3" action="#">
        {#if (is_new)}
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">항목 추가</h3>
        {:else}
        <h3 class="mb-4 text-xl font-medium text-gray-900 dark:text-white">항목 수정</h3>
        {/if}
        {#each table_head as head}
            {#if (head.type === 'boolean')}
            <Label class="text-gray-500 dark:text-gray-400 mt-4 flex items-center">
                {head.desc} <Checkbox class="ms-2" bind:checked={form_data[head.name]}  />
            </Label>
            {:else}
                <FloatingLabelInput style="filled" id="floating_filled" name="floating_filled" type="text" bind:value={form_data[head.name]}>
                    {head.desc}
                </FloatingLabelInput>
            {/if}
        {/each}
      <Button bind:id={btn_id} name={is_new ? "btn_new":"btn_update"} type="submit" class="w-full1" on:click={btn_click}>저장</Button>
    </form>
</Modal>