<script>
export default {
  methods: {
    hello() {
      return 'hello'
    }
  }
}
</script>

<template>
  <div class="p-4 bg-gray-800 text-white rounded-lg">
    Hello Tailwind v4 {{ hello() }}
  </div>
</template>

<style>
</style>
