<template>
    <div class="overlay">
        <p>
            {{ title }}
        </p>
        <p v-if="choiceMode">˄</p>
        <input ref="inputRef" class="input" v-model="inputValue" @keyup="handleKey" :readonly="choiceMode"/>
        <p v-if="choiceMode">˅</p>
    </div>
</template>

<script>
export default {
    name: 'FlashOverlay',
    props: {
        title: String,
        choices: Array
    },
    data() {
        return {
            inputValue: "",
            choiceIndex: 0
        }
    },
    mounted() {
        this.$nextTick(() => {
            this.$refs.inputRef?.focus();
        });

        if (this.choiceMode) {
            this.updateChoice();
        }
    },
    methods: {
        mod(i, n) {
            return ((i % n) + n) % n;
        },
        handleKey(event) {
            switch(event.key) {
                case "Enter":
                    this.submit();
                    break;
                case "Escape":
                    this.exit();
                    break;
                case "ArrowUp":
                    if (this.choiceMode) {
                        this.choiceIndex = this.mod((this.choiceIndex - 1), this.choices.length);
                        this.updateChoice();
                    }
                    break;
                case "ArrowDown":
                    if (this.choiceMode) {
                        this.choiceIndex = this.mod((this.choiceIndex + 1), this.choices.length);
                        this.updateChoice();
                    }
                    break;
                default:
                    break;
            }
        },
        submit() {
            this.$emit('submit', this.inputValue);
            this.inputValue = "";
        },
        exit() {
            this.$emit('cancel');
        },
        updateChoice() {
            this.inputValue = this.choices[this.choiceIndex];
        }
    },
    computed: {
        choiceMode() {
            return this.choices.length > 0;
        } 
    },
    watch: {
        choices: function (newChoices) {
            if (newChoices.length > 0) {
                this.updateChoice();
            }
        }
    }
}
</script>

<style scoped>
.overlay {
  position: fixed;
  height: 100vh;
  width: 100vw;
  z-index: 10;
  background-color: black;
  opacity: 70%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

p, input {
    color: white;
    font-size: 8vh;
}

.input {
    background: transparent;
    border: none;
    text-align: center;
    outline: none;
}

</style>
