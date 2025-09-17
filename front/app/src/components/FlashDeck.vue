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
    width: 100%;
    background-color: #f1f1f8;
    border-radius: calc(var(--border-size) * 2);
    border-color: var(--primary-color);
    border-width: var(--border-size);
    border-style: outset;
    margin: var(--spacing) 0;
    box-sizing: border-box;
    position: relative;
    color: var(--primary-color);
    cursor: pointer;
    box-shadow: rgba(0, 0, 0, 0.35) 0px var(--border-size) calc(var(--border-size) * 2);
    display: flex;
    justify-content: center;
    align-items: center;
}

.deck:disabled {
    background-color: var(--disable-background-color);
    color: var(--disable-color);
    border-color: var(--disable-border-color);
}

.deck-name {
    width: 60%;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: var(--deck-font-size);
}

.deck-score {
    position: absolute;
    bottom: var(--spacing);
    left: var(--spacing);
    margin: 0;
    font-size: var(--deck-font-size);
}

.deck-level {
    position: absolute;
    bottom: var(--spacing);
    right: var(--spacing);
    height: calc(var(--deck-font-size) * 1.3);
}
</style>
