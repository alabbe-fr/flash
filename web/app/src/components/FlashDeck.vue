<template>
    <button class="deck" :disabled="disabled" @click="pick">
        <h1>
            {{ name }}
        </h1>
    </button>
</template>

<script>

export default {
    name: 'FlashDeck',
    props: {
        name: String,
        disabled: Boolean
    },
    methods: {
        pick() {
            if (this.disabled) {
                return;
            }

            this.$emit('pick');
        }
    }
}

</script>

<style scoped>
.deck {
    height: 10%;
    width: 100%;
    background-color: #f1f1f8;
    border-radius: 1em;
    border-color: #3A5BA0;
    border-width: 1em;
    border-style: outset;
    margin: 1em 0;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #3A5BA0;
    cursor: pointer;
    box-shadow: rgba(0, 0, 0, 0.35) 0px 0.5em 1em;
}

.deck:disabled {
    background-color: #e5e5e5;
    color: #7b7b7b;
    border-color: #afafaf;
}
</style>
