<script>
  import '../app.css';
  import Navigation from '$lib/components/common/Navigation.svelte';
  import Footer from '$lib/components/common/Footer.svelte';
  import { APP_NAME,user_token,username } from '$lib/stores';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import Toasts from '$lib/components/common/Toasts.svelte';
  import { get_user } from '$lib/apis/user.js';
 
  async function checked_user_active()
  {
    let params = {}
    
    let success_callback = (json) => {
      let is_active=json.is_active
      if (!is_active) {
          alert("활성화된 계정이 아닙니다.");
          goto('/login');
        }
    }

    let failure_callback = (json_error) => {
        alert("세션이 만료되었습니다. 다시 로그인해주세요.");
        
        username.set("");
        user_token.set("");
        goto('/login');
    }

    await get_user(params,success_callback, failure_callback)
  }

  onMount(async () => {
    if ($user_token !== "" && location.pathname !== '/login') {
      await checked_user_active()
    }

    if ($user_token === "" && location.pathname !== '/login') {
      alert("로그인이 필요합니다.");
      await goto('/login');
    } 
  })
</script>

<svelte:head>
	<title>
		{$APP_NAME}
	</title>
</svelte:head>

<div >
  <div class="navbar">
    <Navigation />
    <div class="container">
      <div class="content">
        <slot />
      </div>
    </div>
  </div>
  <div class="footer">
    <Toasts />
    <Footer />
  </div>
</div> 



<style>
.navbar {
    z-index: 1000;
    position: fixed;
    width: 100%;
  }
.container {
  display: flex;
}
.content {
  flex: 1; /* 남은 공간을 차지하도록 설정 */
}
.footer {
  flex-shrink: 0; /* 브라우저 크기가 줄어들 때, footer는 크기를 줄이지 않도록 설정 */
  position: fixed;
  bottom: 0;
  width: 100%;
}
</style>