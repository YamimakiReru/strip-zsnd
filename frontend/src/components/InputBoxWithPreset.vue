<script setup lang="ts" generic="T">
const props = defineProps<{
  label: string;
  unit: string;
  modelValue: T;
  presets: T[];
  inputAttrs?: Record<string, any>;
}>();

const emit = defineEmits<{
  (ev: "update:modelValue", value: T): void;
}>();

function update(v: T) {
  emit("update:modelValue", v);
}
</script>

<template>
  <div class="dropdown">
    <label class="input input-sm md:input-md text-base-content">
      <span class="label"
        ><slot name="icon" /><span class="hidden md:flex">{{
          label
        }}</span></span
      >
      <input
        class="w-full"
        type="number"
        :value="modelValue"
        @input="update(($event.target as any).value)"
        v-bind="inputAttrs"
      />
      <span class="label">{{ unit }}</span></label
    >
    <ul
      tabindex="0"
      class="dropdown-content menu p-2 shadow bg-base-100 text-base-content rounded-box w-full mt-1"
    >
      <li v-for="(p, i) of presets" :key="i">
        <a @click="update(p)">{{ p }} {{ unit }}</a>
      </li>
    </ul>
  </div>
</template>
