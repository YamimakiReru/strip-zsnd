// Migrated from service.py
import { ZsndWavChunk, Float32ZeroSoundPredicate, ZeroSoundPredicate } from '@/services/wav_logic'
import { formatAudioPosition } from '@/util'

export interface ZsndDetectionEventListener {
  reportProgress?: (position: number, total: number) => void
  reportDropout?: (position: number, length: number) => void
}

export default class DetectZsndService {
  private static _CHUNK_SIZE = 65536

  async detect(listener: ZsndDetectionEventListener,
    chunk: ZsndWavChunk<Float32Array>, sampleRate: number,
    minDurationInMs: number = 10, threshold: number = -80.0) {
    const totalLengthInSeconds = this._formatNumSamplesInSeconds(chunk.size, sampleRate)
    console.debug(`Length: ${totalLengthInSeconds} / Number of frames: ${chunk.size}`)

    const minDurationInSamples = Math.round(sampleRate * minDurationInMs / 1000)
    const zeroSoundPredicate = new Float32ZeroSoundPredicate(threshold)

    let pos = 0
    let numPrevTrailingZeros = 0
    while (pos < chunk.size) {
      console.debug(`Position: ${pos}`)
      const subchunk = chunk.subarray(pos, pos + DetectZsndService._CHUNK_SIZE)
      numPrevTrailingZeros = this._collapse_chunk(listener, subchunk,
        numPrevTrailingZeros, pos, zeroSoundPredicate, minDurationInSamples)
      pos += subchunk.size
      listener.reportProgress?.(pos, chunk.size)
    }

    if (numPrevTrailingZeros >= minDurationInMs) {
      listener.reportDropout?.(chunk.size - numPrevTrailingZeros, numPrevTrailingZeros)
    }
  }

  private _collapse_chunk<T extends ArrayLike<number>>(
    lister: ZsndDetectionEventListener,
    chunk: ZsndWavChunk<T>,
    numPrevTrailingZeros: number,
    pos: number,
    zeroSoundPredicate: ZeroSoundPredicate<T>,
    minDurationInSamples: number): number {
    const numLeadingZeros = chunk.countLeadingZeros(zeroSoundPredicate)
    console.debug(`Leading zeros: ${numLeadingZeros}`)

    let zeroRunLength = numPrevTrailingZeros + numLeadingZeros
    if (chunk.size <= numLeadingZeros) {
      // all samples of the chunk were dropped
      return numLeadingZeros
    }
    if (zeroRunLength >= minDurationInSamples) {
      lister.reportDropout?.(pos - numPrevTrailingZeros, zeroRunLength)
    }

    let processedSamples = numLeadingZeros
    let zeroRunStart;
    for ([zeroRunStart, zeroRunLength] of chunk.iterateInnerZeroRuns(zeroSoundPredicate)) {
      if (zeroRunLength < minDurationInSamples) {
        continue
      }
      lister.reportDropout?.(pos + zeroRunStart, zeroRunLength)
      processedSamples = zeroRunStart + zeroRunLength
    }

    const numTrailingZeros = chunk.countTrailingZeros(zeroSoundPredicate)
    console.debug(`Trailing zeros: ${numTrailingZeros}`)
    return numLeadingZeros
  }

  private _formatNumSamplesInSeconds(numSamples: number, frameRate: number): string {
    return formatAudioPosition(numSamples / frameRate)
  }
}
