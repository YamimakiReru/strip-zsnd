import DetectZsndService, {
  ZsndDetectionEventListener,
} from "@/services/DetectZsndService";
import { ZsndWavChunk } from "@/services/wav_logic";
import { HumanReadableError } from "@/util";

import * as WavDecoder from "wav-decoder";
import * as WavEncoder from "wav-encoder";
import { AudioData } from "wav-encoder";

export default class LoadAudioService {
  private readonly t;

  /**
   * @param t i18n translation function (key → localized string).
   */
  constructor(t: (k: string) => string) {
    this.t = t;
  }

  async loadFile(
    file: File,
    minDuration: number,
    threshold: number,
    zsndDetectionEventListener: ZsndDetectionEventListener,
  ) {
    const arrBuf = await file.arrayBuffer();
    const audioData = WavDecoder.decode.sync(arrBuf);
    if (1 !== audioData.channelData.length) {
      throw new HumanReadableError(this.t("zsnd.mono_only_supported"));
    }
    const rawAudioChunk = new ZsndWavChunk(audioData.channelData[0]);

    const dropouts = await new DetectZsndService().detect(
      zsndDetectionEventListener,
      rawAudioChunk,
      audioData.sampleRate,
      minDuration,
      threshold,
    );

    const audioBlobForPreview = this.loadFromChunk(
      rawAudioChunk,
      audioData.sampleRate,
    );

    return {
      rawAudioChunk,
      originalSampleRate: audioData.sampleRate,
      audioBlobForPreview,
      dropouts,
    };
  }

  loadFromChunk(chunk: ZsndWavChunk<Float32Array>, sampleRate: number): Blob {
    const audioData = {
      sampleRate,
      channelData: [chunk.raw()],
    };

    // wav-decoder returns audio as Float32Array,
    // so using float32 is likely the most efficient.
    const reArrBuf = WavEncoder.encode.sync(audioData, {
      float: true,
      bitDepth: 32,
    });

    return new Blob([reArrBuf], { type: "audio/wav" });
  }
}
