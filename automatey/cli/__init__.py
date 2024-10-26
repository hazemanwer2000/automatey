
import click
import automatey.cli.img.faces

#------------\
# [L-1]: CLI

#------------\------------\
# [L-2]: Image-Edit

#------------\------------\------------\
# [CMD]: Face-Detection

@click.option('--rotate', type=click.INT, default=0, help="Specify a rotation (right-)angle. '-1' for all-rotation(s).")
@click.option('--outline', is_flag=True, default=False, help='Rectangle placed around a face is not filled.')
@click.option('--copy', is_flag=True, default=False, help='Keep a copy of the original file.')
@click.option('-o', '--output', default=None, help='Path to output directory, or file.')
@click.option('-i', '--input', required=True, help='Path to input directory, or file (e.g., image, video, GIF).')
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