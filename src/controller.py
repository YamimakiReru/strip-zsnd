# coding: utf-8

from service import StripZsndService, StrippingEventListener
from model import RWavReader, RWavWriter, ZsndLogMixin

from rich.progress import Progress
from i18n import t as _
import io
import os

class StripZsndController(StrippingEventListener, ZsndLogMixin):
    def _do_strip(self, reader: RWavReader, writer, min_duration, threshold, detect_only):
        service = StripZsndService(self)
        with Progress() as progress:
            self._progress = progress
            self._progress_task = progress.add_task(_('app.processing'), total=reader.count_frames())
            service.strip(reader, writer, min_duration, threshold, detect_only)

    def on_update_progress(self, num_processed_frames, num_total_frames):
        assert self._progress is not None
        assert self._progress_task is not None
        self._progress.update(self._progress_task, completed=num_processed_frames, total=num_total_frames)

    def strip(self, input: str, writer: str|None, min_duration: int, threshold: float, detect_only: bool):
        out_file: io.BufferedWriter|None = None
        writer = None
        in_file, reader = self._create_reader(input)
        if reader is None:
            return 1
        try:
            if not detect_only:
                output_base, ext = os.path.splitext(input)
                output_path = writer or f'{output_base}-fix{ext}'
                out_file, writer = self._create_writer(output_path, reader)
                if writer is None:
                    return 1

            return self._do_strip(reader, writer, min_duration, threshold, detect_only)

        except Exception as exc:
            logger = self.get_logger()
            logger.error(str(exc))
            logger.debug('', exc_info=True)
            return 1
        finally:
            writer and writer.close()
            out_file and out_file.close()
            reader.close()
            in_file.close()

    def _create_reader(self, path: str) -> tuple[io.BufferedIOBase|None, RWavReader|None]:
        try:
            f = io.open(path, 'rb')
            try:
                # Wave_read does not close the file if it is created by an opend file
                return (f, RWavReader(f))
            except BaseException as exc:
                f.close()
                raise
        except Exception as exc:
            logger = self.get_logger()
            logger.error(_('zsnd.input_file_cannot_be_opened'), {'f': path, 'exc': str(exc)})
            logger.debug('', exc_info=True)
            return (None, None)

    def _create_writer(self, path: str, reader: RWavReader) -> tuple[io.BufferedIOBase|None, RWavWriter|None]:
        try:
            outf = io.open(path, 'wb')
            try:
                return (outf, RWavWriter(outf, reader))
            except BaseException as exc:
                outf.close()
                raise
        except Exception as exc:
            logger = self.get_logger()
            logger.error(_('zsnd.output_file_cannot_be_opened'),
                    {'f': path, 'exc': str(exc)})
            logger.debug('', exc_info=True)
            return (None, None)
