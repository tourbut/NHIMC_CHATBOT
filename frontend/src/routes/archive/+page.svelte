<script>
    import { Button, Spinner } from "flowbite-svelte";
    import { Hr} from 'flowbite-svelte';
    import { Card,Label, NumberInput, Textarea} from 'flowbite-svelte';
    import { Tabs, TabItem, P } from 'flowbite-svelte';
    import MarkdownViewer from "$lib/components/archive/MarkdownViewer.svelte";
    import { addToast } from '$lib/common';

    import Sidebar from "$lib/components/common/Sidebar.svelte";
    import FileUploader from "$lib/components/archive/FileUploader.svelte";
    import { onMount } from 'svelte';
    import { upload_flies, delete_file, get_file, download_file} from "$lib/apis/archive";

    let file_list = []
    let dataLoaded = false
    let error = {detail:[]}
    let loading = false;
    let document_content = "Content will be displayed here"

    let files = null;
    let file_value = null;

    let file = {
        name: '',
        description: '',
        ext:'',
        separators:["<*sp*>","\n\n"],
        chunk_size:1000,
        chunk_overlap:250,
        child_chunk_size:100,
        child_chunk_overlap:20
      }

    function get_data()
    {
      let params = {}

      let success_callback = (json) => {
        
        console.log(json)
      }

      let failure_callback = (json_error) => {
        error = json_error
        loading = false;
        addToast('error',error.detail)
      }

      //get_archive_list(params,success_callback, failure_callback)
    }

    onMount( () => {
        get_data()
    })

    const onclick_sidebar = async (id) => {
      
      if (id =='') {
        return
      }
      
      let params = {
        
      }

      let success_callback = (json) => {

        file.name = json.file_name
        file.ext = json.file_ext
        document_content = json.contents.join('\n')

      }
  
      let failure_callback = (json_error) => {
        error = json_error
        loading = false;
        addToast('error',error.detail)
      }
      await get_file(id,params, success_callback, failure_callback);

    }

    const onclick_more = async (id) =>
    {
      if (id =='') {
        return
      }

      let params = {
        id: id
      }

      let success_callback = (json) => {
        addToast('info','삭제 완료')

        file_list.forEach(item => {
          item.items = item.items.filter(item => item.id != id)
        });
      }

      let failure_callback = (json_error) => {
        error = json_error
        loading = false;
        addToast('error',error.detail)
      }
      await delete_file(params, success_callback, failure_callback);
    }

    const onclick_download = async() => {

      let success_callback = (json) => {
        addToast('info','다운로드 완료')
      }

      let failure_callback = (json_error) => {
        error = json_error
        loading = false;
        addToast('error',error.detail)
      }

      await download_file(archive_id,file, success_callback, failure_callback);

    }

    const file_upload = async () => {

      if (files == null) {
        addToast('warning','파일을 선택해주세요.')
        return
      }

      let file_ext = files[0].name.split('.').pop().toLowerCase();

      if (!['txt','TXT','pdf','PDF','xlsx','XLSX','csv','CSV','md'].includes(file_ext)) {
        addToast('warning','지원하지 않는 파일 형식입니다.')
        return
      }

      if (loading == true) {
        addToast('warning','파일 업로드 중입니다.')
        return
      }
      loading = true;

      file.name = files[0].name
      file.ext = file_ext

      let params = {
        file_name: file.name,
        file_desc: file.description,
        separators:["<*sp*>"],
        chunk_size:file.chunk_size,
        chunk_overlap:file.chunk_overlap,
        child_chunk_size:file.child_chunk_size,
        child_chunk_overlap:file.child_chunk_overlap
      }

      let success_callback = (json) => {
        addToast('info','업로드 완료')
        loading = false;
      }
  
      let failure_callback = (json_error) => {
        error = json_error
        loading = false;
        addToast('error',error)
      }

      await upload_flies(params,files[0], success_callback, failure_callback);
    }

</script>

<div class="container">
  <div>
    {#if dataLoaded}
        <Sidebar bind:side_menus={file_list} btn_click={onclick_sidebar} btn_item_more_click={onclick_more}/>
    {/if}
  </div>
  <div class="content">
    <div class="mx-auto p-1 max-w-sm">
      <Tabs contentClass="">
        <TabItem open={true}>
          <span slot="title">파일</span>
          <Card>
            <div>
              <Label for="file" class="mb-2">파일 업로드</Label>
              <FileUploader bind:files={files} bind:value={file_value} />
              <Textarea bind:value={file.description} placeholder="파일 설명" class="mt-2"/>
              <div class="flex items-center justify-between">
                <Label class="space-y-2 mb-4">
                  Chunk Size
                  <NumberInput bind:value={file.chunk_size} class="mt-2"/>
                </Label>
                <Label class="space-y-2 mb-4">
                  Chunk Overlap
                  <NumberInput bind:value={file.chunk_overlap} class="mt-2"/>
                </Label>
              </div>
              <div class="flex items-center justify-between">
                <Label class="space-y-2 mb-4">
                  Separators
                  <Textarea bind:value={file.separators} class="mt-2"/>
                </Label>
                <Label class="space-y-2 mb-4">
                  Child Chunk Size
                  <NumberInput bind:value={file.child_chunk_size} class="mt-2"/>
                </Label>
                <Label class="space-y-2 mb-4">
                  Child Chunk Overlap
                  <NumberInput bind:value={file.child_chunk_overlap} class="mt-2"/>
                </Label>
              </div>
              <Button on:click={file_upload}>Upload</Button>
            </div>
          </Card>
        </TabItem>
      </Tabs>
    </div>
    
    <Hr hrClass="h-px my-1 bg-gray-200 border-0 dark:bg-gray-700"/>
    
    <div class="form-tabs">

      <MarkdownViewer bind:markdown={document_content} bind:loading={loading} onclick_download={onclick_download}/>
     
    </div>  
  </div> 
</div>


<style>
  .container {
    display: flex;
    min-height: 100vh /* 브라우저 높이와 동일하게 설정 */
  }
  .content {
    flex: 1; /* 남은 공간을 차지하도록 설정 */
    padding: 0rem; /* 콘텐츠 패딩 설정 */
  }
</style>