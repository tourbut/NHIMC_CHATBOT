<script>
    import '../app.css';
    import { APP_NAME } from '$lib/stores';
</script>

<svelte:head>
	<title>
		{$APP_NAME}
	</title>
</svelte:head>

<slot></slot>

