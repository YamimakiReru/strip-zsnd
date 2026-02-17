<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    /**
     * The parent element node of resizeTarget needs to define the available maximum size for the resize target.
     * This can be a fixed size or a dynamic one provided by flex-grow.
     *
     * ```
     * Expected layout structure:
     * | parent container (flex, full width) |
     * | toolbar / header | resizeTarget (percentage width) | secondary sidebar (flex-grow) |
     * ```
     */
    resizeTarget: HTMLElement | null;

    /**
     * The CSS custom property name that provides the size value.
     *
     * For example, you might pass `--foo-size`, which can then be used
     * elsewhere as `var(--foo-size)` - including in Tailwind via `w-(--foo-size)`.
     */
    cssPropertyName: string;

    /**
     * - horizontal↔ -> resize width.
     * - vertical↕   -> resize height.
     */
    orientation: "horizontal" | "vertical";

    /** Minimum size as a percentage. (default: 10) */
    min?: number;

    /** Maximum size as a percentage. (default: 90) */
    max?: number;
  }>(),
  {
    min: 10,
    max: 90,
  },
);

function _moveDividerOnPointerEvent(event: PointerEvent) {
  if (!(event.target as HTMLElement).hasPointerCapture(event.pointerId)) {
    return;
  }
  const el = props.resizeTarget;
  if (null == el) {
    return;
  }

  const parentRect = el.parentElement?.getBoundingClientRect();
  if (null == parentRect) {
    console.error("resizeTarget does not have any parent");
    return;
  }

  const ratio =
    "vertical" == props.orientation
      ? (event.clientY - parentRect.top) / parentRect.height
      : (event.clientX - parentRect.left) / parentRect.width;
  const clamped = Math.round(
    Math.max(props.min, Math.min(props.max, 100 * ratio)),
  );
  el.style.setProperty(props.cssPropertyName, `${clamped}%`);
}
</script>

<template>
  <div
    @pointerdown="
      (ev) => (ev.target as HTMLElement).setPointerCapture(ev.pointerId)
    "
    @pointermove="_moveDividerOnPointerEvent"
    @pointerup="
      (ev) => (ev.target as HTMLElement).releasePointerCapture(ev.pointerId)
    "
    class="touch-none divider"
    :class="
      'vertical' == orientation
        ? 'divider-vertical cursor-ns-resize'
        : 'divider-horizontal cursor-ew-resize'
    "
  ></div>
</template>
