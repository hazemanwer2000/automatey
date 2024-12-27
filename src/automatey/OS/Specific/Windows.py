
import automatey.OS.FileUtils as FileUtils

import winreg

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
            commandKeyPath = fr"{entryKeyPath}\command"
            iconKeyPath = fr"{entryKeyPath}\DefaultIcon"
            
            print(commandKeyPath)
            
            exit(0)

            # ? Key: Entry.
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, entryKeyPath) as entryKey:
                winreg.SetValue(entryKey, "", winreg.REG_SZ, name)

            # ? Key: Command.
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, commandKeyPath) as commandKey:
                winreg.SetValue(commandKey, "", winreg.REG_SZ, command)

            # ? Key: Icon.
            #with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, iconKeyPath) as iconKey:
            #    winreg.SetValue(iconKey, "", winreg.REG_SZ, f_icon)  # Set icon path