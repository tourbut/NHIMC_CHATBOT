<script>
    import { Select, Dropdown, DropdownItem } from 'flowbite-svelte';
    import { ChevronDownOutline } from 'flowbite-svelte-icons';

    let selected_item="선택하세요.";

    export let ComboMenu = [
      { drop_value:'us',value: 'CA', name: 'Californiass' },
      { drop_value:'us',value: 'TX', name: 'Texas' },
      { drop_value:'us',value: 'WH', name: 'Washinghton' },
      { drop_value:'ca',value: 'FL', name: 'Florida' },
      { drop_value:'ca',value: 'VG', name: 'Virginia' },
      { drop_value:'fr',value: 'GE', name: 'Georgia' },
      { drop_value:'fr',value: 'MI', name: 'Michigan' }
    ];
    export let is_dropcombo=false
    export let selected_name
    export let placeholder = "선택하세요."
    export let underline = false
    let drop_items = ComboMenu.filter((item, index, self) =>
      index === self.findIndex((t) => (
        t.drop_value === item.drop_value
      ))
    );
    
    let select_menu=[]
    let selected_value=""
    
    function handleSelect(event) {
      selected_item = event.target.innerText;
      select_menu = ComboMenu.filter(item => item.drop_value === selected_item);
      selected_name=select_menu[0].value;
    }


  </script>
  
  {#if is_dropcombo}
  <div class="flex">
    <button id="states-button" class="flex-shrink-0 z-10 inline-flex items-center py-2.5 px-4 text-sm font-medium text-center text-gray-500 bg-gray-100 border border-gray-300 rounded-s-lg hover:bg-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-700 dark:text-white dark:border-gray-600" type="button">
      {selected_item}
      <ChevronDownOutline class="w-6 h-6 ms-2" />
    </button>

    <Dropdown triggeredBy="#states-button">
      {#each drop_items as item}
      <DropdownItem class="flex items-center" on:click={handleSelect}>
       {item.drop_value}
      </DropdownItem>
      {/each} 
    </Dropdown>
    <Select underline={underline} placeholder={placeholder} items={select_menu} class="!rounded-s-none" bind:value={selected_name} />
  </div>
  {:else}
  <div>
    <Select underline={underline} placeholder={placeholder} items={ComboMenu} class="!rounded-s-none" bind:value={selected_name}/>
  </div>
  {/if}
