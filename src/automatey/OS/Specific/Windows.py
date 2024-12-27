
# ? Internal Libraries
import automatey.OS.FileUtils as FileUtils

# ? Standard Libraries
import winreg

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
            commandKeyPath = fr"{entryKeyPath}\command"
            iconKeyPath = fr"{entryKeyPath}\DefaultIcon"

            # ? Key: Entry.
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, entryKeyPath) as entryKey:
                winreg.SetValue(entryKey, "", winreg.REG_SZ, name)

            # ? Key: Command.
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, commandKeyPath) as commandKey:
                winreg.SetValue(commandKey, "", winreg.REG_SZ, command)

            # ? Key: Icon.
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, iconKeyPath) as iconKey:
                winreg.SetValue(iconKey, "", winreg.REG_SZ, INTERNAL.asPath(f_icon))
