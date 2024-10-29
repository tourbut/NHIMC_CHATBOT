<script>
  import { Input, Label, Toggle, Button, Checkbox, A } from 'flowbite-svelte';
  import { goto } from '$app/navigation';
  import { post_user} from "$lib/apis/user";
  import InterestsInput from '$lib/components/detail/InterestsInput.svelte';
  import { addToast } from '$lib/common';
  let error = {detail:[]}
  //User info
  let username = ''
  let password1 = ''
  let password2 = ''
  let email = ''
  //Detail info
  let name = ""
  let age = 0
  let discord_yn = false
  let email_yn = false
  let interests = []

  const handleSubmit = async () => {

    if (password1 !== password2) {
      error={detail: "비밀번호가 일치하지 않습니다."}
      return
    }
    
    let user_params = {
      username: username,
      password: password1,
      email: email,
      name: name,
      age: age,
      discord_yn: discord_yn,
      email_yn: email_yn,
      interests: interests.join('|')
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
    <Label for="username" class="mb-2">ID</Label>
    <Input type="text" id="username" placeholder="knowslog" required bind:value={username}/>
  </div>
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
  <div class="mb-6">
    <Label for="email" class="mb-2">Email</Label>
    <Input type="email" id="email" placeholder="abc@knowslog.com" required bind:value={email}/>
  </div>
  <div class="mb-6">
    <Label for="password" class="mb-2">Password</Label>
    <Input type="password" id="password1" placeholder="•••••••••" required bind:value={password1}/>
  </div>
  <div class="mb-6">
    <Label for="password2" class="mb-2">Confirm password</Label>
    <Input type="password" id="password2" placeholder="•••••••••" required bind:value={password2}/>
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

  <Button type="submit">회원가입</Button>
</form>
</div> 