<template>
  <div class="flash-card" @click="flip" :style="cssVars">
    <div class="flash-card-inner" :class="{ flipped: flipped}">
      <div class="flash-card flash-card-front">
        <h1 class="flash-title">{{ translation }}</h1>
      </div>
      <div class="flash-card flash-card-back" :style="cssVars">
        <h1 class="flash-title">{{ gender }} {{ value }}</h1>
        <button class="flash-button" @click="done">OK</button>
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
      this.flipped = !this.flipped;
    },
    done() {
      this.$emit('done');
    },
    generateRandomAngle() {
      this.angle = Math.floor(Math.random() * (2 * MAX_ANGLE + 1) - MAX_ANGLE);
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
  height: 75vh;
  width: 50vh;
  perspective: 200vh;
  color: #5352ed;
  transform: translate(-50%, -50%) rotate(var(--angle));
  z-index: var(--z-index);
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

.flash-card-front, .flash-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden; /* Safari */
  backface-visibility: hidden;
  background-color: #f1f1f8;
  border-radius: 2vh;
  border-color: #5352ed;
  border-width: 1vh;
  border-style: solid;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3em 0;
  box-sizing: border-box;
  box-shadow: rgba(0, 0, 0, 0.35) 0px 0.5em 1em;
}

.flash-card-front:hover, .flash-card-back:hover {
  box-shadow: rgba(0, 0, 0, 0.35) 0px 1.5em 3em;
  cursor: pointer;
}

.flash-card-back {
  transform: translate(-50%, -50%) rotate(var(--angle)) rotateY(180deg);
}

.flash-title {
  font-size: 3em;
}

.flash-button {
  padding: 1rem 2rem;
  font-size: 2rem;
  margin-top: auto;
  border-radius: 1rem;
  border-color: #5352ed;
  border-width: 0.5rem;
  background-color: white;
  color: #5352ed;
  font-weight: bold;
  cursor: pointer;
}

</style>
