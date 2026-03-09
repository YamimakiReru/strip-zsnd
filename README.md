# strip-zsnd
Detect and strip audio skips in WAV files to mitigate audio issues such as buffer underflow during recording.

You can run the GUI version of this application in the browser at:<br />
https://do.symphonic.lol/app.php/strip-zsnd/

## Limitations
- Only mono `.wav` files are supported.
- This tool can **mitigate** audio skips, but in many cases it cannot **fully restore** audio glitches. See "[How it works]( https://github.com/YamimakiReru/strip-zsnd/wiki )"

## In Japanese (日本語説明)
WAVファイル内の一定の音飛び区間を検知・除去し、録音時に生じたバッファアンダーフローを軽減します。

ブラウザ上で動作するGUI版は、以下のURLからも利用できます:<br />
https://do.symphonic.lol/app.php/strip-zsnd/

詳しい説明は [Wiki]( https://github.com/YamimakiReru/strip-zsnd/wiki/日本語 ) をご覧ください。

### 制限
- モノラルWAV形式のみのサポートです。
- このツールは一定の音飛びを **緩和** しますが、ある程度以上の長さの音源については **完全な修復** は困難なことが多いです。「[アプローチ]( https://github.com/YamimakiReru/strip-zsnd/wiki/日本語 )」をご参照ください。

### 基本的な使い方
1. **「ファイルの選択」** ボタンをクリックし、WAVファイルを読み込みます
    - 音飛びはファイル読み込み時に自動で検出されます
2. 音飛びを一つ一つ確認して消すか、もしくは🌙メニューの**「全ドロップアウトを除去」**で一括処理できます。
3. 🌙メニューの **「保存」** ボタンを押下すると処理結果をダウンロードできます。

## Installation

### Browser version
Installation is not required.
You can use it at: https://do.symphonic.lol/app.php/strip-zsnd/

### GUI version
It works almost the same as the browser version, but it does not pick up my recent info shown in the browser app ;)

Download the zip file, extract it, and open index.html.

### CLI version for Windows
Download the zip file and execute `strip-zsnd.exe`.

Run `strip-zsnd.exe --help` for more detailed information.

### CLI version for *nix-like systems
This tool requires Python 3 and Bash.

```bash
git clone git@github.com:YamimakiReru/strip-zsnd.git
cd strip-zsnd
./strip-zsnd --help
```
A venv is automatically initialized upon first execution.

## Basic Usage
1. Click **"Choose File"** button and open a `.wav` file.
    - *Dropouts are automatically detected when opening the file.*
2. Remove dropouts individually, or select **"Trim all dropouts"** from the 🌙 menu.
3. Select **"Save"** from the 🌙 menu to export the processed file.

See [the Wiki]( https://github.com/YamimakiReru/strip-zsnd/wiki ) for more details.

## License

This project is licensed under the MIT License.  
See the LICENSE file for details.
