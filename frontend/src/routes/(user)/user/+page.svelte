<script>
  import { Input, Label, Toggle, Button, Checkbox, A } from 'flowbite-svelte';
  import { goto } from '$app/navigation';
  import { post_user} from "$lib/apis/user";
  import InterestsInput from '$lib/components/detail/InterestsInput.svelte';
  import { addToast } from '$lib/common';
  let error = {detail:[]}
  //User info
  let empl_no = ''
  let name = ""
  let password1 = ''
  let password2 = ''
  let dept_cd = ''

  const handleSubmit = async () => {

    if (password1 !== password2) {
      error={detail: "비밀번호가 일치하지 않습니다."}
      return
    }
    
    let user_params = {
      empl_no: empl_no,
      password: password1,
      name: name,
      dept_cd: dept_cd
    }

    let success_callback = (json) => {
      addToast('info',"회원가입이 완료되었습니다.")
      goto('/login')
    }

    let failure_callback = (json_error) => {
      error = json_error
      addToast('error',error.detail)
    }

    await post_user(user_params, success_callback, failure_callback);
  }

</script>

<div  class="form-container">
<form method="post" class="form-layout" on:submit|preventDefault={() => {handleSubmit();}}>
  
  <div>
    <Label for="empl_no" class="mb-2">사번</Label>
    <Input type="text" id="empl_no" required bind:value={empl_no}/>
  </div>
  <div class="grid gap-6 mb-6 md:grid-cols-2">
    <div>
      <Label for="name" class="mb-2">이름</Label>
      <Input type="text" id="name" placeholder="홍길동" required bind:value={name}/>
    </div>
    <div>
      <Label for="dept_cd" class="mb-2">부서</Label>
      <Input type="text" id="dept_cd" required bind:value={dept_cd}/>
    </div>
  </div>
  <div class="mb-6">
    <Label for="password" class="mb-2">Password</Label>
    <Input type="password" id="password1" placeholder="•••••••••" required bind:value={password1}/>
  </div>
  <div class="mb-6">
    <Label for="password2" class="mb-2">Confirm password</Label>
    <Input type="password" id="password2" placeholder="•••••••••" required bind:value={password2}/>
  </div>

  <Button type="submit">회원가입</Button>
</form>
</div> 