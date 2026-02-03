from service import StripZsndService, StrippingEventListener
from wav_io import ZsndWavReader, ZsndWavWriter
from util import ZsndLogMixin

from rich.progress import Progress
import typer
from i18n import t as _
import io
import os
from typing import override

class StripZsndController(StrippingEventListener, ZsndLogMixin):
    '''
    Controller class should take care of environment‑specific concerns (data stores, UX and so on),
    so that Service class can focus exclusively on core business logic and become more testable.
    '''
    def _do_strip(self, reader: ZsndWavReader, writer, min_duration, threshold, detect_only):
        with Progress() as progress:
            self._progress = progress
            self._progress_task = progress.add_task(_('app.processing'), total=reader.count_frames())
            StripZsndService().strip(reader, writer, min_duration, threshold, detect_only, self)

    @override
    def on_update_progress(self, num_processed_frames, num_total_frames):
        assert self._progress is not None
        assert self._progress_task is not None
        self._progress.update(self._progress_task, completed=num_processed_frames, total=num_total_frames)

    def strip(self, input: str, output: str|None, force_overwrite: bool, 
            min_duration: int, threshold: float, detect_only: bool):
        out_file: io.BufferedWriter|None = None
        writer = None
        in_file, reader = self._create_reader(input)
        if reader is None:
            return 1
        try:
            if not detect_only:
                output_base, ext = os.path.splitext(input)
                output_path = output or f'{output_base}-fix{ext}'
                out_file, writer = self._create_writer(output_path, reader, force_overwrite)
                if writer is None:
                    return 1

            return self._do_strip(reader, writer, min_duration, threshold, detect_only)

        except typer.Exit:
            raise
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

    def _create_reader(self, path: str) -> tuple[io.BufferedIOBase|None, ZsndWavReader|None]:
        try:
            f = io.open(path, 'rb')
            try:
                # Wave_read does not close the file if it is created by an opend file
                return (f, ZsndWavReader(f))
            except BaseException as exc:
                f.close()
                raise
        except Exception as exc:
            logger = self.get_logger()
            logger.error(_('app.input_file_cannot_be_opened'), {'f': path, 'exc': str(exc)})
            logger.debug('', exc_info=True)
            return (None, None)

    def _create_writer(self, path: str, reader: ZsndWavReader, force_overwrite: bool) \
            -> tuple[io.BufferedIOBase|None, ZsndWavWriter|None]:
        try:
            if os.path.exists(path) and not force_overwrite:
                if not typer.confirm(_('app.confirm_overwrite_output_file') % (path)):
                    raise typer.Exit(0)
            outf = io.open(path, 'wb')
            try:
                bytes_per_sample = reader.get_wave_format().get_bytes_per_sample()
                return (outf, ZsndWavWriter(outf, bytes_per_sample, reader.get_sample_rate()))
            except BaseException as exc:
                outf.close()
                raise
        except typer.Exit:
            raise
        except Exception as exc:
            logger = self.get_logger()
            logger.error(_('app.output_file_cannot_be_opened'),
                    {'f': path, 'exc': str(exc)})
            logger.debug('', exc_info=True)
            return (None, None)
