// Migrated from service.py
import { ZsndWavChunk, Float32ZeroSoundPredicate, ZeroSoundPredicate } from '@/services/wav_logic'
import { formatAudioPosition } from '@/util'

export interface DropoutInfo {
  position: number,
  duration: number,
}

export interface ZsndDetectionEventListener {
  reportProgress?: (position: number, total: number) => void
}

export default class DetectZsndService {
  private static _CHUNK_SIZE = 65536

  async detect(listener: ZsndDetectionEventListener,
    chunk: ZsndWavChunk<Float32Array>, sampleRate: number,
    minDurationInMs: number = 10, threshold: number = -80.0): Promise<DropoutInfo[]> {
    const totalLengthInSeconds = this._formatNumSamplesInSeconds(chunk.size, sampleRate)
    console.debug(`Length: ${totalLengthInSeconds} / Number of frames: ${chunk.size}`)

    const minDurationInSamples = Math.round(sampleRate * minDurationInMs / 1000)
    const zeroSoundPredicate = new Float32ZeroSoundPredicate(threshold)

    const { instance: result, proxy: dropoutInfoArray }
      = this._createLoggingDropoutInfoArray()
    let pos = 0
    let numPrevTrailingZeros = 0
    while (pos < chunk.size) {
      console.debug(`Position: ${pos}`)
      const subchunk = chunk.subarray(pos, pos + DetectZsndService._CHUNK_SIZE)
      numPrevTrailingZeros = this._collapse_chunk(dropoutInfoArray, listener,
        subchunk, numPrevTrailingZeros, pos, zeroSoundPredicate, minDurationInSamples)
      pos += subchunk.size
      listener.reportProgress?.(pos, chunk.size)
      // Allow the UI thread to render by yielding control.
      await new Promise(r => setTimeout(r))
    }

    if (numPrevTrailingZeros >= minDurationInMs) {
      dropoutInfoArray.push({
        position: chunk.size - numPrevTrailingZeros,
        duration: numPrevTrailingZeros,
      })
    }

    return result;
  }

  private _collapse_chunk<T extends ArrayLike<number>>(
    dropoutInfoArray: DropoutInfo[],
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
      dropoutInfoArray.push({
        position: pos - numLeadingZeros,
        duration: zeroRunLength,
      })
    }

    let processedSamples = numLeadingZeros
    let zeroRunStart;
    for ([zeroRunStart, zeroRunLength] of chunk.iterateInnerZeroRuns(zeroSoundPredicate)) {
      if (zeroRunLength < minDurationInSamples) {
        continue
      }
      dropoutInfoArray.push({
        position: pos + zeroRunStart,
        duration: zeroRunLength,
      })
      processedSamples = zeroRunStart + zeroRunLength
    }

    const numTrailingZeros = chunk.countTrailingZeros(zeroSoundPredicate)
    console.debug(`Trailing zeros: ${numTrailingZeros}`)
    return numLeadingZeros
  }

  private _createLoggingDropoutInfoArray() {
    const instance = [] as DropoutInfo[]
    const proxy = new Proxy(instance, {
      get(target, prop, receiver) {
        if (prop === "push") {
          return (...items: DropoutInfo[]) => {
            console.debug(...items)
            return Array.prototype.push.apply(target, items)
          }
        }
        return Reflect.get(target, prop, receiver)
      }
    })
    return { instance, proxy }
  }

  private _formatNumSamplesInSeconds(numSamples: number, frameRate: number): string {
    return formatAudioPosition(numSamples / frameRate)
  }
}
