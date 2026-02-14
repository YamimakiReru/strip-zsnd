import DetectZsndService from "@/services/DetectZsndService";
import { ZsndWavChunk, Float32ZeroSoundPredicate } from "@/services/wav_logic"
import { describe, it, expect } from "vitest";

describe(DetectZsndService.name, () => {
  it("can detect inner zero runs", async () => {
    let buf = new Float32Array(114514).fill(0.5)
    buf.fill(1e-10, 89383, 89383 + 581)
    const chunk = new ZsndWavChunk(buf)
    const service = new DetectZsndService();
    const results = await service.detect({}, chunk, 44100)
    expect(results).toEqual([{ position: 89383, duration: 581 }])
  })
})

function uniformRandom(l: number, h: number) {
  return l + ((h - l) * Math.random())
}

describe(Float32ZeroSoundPredicate.name, () => {
  it("always returns true if any sample is lower than the threshold", () => {
    const lim = 0.99
    const vals = new Float32Array(4000)
    for (let i = 0; i < vals.length; ++i) {
      vals[i] = - uniformRandom(-lim, lim)
    }
    const predicate = new Float32ZeroSoundPredicate(-0.01)
    for (let i = 0; i < vals.length; ++i) {
      expect(predicate.isZeroSoundSample(vals, i)).toBe(true)
    }
  })

  it("always returns false if the sample exceeds the threshold", () => {
    // -20dB -> 0.1x
    const vals = new Float32Array(4000)
    for (let i = 0; i < vals.length; ++i) {
      vals[i] = Math.sign(Math.random() - 0.5) * uniformRandom(1e-9, 1e-2)
    }
    const predicate = new Float32ZeroSoundPredicate(-200)
    for (let i = 0; i < vals.length; ++i) {
      expect(predicate.isZeroSoundSample(vals, i)).toBe(false)
    }
  })
})

describe(ZsndWavChunk.name, () => {
  it("can count leading zeros", () => {
    const predicate = new Float32ZeroSoundPredicate(-80)
    const bbuf = new Float32Array(4000).fill(-0.5)
    bbuf.fill(uniformRandom(-1e-9, +1e-9), 0, 200)
    const chunk = new ZsndWavChunk(bbuf)
    expect(chunk.countLeadingZeros(predicate)).toBe(200)
    expect(chunk.countTrailingZeros(predicate)).toBe(0)
  })

  it("can count trailing zeros", () => {
    const predicate = new Float32ZeroSoundPredicate(-80)
    const bbuf = new Float32Array(4000).fill(-0.5)
    bbuf.fill(uniformRandom(-1e-9, +1e-9), 4000 - 200)
    const chunk = new ZsndWavChunk(bbuf)
    expect(chunk.countTrailingZeros(predicate)).toBe(200)
    expect(chunk.countLeadingZeros(predicate)).toBe(0)
  })

  it("can iterate inner zeros", () => {
    const predicate = new Float32ZeroSoundPredicate(-80)
    const bbuf = new Float32Array(4000).fill(-0.5)
    bbuf.fill(uniformRandom(-1e-9, +1e-9), 100, 200)
    bbuf.fill(uniformRandom(-1e-9, +1e-9), 594, 680)
    const chunk = new ZsndWavChunk(bbuf)
    expect(Array.from(chunk.iterateInnerZeroRuns(predicate))).toEqual([
      [100, 200 - 100],
      [594, 680 - 594],
    ])
  })
})
