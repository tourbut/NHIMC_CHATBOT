<script>
    import { Button } from "flowbite-svelte";
    import { Card,Label, NumberInput, Textarea} from 'flowbite-svelte';
    import { Tabs, TabItem, P } from 'flowbite-svelte';
    import { addToast } from '$lib/common';

    import Table from '$lib/components/common/Table.svelte';
    import FileUploader from "$lib/components/archive/FileUploader.svelte";
    import { onMount } from 'svelte';
    import { upload_flies,get_file_list} from "$lib/apis/archive";

    let file_table_head=[
      {id:0,name:"file_name",type:"string",desc:"파일명"},
      {id:1,name:"file_size",type:"string",desc:"파일 크기"},
      {id:2,name:"file_ext",type:"string",desc:"파일 확장자"},
      {id:3,name:"file_desc",type:"string",desc:"파일 설명"},
      {id:3,name:"embedding_yn",type:"boolean",desc:"임베딩여부"},
    ]
    let file_table_body=[];

    let error = {detail:[]}
    let loading = false;
    let form_data={}
    let formModal = false;

    let files = null;
    let file_value = null;

    let file = {
        name: '',
        description: '',
        ext:'',
        separators:"<*sp*>,\n\n",
        chunk_size:1000,
        chunk_overlap:250,
        child_chunk_size:100,
        child_chunk_overlap:20
      }

    function get_data()
    {
      let params = {}

      let success_callback = (json) => {
        
        file_table_body = json
      }

      let failure_callback = (json_error) => {
        error = json_error
        loading = false;
        addToast('error',error.detail)
      }

      get_file_list(params,success_callback, failure_callback)
    }

    onMount( () => {
        get_data()
    })

    const file_upload = async () => {

      if (files == null) {
        addToast('warning','파일을 선택해주세요.')
        return
      }

      let file_ext = files[0].name.split('.').pop().toLowerCase();

      if (!['txt','TXT','pdf','PDF','xlsx','XLSX','csv','CSV','md','docx','DOCX'].includes(file_ext)) {
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
      console.log(file.separators)
      let params = {
        file_name: file.name,
        file_desc: file.description,
        separators:file.separators,
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
<div class="form-tabs">
  <Tabs>
    <TabItem open title="모델">
      <Table btn_id=0 btn_click={onsubmit} table_head={file_table_head} is_plus={false}  
               bind:table_body={file_table_body} bind:form_data={form_data} 
               bind:formModal={formModal} />
    </TabItem>
    <TabItem title="업로드">
      <div class="container">
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
        </div> 
      </div>
    </TabItem>
  </Tabs>

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