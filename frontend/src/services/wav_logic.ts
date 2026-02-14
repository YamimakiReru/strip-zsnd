// Migrated from wav_io.py, wav_logic.py
export interface ZeroSoundPredicate<T> {
  isZeroSoundSample(frames: T, posInBytes: number): boolean;
}

export class ZsndWavChunk<T extends ArrayLike<number>> {
  /** Number of samples contained in this buffer */
  public readonly size: number;

  private readonly _frames: T;

  constructor(frames: T) {
    this._frames = frames;
    this.size = frames.length;
  }

  public countLeadingZeros(predicate: ZeroSoundPredicate<T>): number {
    for (let i = 0; i < this._frames.length; ++i) {
      if (!predicate.isZeroSoundSample(this._frames, i)) {
        return i;
      }
    }
    return this._frames.length;
  }

  public countTrailingZeros(predicate: ZeroSoundPredicate<T>): number {
    for (let i = this._frames.length - 1; i >= 0; --i) {
      if (!predicate.isZeroSoundSample(this._frames, i)) {
        return this._frames.length - i - 1;
      }
    }
    return this._frames.length;
  }

  public *iterateInnerZeroRuns(
    predicate: ZeroSoundPredicate<T>,
  ): IterableIterator<[number, number]> {
    // skip leading and trailing zeros
    let i = this.countLeadingZeros(predicate);

    // scan inner dropouts
    let zeroRunLength = 0;
    let zeroRunStart = 0;
    for (; i < this._frames.length; ++i) {
      if (predicate.isZeroSoundSample(this._frames, i)) {
        if (0 === zeroRunLength) {
          zeroRunStart = i;
        }
        ++zeroRunLength;
      } else {
        if (0 < zeroRunLength) {
          yield [zeroRunStart, zeroRunLength];
          zeroRunLength = 0;
        }
      }
    }
  }

  public subarray(start: number, stop: number) {
    if (!("subarray" in this._frames)) {
      throw new Error("this._frames does not implement 'subarray()'");
    }
    const sub = (this._frames.subarray as Function)(start, stop);
    return new ZsndWavChunk(sub);
  }
}

/** Float PCM: -1.0 < x < 1.0 (normalized) */
export class Float32ZeroSoundPredicate implements ZeroSoundPredicate<Float32Array> {
  private readonly _maxAmp: number;
  private readonly _minAmp: number;

  constructor(thresholdInDb: number) {
    this._maxAmp = this._dbToAmplitude(thresholdInDb);
    this._minAmp = -this._maxAmp;
  }

  /**
   * dBFS conversion:
   *   -6 dB = 0.5x amplitude
   *  -20 dB = 0.1x amplitude
   */
  private _dbToAmplitude(volumeInDb: number): number {
    const amp = Math.pow(10, volumeInDb / 20);
    console.debug(`${volumeInDb} dBFS -> normalized amplitude ${amp}`);
    return amp;
  }

  isZeroSoundSample(frames: Float32Array, posInBytes: number): boolean {
    const fp = frames[posInBytes];
    return this._minAmp <= fp && fp <= this._maxAmp;
  }
}
