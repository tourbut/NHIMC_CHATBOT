<script>
    import { goto } from '$app/navigation';
    import Error from "$lib/components/Error.svelte";
    import { post_user } from "$lib/apis/user";
  
    let error = {detail:[]}
    let username = ''
    let password = ''
  
    const handleSubmit = async () => {
      
      let params = {
          username: username,
          password: password
      }
  
      let success_callback = (json) => {
              goto('/chat')
          }
  
      let failure_callback = (json_error) => {
              error = json_error
          }
  
      //await login(params, success_callback, failure_callback);
      success_callback()
    }
  
  </script>
  <div class="form-container">
      <h5 class="form-title">로그인</h5>
      <form method="post" class="form-layout" on:submit|preventDefault={() => {handleSubmit();}}>
        <div>
          <label for="username" class="form-label">ID</label>
          <input type="text" class="form-input" id="username" bind:value={username}>
        </div>
        <div>
          <label for="password1" class="form-label">PW</label>
          <input type="password" class="form-input" id="password1" bind:value={password}>
        </div>
        <button type="submit" class="form-button">로그인</button>
        <Error error={error} />
      </form>
  </div>
  <div class="container mx-auto p-4 max-w-md">
    <button class="form-button" on:click={() => {goto('/user');}}>회원가입</button>
  </div>