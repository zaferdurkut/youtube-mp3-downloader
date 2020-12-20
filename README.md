# Youtube Downloader
Youtube single or multiple (playlist) song downloader with youtube-dl library with mp3 output type
Maybe you can try with youtube-dl but for my case youtube-dl don't support mp3 output type
#### Request
```
youtube-dl -i -f mp3 --yes-playlist 'https://www.youtube.com/watch?v=BaW_jenozKc&ab_channel=PhilippHagemeister'
```
#### Result
```
[youtube] hxEtaxWgUCA: Downloading webpage
ERROR: requested format not available
```
## Installation
if you use Mac OS, you should install ffmpeg (for other operating systems, you can google)

```
brew install ffmpeg
```

You can build virtualenv library
```
virtual env
```
For python library
```
source venv/bin/activate
```
For Active
```
pip install -r requirements.txt 
```
## Usage
```
 python downloader.py --output_folder downloaded_songs --url https://www.youtube.com/watch?v=BaW_jenozKc&ab_channel=PhilippHagemeister
```

