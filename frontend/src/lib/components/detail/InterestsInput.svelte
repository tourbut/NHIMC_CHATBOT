<script>
    import { Label, Input, Button, P} from 'flowbite-svelte';
    export let interests = [];
    let newInterest = '';

    function addInterest() {
        if (newInterest.trim()) {
            interests = [...interests, newInterest.trim()];
            newInterest = '';
        }
    }

    function removeInterest(index) {
        interests = interests.filter((_, i) => i !== index);
    }
</script>

<div>
    <div class="pt-8">
        <Label for="interests" class="block mb-2">관심사항</Label>
        <Input id="interests" placeholder="Please enter your interests." size="lg" bind:value={newInterest}>
            <Button slot="right" size="sm" on:click={addInterest}>추가</Button>
        </Input>
    </div>
    <div class="pt-2">
        <ul> 
            {#each interests as interest, index}
                <li class="flex items-center mb-2">
                    <P class="flex-grow">{interest}</P>
                    <Button tslot="right" size="sm" on:click={() => removeInterest(index)}>삭제</Button>
                </li>
            {/each}
        </ul>
    </div>
</div>