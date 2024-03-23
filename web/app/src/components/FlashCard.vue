<template>
  <div class="flash-card" @click="flip">
    <div class="flash-card-inner" :class="{ flipped: flipped }">
      <div class="flash-card-front" :style="cssVars">
        <h1 class="flash-title">{{ translation }}</h1>
      </div>
      <div class="flash-card-back">
        <h1 class="flash-title">{{ gender }} {{ value }}</h1>
        <div class="flash-button-container">
          <button class="flash-button flash-button-check" @click="success"><img class="flash-icon"
              src="../assets/check.svg" /></button>
          <button class="flash-button flash-button-close" @click="fail"><img class="flash-icon"
              src="../assets/close.svg" /></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

const MAX_ANGLE = 3;

export default {
  name: 'FlashCard',
  data() {
    return {
      flipped: false,
      angle: 0
    }
  },
  props: {
    gender: String,
    value: String,
    translation: String,
    order: Number,
    disabled: Boolean,
  },
  computed: {
    cssVars() {
      return {
        "--angle": `${this.angle}deg`,
        "--z-index": this.order,
      }
    }
  },
  methods: {
    flip() {
      if (this.disabled) return;
      this.flipped = !this.flipped;
    },
    success() {
      this.$emit('success');
    },
    fail() {
      this.$emit('fail');
    },
    generateRandomAngle() {
      this.angle = this.disabled ? 0 : Math.floor(Math.random() * (2 * MAX_ANGLE + 1) - MAX_ANGLE);
    },
  },
  mounted() {
    this.generateRandomAngle();
  }
}
</script>

<style scoped>
.flash-card {
  position: absolute;
  top: 50%;
  left: 50%;
  height: 100%;
  width: 100%;
  perspective: 200vh;
  color: #3A5BA0;
  z-index: var(--z-index);
  transform: translate(-50%, -50%);
}

.flash-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 1s;
  transform-style: preserve-3d;
}

.flipped {
  transform: rotateY(180deg);
}

.flash-card-front,
.flash-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  /* Safari */
  backface-visibility: hidden;
  background-color: #f1f1f8;
  border-radius: 2em;
  border-color: #3A5BA0;
  border-width: 1em;
  border-style: outset;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  padding: 6em 0;
  box-sizing: border-box;
  box-shadow: rgba(0, 0, 0, 0.35) 0px 0.5em 1em;
}

.flash-card-front:hover,
.flash-card-back:hover {
  box-shadow: rgba(0, 0, 0, 0.35) 0px 1.5em 3em;
  cursor: pointer;
}

.flash-card-front {
  transform: rotate(var(--angle));
}

.flash-card-back {
  transform: rotateY(180deg);
}

.flash-title {
  font-size: 3em;
}

.flash-button-container {
  margin-top: auto;
  display: flex;
  justify-content: space-around;
}

.flash-button {
  padding: 1rem;
  font-size: 2rem;
  border-radius: 1rem;
  border-width: 0.5rem;
  cursor: pointer;
}

.flash-button-check {
  border-color: #6BCB77;
  background-color: #f3fff4;
}

.flash-button-close {
  border-color: #FF6B6B;
  background-color: #fff0f0;
}

.flash-icon {
  width: 2em;
  height: 2em;
}
</style>
