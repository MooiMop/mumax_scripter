import Modules.tools as tools
import imageio
import ffmpy
from tqdm import tqdm
import time

def makemovie(images, fps=10, delete=False):
    '''
    Goal: Make a gif and mp4 of the list of images that are inputted.
    Inputs:
        -images([str]): list of filenames. Should all be jpg. Png does not always work.
        -fps(int): frames per second.
        -delete(bool): whether to delete files after making the animation.
    '''
    tools.logprint('Checking images for corruption.')
    images = tools.corruption_check(images)

    tools.logprint('Making gif...')
    source = [imageio.imread(str(image)) for image in images]
    imageio.mimwrite('movie.gif', source, fps=fps)
    tools.logprint('Gif saved')

    tools.logprint('Making mp4...')

    ff = ffmpy.FFmpeg(
      inputs={'movie.gif': None},
      outputs={'movie.mp4': None})

    try:
      ff.run()
      tools.logprint('mp4 saved')
    except ffmpy.FFExecutableNotFoundError:
      tools.logprint('Executable ffmpeg not found.')
    except:
      tools.logprint('Mp4 already exists.')

    if (delete) & (len(tools.find('movie.mp4'))!= []):
      tools.delete(images)
