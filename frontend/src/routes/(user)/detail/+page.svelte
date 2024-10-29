<script>
    import { goto } from '$app/navigation';
    import { update_detail,get_userdetail } from "$lib/apis/user";
    import { Input, Label, Toggle, Button, Checkbox, A } from 'flowbite-svelte';
    import InterestsInput from '$lib/components/detail/InterestsInput.svelte';
    import { onMount } from 'svelte';
    import { addToast } from '$lib/common';
    let error = {detail:[]}
    let name = ""
    let age = 0
    let discord_yn = false
    let email_yn = false
    let interests = []
    let data_loaded = false

    async function get_data()
    {
      let params = {}
      let success_callback = (json) => {
        if (json != null) {
          data_loaded = true
        }
        name = json.name
        age = json.age
        discord_yn = json.discord_yn
        email_yn = json.email_yn
        interests = json.interests ? json.interests.split('|') : []

      }

      let failure_callback = (json_error) => {
        error = json_error
      addToast('error',error.detail)
      }

      await get_userdetail(params,success_callback, failure_callback)
    }

    onMount(async () => {
      await get_data()
    })


    const handleSubmit = async () => {
      let params = {
          "name": name,
          "age": age,
          "discord_yn": discord_yn,
          "email_yn": email_yn,
          "interests": interests.join('|'),
        }

        let success_callback = (json) => {
          addToast('info',"수정이 완료되었습니다.")
          get_data()
        }

        let failure_callback = (json_error) => {
          error = json_error
          addToast('error',error.detail)
        }
          await update_detail(params, success_callback, failure_callback);
      }

</script>

<div class="form-container">
  <form method="post" class="form-layout">
  
  <div class="grid gap-6 mb-6 md:grid-cols-2">
    <div>
      <Label for="name" class="mb-2">이름</Label>
      <Input type="text" id="name" placeholder="홍길동" required bind:value={name}/>
    </div>
    <div>
      <Label for="age" class="mb-2">나이</Label>
      <Input type="number" id="age" placeholder=0 required bind:value={age}/>
    </div>
  </div>
  <div class="grid gap-6 mb-6 md:grid-cols-2">
    <div>
      <Toggle bind:checked={discord_yn}>Discord 수신여부</Toggle>
    </div>
    <div>
      <Toggle bind:checked={email_yn}>Email 수신여부</Toggle>
    </div>
  </div>
  <div>
    <InterestsInput bind:interests={interests} />
  </div>

  <Button on:click={handleSubmit}>수정</Button>
</form>
</div>