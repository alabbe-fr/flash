<template>
    <button class="deck" :disabled="disabled" @click="pick">
        <h1 class="deck-name">
            {{ name }}
        </h1>
        <h1 class="deck-score" v-if="score >= 0 && size >= 0">{{ score }}/{{ size }}</h1>
        <img class="deck-level" src="../assets/deck/easy.svg" v-if="level === 'easy' && !disabled" />
        <img class="deck-level" src="../assets/deck/medium.svg" v-if="level === 'medium' && !disabled" />
        <img class="deck-level" src="../assets/deck/hard.svg" v-if="level === 'hard' && !disabled" />
        <img class="deck-level" src="../assets/deck/easy-disabled.svg" v-if="level === 'easy' && disabled" />
        <img class="deck-level" src="../assets/deck/medium-disabled.svg" v-if="level === 'medium' && disabled" />
        <img class="deck-level" src="../assets/deck/hard-disabled.svg" v-if="level === 'hard' && disabled" />
    </button>
</template>

<script>

export default {
    name: 'FlashDeck',
    props: {
        name: String,
        level: String,
        size: Number,
        score: Number,
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
    min-height: 10%;
    width: 100%;
    background-color: #f1f1f8;
    border-radius: 1em;
    border-color: #3A5BA0;
    border-width: 1em;
    border-style: outset;
    margin: 1em 0;
    box-sizing: border-box;
    position: relative;
    color: #3A5BA0;
    cursor: pointer;
    box-shadow: rgba(0, 0, 0, 0.35) 0px 0.5em 1em;
    display: flex;
    justify-content: center;
    align-items: center;
}

.deck:disabled {
    background-color: #e5e5e5;
    color: #7b7b7b;
    border-color: #afafaf;
}

.deck-name {
    width: 65%;
    overflow: hidden;
    text-overflow: ellipsis;
}

.deck-score {
    position: absolute;
    bottom: 0.5em;
    left: 0.5em;
    margin: 0;
}

.deck-level {
    position: absolute;
    bottom: 0.5em;
    right: 0.5em;
    height: 4em;
}
</style>
