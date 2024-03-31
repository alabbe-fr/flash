<template>
    <button class="deck" :disabled="disabled" @click="pick">
        <h1 class="dech-name">
            {{ name }}
        </h1>
        <img class="deck-level" src="../assets/easy.svg" v-if="level === 'easy'" />
        <img class="deck-level" src="../assets/medium.svg" v-if="level === 'medium'" />
        <img class="deck-level" src="../assets/hard.svg" v-if="level === 'hard'" />
    </button>
</template>

<script>

export default {
    name: 'FlashDeck',
    props: {
        name: String,
        level: String,
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
    position: relative;
    color: #3A5BA0;
    cursor: pointer;
    box-shadow: rgba(0, 0, 0, 0.35) 0px 0.5em 1em;
}

.deck:disabled {
    background-color: #e5e5e5;
    color: #7b7b7b;
    border-color: #afafaf;
}

.deck-name {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

.deck-level {
    position: absolute;
    bottom: 0.5em;
    right: 0.5em;
    height: 4em;
}
</style>
