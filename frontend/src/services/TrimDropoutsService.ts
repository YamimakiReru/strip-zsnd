import { DropoutInfo } from "@/services/DetectZsndService";
import { ZsndWavChunk } from "@/services/wav_logic";

export default class TrimDropoutsService {
  trimAt(
    chunk: ZsndWavChunk<Float32Array>,
    dropouts: DropoutInfo[],
    index: number,
  ): { newChunk: ZsndWavChunk<Float32Array>; newDropouts: DropoutInfo[] } {
    const newChunk = this.trimAll(chunk, [dropouts[index]]);

    // Shifts the following elements left by the removed element's length.
    const newDropouts = dropouts.slice(0, index);
    const offset = dropouts[index].duration;
    for (let i = index + 1; i < dropouts.length; ++i) {
      newDropouts.push({
        position: dropouts[i].position - offset,
        duration: dropouts[i].duration,
      });
    }

    return { newChunk, newDropouts };
  }

  trimAll(
    chunk: ZsndWavChunk<Float32Array>,
    dropouts: DropoutInfo[],
  ): ZsndWavChunk<Float32Array> {
    // Estimates size of the trimmed chunk
    let newSize = chunk.size;
    for (const d of dropouts) {
      newSize -= d.duration;
    }

    const newFrames = new Float32Array(newSize);
    let srcPos = 0;
    let dstPos = 0;
    for (const d of dropouts) {
      console.assert(srcPos <= d.position);
      const subchunk = chunk.subarray(srcPos, d.position);
      srcPos = d.position + d.duration;
      newFrames.set(subchunk.raw(), dstPos);
      dstPos += subchunk.size;
    }

    if (srcPos < chunk.size) {
      const subchunk = chunk.subarray(srcPos, chunk.size);
      newFrames.set(subchunk.raw(), dstPos);
    }

    return new ZsndWavChunk(newFrames);
  }
}
