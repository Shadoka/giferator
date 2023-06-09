import cv2 as cv
import imageio
import argparse
from pygifsicle import optimize
from enum import Enum

class Color(Enum):
    BLACK   = (0, 0, 0)
    WHITE   = (255, 255, 255)
    RED     = (0, 0, 255)
    GREEN   = (0, 255, 0)
    BLUE    = (255, 0, 0)
    YELLOW  = (0, 255, 255)

def getFramesFromVideo(filepath, startString, duration=2, reverse=False):
    """
    Loads a video file and returns the frames beginning from the specified
    offset with the given duration.
    Returns tupel of (frames, fps)

    filepath : Location of the video file
    startString : Start timestamp in video
    duration : How many seconds of frames should be collected
    """
    if duration <= 0:
        print(f"can't make a gif out of a video with a duration of {duration}")
        return [], 0

    result = []
    src = cv.VideoCapture(str(filepath))
    fps = src.get(cv.CAP_PROP_FPS)
    videoLength = src.get(cv.CAP_PROP_FRAME_COUNT)
    framesRequired = int(duration * fps)

    try:
        start, offsetSeconds = calculateStart(startString, fps)
    except:
        src.release()
        return result, fps

    if start > videoLength:
        print("the beginning of the gif is set after the video has ended")
        print(f"video duration:\t{int(videoLength / fps / 60)}:{round(videoLength / fps) % 60} minutes")
        print(f"start of gif:\t{int(offsetSeconds / 60)}:{offsetSeconds % 60} minutes")
        return result, fps
    
    if framesRequired + start > videoLength:
        print("the end of the gif is scheduled to be after the video has ended")
        print(f"video duration:\t{int(videoLength / fps / 60)}:{round(videoLength / fps) % 60} minutes")
        print(f"end of the gif:\t{int((framesRequired + start) / fps / 60)}:{round((framesRequired + start) / fps) % 60} minutes")
        return result, fps

    src.set(cv.CAP_PROP_POS_FRAMES, start)

    readFrames = 0
    while readFrames < framesRequired:
        ret, frame = src.read()
        readFrames += 1
        if ret:
            result.append(frame)
        else:
            print("could not read frame from video")

    src.release()

    if reverse:
        result = result[::-1]

    return result, fps

def saveGif(frames, fps, filepath):
    """
    Saves the given frames as a .gif file.

    frames : Frames to be saved as gif
    fps : FPS of the gif
    filepath : Location of the gif file
    """
    framesGif = list(map(lambda f: cv.cvtColor(f, cv.COLOR_BGR2RGB), frames))

    imageio.mimsave(filepath, framesGif, fps=fps)

def reduceFrames(frames, cull=3):
    """
    Reduces the number of frame by the given cull amount.
    Returns a list of frames with the length of int(len(frames) / 3)

    frames : List of frames
    cull : The amount the list of frames should be reduced by
    """
    result = []
    for i in range(len(frames)):
        if i % cull == 0:
            result.append(frames[i])

    return result

def autoscaleTextSize(imageShape, text, thickness, font=cv.FONT_HERSHEY_SIMPLEX):
    """
    Finds the maximum text size the given text can be displayed while having
    a certain padding to the sides.
    Returns the text size (fontScale) as float.

    imageShape : The shape of an image frame
    text : The string to be displayed
    font : The font to use
    thickness : The thickness of the text
    """
    # TODO: Handle text that requires a linebreak
    _, imageWidth, _ = imageShape
    paddingHorizontal = 100
    maxTextWidth = imageWidth - paddingHorizontal * 2
    fontScale = 1.0
    textSize, _ = cv.getTextSize(text, font, fontScale, thickness)
    textWidth, _ = textSize

    while textWidth < maxTextWidth:
        fontScale += 1.
        textSize, _ = cv.getTextSize(text, font, fontScale, thickness)
        textWidth, _ = textSize

    # FIXME: buggy when text with font scale 1 is already too long
    return fontScale - 1.

def writeCenteredText(frames, text, fontScale, thickness, color, outlineColor, font=cv.FONT_HERSHEY_SIMPLEX):
    """
    Writes the specified text with the given font settings into every
    frame in 'frames'.
    Returns the altered list of frames.

    frames : List of image frames
    text : Text to be written in each frame
    fontScale : Font size
    thickness : Thickness of the writing
    color : Color of the text
    outline : Color of the outline of the text
    font : Font to be used
    """
    paddingVertical = 100

    textSize, _ = cv.getTextSize(text, font, fontScale, thickness)
    textWidth, textHeight = textSize

    _, imageWidth, _ = frames[0].shape
    textOrigin = (int((imageWidth - textWidth) / 2), textHeight + paddingVertical)

    for i in range(len(frames)):
        currentImage = cv.putText(img=frames[i],
                               text=text,
                               org=textOrigin,
                               fontFace=font,
                               fontScale=fontScale,
                               color=outlineColor.value,
                               thickness=thickness + 2)
        frames[i] = cv.putText(img=currentImage,
                               text=text,
                               org=textOrigin,
                               fontFace=font,
                               fontScale=fontScale,
                               color=color.value,
                               thickness=thickness)
        
    return frames

def scaleImages(frames, scaleFactor):
    """
    Scales the image frames by the given scaleFactor.
    Returns the scaled frames.

    frames : List of image frames
    scaleFactor : Factor the images get scaled by
    """
    height, width, _ = frames[0].shape
    newDimensions = (int(width * scaleFactor), int(height * scaleFactor))

    for i in range(len(frames)):
        frames[i] = cv.resize(frames[i], newDimensions, interpolation=cv.INTER_AREA)

    return frames

def calculateStart(startString, fps):
    """
    Calculates the offset of the start of the gif recording by parsing
    the given string and multiplying the result with the fps of the video.
    Returns the index of the frame with which to start the gif recording and
    the offset in the video in seconds.

    startString : Start of the gif recording as string
    fps : FPS of the video to make the gif from
    """
    timeComponents = startString.split(":")
    if len(timeComponents) == 1 or len(timeComponents) > 3:
        raise Exception("time has to be in the format (h:)m:s")
    
    seconds = 0
    if len(timeComponents) == 2:
        seconds += int(timeComponents[0]) * 60 + int(timeComponents[1])
    elif len(timeComponents) == 3:
        seconds += timeComponents[0] * 60 * 60 + timeComponents[1] * 60 + timeComponents[2]

    return int(seconds * fps), seconds

def parseColor(colorString):
    match colorString.lower():
        case "black":
            return Color.BLACK
        case "white":
            return Color.WHITE
        case "red":
            return Color.RED
        case "green":
            return Color.GREEN
        case "blue":
            return Color.BLUE
        case "yellow":
            return Color.YELLOW
        case _:
            return Color.BLACK
        

parser = argparse.ArgumentParser(description="Generate Gifs out of videos")
parser.add_argument("--start", required=True, help="start timestamp in the video of the gif recording, e.g. 5:35")
parser.add_argument("--duration", required=True, type=float, help="duration of the gif recording in seconds")
parser.add_argument("--input", required=True, help="input video to make the gif from")
parser.add_argument("--out", required=True, help="output file path for the gif")
parser.add_argument("--text", required=False, help="text to put into the gif")
parser.add_argument("--image-scale", required=False, type=float, help="factor the image size gets scaled by. default is 0.5")
parser.add_argument("--reverse", required=False, action="store_true", help="whether the gif should play in reverse. default is false")
parser.add_argument("--optimize-size", required=False, action="store_true", help="whether the gif should be optimized for filesize. default is false")
parser.add_argument("--cull", required=False, type=int, help="how much of the frames of the video get reduced by for the gif. default is 3")
parser.add_argument("--color", required=False, help="color of the text (available: red, blue, green, yellow, black, white). default is black")
parser.add_argument("--outline-color", required=False, help="color of the outline of the text (available: red, blue, green, yellow, black, white). default is white")
parser.add_argument("--tell-fps", required=False, action="store_true", help="Prints out the fps of the underlying source material")
parser.add_argument("--fps", required=False, help="Overrides the calculated fps of the resulting gif")

args = parser.parse_args()

frames, fps = getFramesFromVideo(args.input, startString=args.start, duration=args.duration, reverse=args.reverse)
if args.tell_fps:
    print(f"the input material has {fps} fps")

cull = 3
if not args.cull == None:
    cull = args.cull
frames = reduceFrames(frames, cull)

if not args.text == None:
    color = Color.BLACK
    if not args.color == None:
        color = parseColor(args.color)
    
    outlineColor = Color.WHITE
    if not args.outline_color == None:
        outlineColor = parseColor(args.outline_color)

    thickness = 6
    fontScale = autoscaleTextSize(frames[0].shape, args.text, thickness)
    frames = writeCenteredText(frames, args.text, fontScale, thickness, color, outlineColor)

imageScale = 0.5
if not args.image_scale == None:
    imageScale = args.image_scale

frames = scaleImages(frames, imageScale)

gifFps = fps / cull
if not args.fps == None:
    gifFps = args.fps

saveGif(frames, gifFps, args.out)

if args.optimize_size:
    optimize(args.out)