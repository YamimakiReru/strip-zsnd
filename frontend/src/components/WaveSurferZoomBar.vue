<script setup lang="ts">
// (In wavesurfer.js v7.12.1)
// The Zoom plugin crashes if it receives mouse‑wheel events before an audio is loaded.
// Initialize the plugin only after WaveSurfer has finished loading an audio.

import WaveSurferZoomPlugin from "wavesurfer.js/dist/plugins/zoom.esm.js";
import WaveSurfer from "wavesurfer.js";
import { useI18n } from "vue-i18n";
import { onBeforeUnmount, onMounted, watch, computed, ref } from "vue";

const props = defineProps<{
  /**
   * Container element used by wavesurfer.js to render its UI.
   * Not the internal wrapper returned by getWrapper().
   */
  container: HTMLElement | null;

  waveSurfer: WaveSurfer | null;
}>();

const { t } = useI18n();
const _SLIDER_MAX = 1000;

/**
 * The "zoom" value represents the minimum pixels per second of audio.
 * The slider itself uses a logarithmic scale.
 *
 * @see {WaveSurfer.minPxPerSec}
 * @see https://wavesurfer.xyz/docs/types/wavesurfer.WaveSurferOptions
 */
let _min_zoom = 1;
const _MAX_ZOOM = 10000;
const _zoomLevel = ref<number>(0);

const _resizeObserver = new ResizeObserver(() => _recalculateMinZoom());

const _canInitialize = computed(
  () => null != props.waveSurfer && null != props.container,
);

const _stopWatchingWaveSurfer = watch(_canInitialize, (state) => {
  if (!state) {
    console.error("Unload operation is not yet implemented.");
    return;
  }
  _ensureReadyThenInitPlugin();
  _stopWatchingWaveSurfer();
});

onMounted(async () => {
  if (_canInitialize.value) {
    _ensureReadyThenInitPlugin();
    _stopWatchingWaveSurfer();
  }
});
onBeforeUnmount(() => {
  _resizeObserver.disconnect();
});

function _ensureReadyThenInitPlugin() {
  if (null == props.waveSurfer) {
    console.error("waveSurfer must not be null.");
    return;
  }
  if (props.waveSurfer.getDuration()) {
    _doInitPlugin();
  } else {
    props.waveSurfer.once("ready", () => _doInitPlugin());
  }
}

function _doInitPlugin() {
  if (null == props.waveSurfer) {
    console.error("waveSurfer must not be null.");
    return;
  }

  _recalculateMinZoom();
  _registerMinZoomRecalcHandler();

  // (In @meersagor/wavesurfer-vue v2.0.2)
  // "zoom" is not forwarded as a Vue event, so "@zoom" will never fire.
  props.waveSurfer.on("zoom", () => _onZoom());

  const activePlugins = props.waveSurfer.getActivePlugins();
  const isZoomPluginLoaded =
    -1 != activePlugins.findIndex((p) => "calculateNewZoom" in p);
  if (!isZoomPluginLoaded) {
    props.waveSurfer.registerPlugin(
      new WaveSurferZoomPlugin({
        exponentialZooming: true,
        maxZoom: _MAX_ZOOM,
      }),
    );
  }
}

function _registerMinZoomRecalcHandler() {
  if (null == props.waveSurfer || null == props.container) {
    console.error("waveSurfer must not be null.");
    return;
  }

  // The wrapper element fires a resize event even when the user changes the zoom level,
  // so I observe its container instead.
  _resizeObserver.observe(props.container);
  props.waveSurfer.once("destroy", () => _resizeObserver.disconnect());
}

function _recalculateMinZoom() {
  if (null == props.waveSurfer) {
    return;
  }
  _min_zoom = props.waveSurfer.getWidth() / props.waveSurfer.getDuration();
  _onZoom();
}

/** logarithmic slider */
function _onZoom() {
  const minPxPerSec = props.waveSurfer?.options.minPxPerSec || 1;
  if (Number.EPSILON > Math.abs(minPxPerSec - _min_zoom)) {
    _zoomLevel.value = 0;
    return;
  }

  const logMinZoom = Math.log(_min_zoom);
  const logValue =
    (Math.log(minPxPerSec) - logMinZoom) / (Math.log(_MAX_ZOOM) - logMinZoom);
  _zoomLevel.value = _SLIDER_MAX * logValue;
}

function _onZoomBarInput(event: Event) {
  const el = event.target as HTMLInputElement;
  _zoomLevel.value = parseFloat(el.value);
  _updateZoomLevel();
}

/* logarithmic slider */
function _updateZoomLevel() {
  // t(0 <= t <= 1)       = (log(x) - log(min)) / (log(max) - log(min))
  //    log(x) - log(min) =    t * (log(max) - log(min)
  //    log(x)            =    t * (log(max) - log(min)) + log(min)
  // x(min <= x <= max)   = e^{t * (log(max) - log(min)) + log(min)}
  const t = _zoomLevel.value / _SLIDER_MAX;
  const logMinZoom = Math.log(_min_zoom);
  const minPxPerSec = Math.exp(
    t * (Math.log(_MAX_ZOOM) - logMinZoom) + logMinZoom,
  );
  props.waveSurfer?.zoom(minPxPerSec);
}
</script>

<template>
  <label class="input text-base-content" :class="$attrs.class">
    <span class="label">{{ t("app.zoom") }}</span>
    <input
      type="range"
      @input="_onZoomBarInput"
      min="0"
      :max="_SLIDER_MAX"
      :value="_zoomLevel"
      class="range grow"
    />
  </label>
</template>
