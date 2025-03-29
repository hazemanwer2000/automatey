
# ? Internal Libraries
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.StringUtils as StringUtils

# ? Standard Libraries
import winreg
import os

# ? External Libraries
import winshell
import natsort

class Registry:
    
    class ContextMenu:
        
        class FileCategory:
            
            class AllDirectories:
                '''
                Applies whenever a directory is right-clicked.
                '''
                pass
            class AllDirectoriesAsBackground:
                '''
                Applies whenever the empty space within a directory is right-clicked.
                '''
                pass
            class AllFiles:
                '''
                Applies whenever a file is right-clicked.
                '''
                pass
            class SpecificExtension:
                '''
                Applies whenever a file with a specific extension is right-clicked.
                '''
                pass
            
            INTERNAL_mapping = {
                AllDirectoriesAsBackground : 'Directory\Background',
                AllDirectories : 'Directory',
                AllFiles : '*',
                SpecificExtension : None,
            }
    
        @staticmethod
        def createCommand(name:str, command:str, f_icon:FileUtils.File, fileCategory:"FileCategory", extension:str=None):
            '''
            Creates a command with a name and icon, and associates it with the given file category.
            
            Note that,
            - The icon must be in `.ico` format.
            - If extensions is used, it must be without a dot.
            '''
            
            # ? Determine file association.
            if fileCategory != Registry.ContextMenu.FileCategory.SpecificExtension:
                fileAssociation = Registry.ContextMenu.FileCategory.INTERNAL_mapping[fileCategory]
            else:
                fileAssociation = '.' + extension
            
            # ? Key path(s).
            baseKeyPath = fr"{fileAssociation}\shell"
            entryKeyPath = fr"{baseKeyPath}\{name}"

            # ? Setting key.
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, entryKeyPath) as entryKey:
                winreg.SetValue(entryKey, "", winreg.REG_SZ, name)
                winreg.SetValue(entryKey, "command", winreg.REG_SZ, command)
                winreg.SetValueEx(entryKey, "Icon", 0, winreg.REG_SZ, Utils.File2Path(f_icon))
    
    @staticmethod            
    def setAutoRun(f_batch:FileUtils.File):
        '''
        Sets the Auto-Run batch file (i.e., `.bat` file that executes automatically with every CMD opened).
        '''
        targetPath = Utils.File2Path(f_batch, isDoubleQuoted=True)
        entryKeyPath = fr"Software\Microsoft\Command Processor"

        # ? Setting key.
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, entryKeyPath) as entryKey:
            winreg.SetValueEx(entryKey, "AutoRun", 0, winreg.REG_SZ, targetPath)

class Shortcut:
    
    @staticmethod
    def toStartMenu(name:str, f_icon:FileUtils.File, f_exe:FileUtils.File):
        '''
        Create a shortcut, and place it in the `Start Menu`.
        '''
        targetPath = Utils.File2Path(f_exe)
        iconPath = Utils.File2Path(f_icon)
        start_menu_path = os.path.join(winshell.start_menu(), "Programs")
        shortcut_path = os.path.join(start_menu_path, f"{name}.lnk")
        
        # ? Create the shortcut.
        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = targetPath
            shortcut.description = name
            shortcut.working_directory = os.path.dirname(targetPath)
            shortcut.icon_location = (iconPath, 0)

class Utils:
    
    @staticmethod
    def sorted(iterable, key=None):
        '''
        Sort a list, via a key-string, according to criteria used by Windows Built-in Application(s) (e.g., File Explorer).
    
        Note that, similar to Python's built-in `sorted`, creates a new list.
        '''
        return natsort.natsorted(iterable, key=key)
    
    @staticmethod
    def sort(iterable, key=None):
        '''
        Sort a list, via a key-string, according to criteria used by Windows Built-in Application(s) (e.g., File Explorer).
    
        Note that, similar to Python's built-in `sort`, sorts in-place.
        '''
        natsort_key = natsort.natsort_keygen()
        kwargs = {}
        if key != None:
            kwargs['key'] = lambda x: natsort_key(key(x))
        iterable.sort(**kwargs)
    
    @staticmethod
    def File2Path(f:FileUtils.File, isDoubleQuoted:bool=False) -> str:
        '''
        Returns *Windows*-specific path of file.
        '''
        path = str(f).replace('/', '\\')
        if isDoubleQuoted:
            path = StringUtils.Simply.doubleQuote(path)
        return path
