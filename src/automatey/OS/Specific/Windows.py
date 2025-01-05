
# ? Internal Libraries
import automatey.OS.FileUtils as FileUtils

# ? Standard Libraries
import winreg
import os
import winshell

class INTERNAL:

    def asPath(f:FileUtils.File, isQuoted=False) -> str:
        '''
        Returns *Windows*-specific path of file.
        '''
        path = str(f).replace('/', '\\')
        if isQuoted:
            path = '"' + path + '"'
        return path

class Registry:
    
    class ContextMenu:
        
        class FileCategory:
            
            class AllDirectories: pass
            class AllFiles: pass
            class SpecificExtension: pass
            
            INTERNAL_mapping = {
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
                winreg.SetValueEx(entryKey, "Icon", 0, winreg.REG_SZ, INTERNAL.asPath(f_icon))
    
    @staticmethod            
    def setAutoRun(f_batch:FileUtils.File):
        '''
        Sets the Auto-Run batch file (i.e., `.bat` file that executes automatically with every CMD opened).
        '''
        targetPath = INTERNAL.asPath(f_batch, isQuoted=True)
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
        targetPath = INTERNAL.asPath(f_exe)
        iconPath = INTERNAL.asPath(f_icon)
        start_menu_path = os.path.join(winshell.start_menu(), "Programs")
        shortcut_path = os.path.join(start_menu_path, f"{name}.lnk")
        
        # ? Create the shortcut.
        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = targetPath
            shortcut.description = name
            shortcut.working_directory = os.path.dirname(targetPath)
            shortcut.icon_location = (iconPath, 0)
