/** @see https://github.com/mohayonao/wav-encoder */
declare module "wav-encoder" {
  interface AudioData {
    sampleRate: number
    channelData: Float32Array[]
  }

  interface WavEncoderOptions {
    bitDepth?: number
    float?: boolean
    symmetric?: boolean
  }

  function encode(audioData: AudioData, opts?: WavEncoderOptions): Promise<ArrayBuffer>
  namespace encode {
    function sync(audioData: AudioData, opts?: WavEncoderOptions): ArrayBuffer
  }
}
