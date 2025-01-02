<script>
  import { Card, Button, Label, Input, Checkbox } from 'flowbite-svelte';
  import { goto } from '$app/navigation';
  import { login } from '$lib/apis/user';
  import { addToast } from '$lib/common';
  import { user_token,username,is_admin, dept_cd, dept_nm } from '$lib/stores';
  let error = {detail:[]}
  let empl_no = ''
  let password = ''

  const handleSubmit = async () => {
    
    let params = {
      username: empl_no,
      password: password
    }

    let success_callback = (json) => {
      user_token.set(json.access_token)
      username.set(json.name)
      is_admin.set(json.is_admin)
      dept_nm.set(json.dept_nm)
      dept_cd.set(json.dept_cd)
      goto('/')
    }

    let failure_callback = (json_error) => {
      error = json_error
      addToast('error',error.detail)
    }

    await login(params, success_callback, failure_callback);
  }

</script>
{#if $username}
  <div class="container mx-auto p-4 max-w-md">
    <h1>{$dept_nm} {$username}님 반갑습니다.</h1>
  </div>
{:else}
<Card class="container mx-auto p-4 max-w-md my-8">
  <form class="flex flex-col space-y-6" method="post" on:submit|preventDefault={() => {handleSubmit();}}>
    <h3 class="text-xl font-medium text-gray-900 dark:text-white">국민건강보험 일산병원 챗봇</h3>
    <Label class="space-y-2">
      <span>사번</span>
      <Input type="text" name="사번" required bind:value={empl_no} />
    </Label>
    <Label class="space-y-2">
      <span>비밀번호</span>
      <Input type="password" name="password" placeholder="•••••" required bind:value={password} />
    </Label>
    <Button type="submit" class="w-full">로그인</Button>
  </form>
</Card>
{/if}