# giferator

Always dreamt of creating your own fancy gifs? Dream no more!

![naked gun](examples/nakedgun.gif)

You can put text captions into the gifs and even reverse scenes!

![caption gif](examples/example_caption.gif)
![reversed gif](examples/example_reversed.gif)

## Usage

Described here are the parameters available and their usage for generating the gifs shown in this readme.

### Parameters

| Name | Description | Example | Optional? |
|------|-------------|---------|-----------|
| --start | Defines when the gif recording in the video should start | `--start "5:35"` | No |
| --duration | Sets how many seconds of video material is used for the gif | `--duration 5` | No |
| --input | File path to the video the gif should be created from | `--input source/video.mp4` | No |
| --out | File path of the resulting gif | `--out output/example.gif` | No |
| --text | Text to be displayed in the gif. It will be horizontally centered with (currently) not customizable paddings. | `--text "Lorem ipsum"` | Yes |
| --image-scale | Defines how much the gif images get scaled. Defaults to 0.5 | `--image-scale 0.9` | Yes |
| --reverse | Whether or not the gif should play in reverse. Defaults to false. | `--reverse` | Yes |
| --optimize-size | Tries to perform some compression on the gif. Does not work well and has additional dependency requirements | `--optimize-size` | Yes |
| --cull | Reduces the fps of the gif (in relation to the fps of the video) by the specified amount. Default is 3 | `--cull 3` | Yes |
| --color | Color of the text (available: red, blue, green, yellow, black, white). Default is black | `--color "red"`| Yes |
| --outline-color | Color of the outline of the text. See above for values. Default is white | `--outline-color "yellow"` | Yes |
| --tell-fps | Writes out the fps of the video source material | `--tell-fps` | Yes |
| --fps | Overrides the calculated fps of the gif. Higher fps = faster playback | `--fps 25` | Yes |

### Gif without caption

![naked gun](examples/nakedgun.gif)

`python .\giferator.py --start "19:19" --duration 5 --input .\source\video2.avi --out .\output\nakedgun.gif --image-scale 0.7`

### Gif with caption

![caption gif](examples/example_caption.gif)

`python .\giferator.py --start "17:30" --duration 5 --text "Me taking out trash mobs" --input .\source\video.mp4 --out .\output\example_caption.gif`

### Reversed gif with caption

![reversed gif](examples/example_reversed.gif)

`python .\giferator.py --start "17:30" --duration 5 --text "Me when I hear boss music playing" --input .\source\video.mp4 --out .\output\example_reversed.gif --reverse`

## Dependencies

Python has to be in version >= 3.10.
The following dependencies are required to run giferator:

* opencv-python
* imageio
* pygifsicle

If you wish to use the compression flag (--optimize-size) you need to additionally install [pygifsicle](https://pypi.org/project/pygifsicle/).
Besides installing it via `pip install` you may need to perform additional steps, depending on your OS.
In my experiments the file size wasn't drastically improved but the quality of the resulting gif was much worse.

## How to reduce file size

You have three options to reduce the file size of the resulting gif:

1. You can scale down the image size via `--image-scale`. The smaller the scale factor, the smaller the resulting gif.
2. You can use `--cull` to include less frames in your gif. A higher cull results in a smaller gif, but the gif gets more choppier.
3. (Not recommended) You can use `--optimize-size` if you have pygifsicle installed. It reduces the gif by a bit, but the quality gets noticeably worse.