<script>
    export let llm_model = "";
</script>

<select class="form-input mb-4 p-2 border border-gray-300 rounded" bind:value={llm_model}>
    <option value="">모델 선택</option>
    <option value="gpt-4o">gpt-4o</option>
    <option value="gpt-4o-mini">gpt-4o-mini</option>
    <option value="gpt-4-turbo">gpt-4-turbo</option>
    <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
    <option value="claude-3-5-sonnet-20240620">claude-3-5-sonnet-20240620</option>
    <!-- Add more options as needed -->
</select>