# coding: utf-8

from collapse_wav_dropouts import AudioDropoutCollapserApp
import sys

if __name__ == '__main__':
    the_app = AudioDropoutCollapserApp()
    sys.exit(the_app.run())
