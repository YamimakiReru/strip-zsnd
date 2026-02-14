/** @see https://github.com/mohayonao/wav-decoder */
declare module "wav-decoder" {
  interface AudioData {
    sampleRate: number;
    channelData: Float32Array[];
  }

  interface WavDecoderOptions {
    symmetric?: boolean;
  }

  function decode(
    src: ArrayBuffer,
    opts?: WavDecoderOptions,
  ): Promise<AudioData>;
  namespace decode {
    function sync(src: ArrayBuffer, opts?: object): AudioData;
  }
}
