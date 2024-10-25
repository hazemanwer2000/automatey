
import click
import automatey.cli.img.faces

#------------\
# [L-1]: CLI

#------------\------------\
# [L-2]: Image-Edit

#------------\------------\------------\
# [CMD]: Face-Detection

@click.option('--rotate', is_flag=True, default=False, help='Rotate each image (+/-)90 and 180, before processing. This quadruples the processing time.')
@click.option('-o', '--output', default=None, help='Path to output directory.')
@click.command(help='Detect faces in an image.')
def CMD_img_faces(**kwargs):
    automatey.cli.img.faces.run(kwargs)

#------------\------------\------------\

@click.group()
def GroupCMD_img():
    pass

GroupCMD_img.add_command(CMD_img_faces, name='faces')

#------------\------------\

@click.group()
def GroupCMD_cli():
    pass

GroupCMD_cli.add_command(GroupCMD_img, name='img')

#------------\