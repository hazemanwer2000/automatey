
import click
import automatey.cli.img.faces

#------------\
# [L-1]: CLI

#------------\------------\
# [L-2]: Image-Edit

#------------\------------\------------\
# [CMD]: Face-Detection

@click.command()
def CMD_img_faces():
    automatey.cli.img.faces.run()

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