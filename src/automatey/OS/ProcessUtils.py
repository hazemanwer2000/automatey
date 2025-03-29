
# Internal libraries
import automatey.Utils.StringUtils as StringUtils
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

# Standard libraries
import subprocess
import shlex

class FileTemplate:
    '''
    A file template.
    
    May include:
    - Section(s), represented as `{{{SECTION-NAME: ... :}}}`
    - Parameter(s), represented as `{{{PARAMETER-NAME}}}`
    
    Note that,
    - All name(s) must be upper-case.
    - Section name(s) must be unique (or, repeated, but identical in content).
    - When nesting, inner section(s) must be asserted first.
    '''
    
    def __init__(self, template):
        self.template = template
        
    @staticmethod
    def fromFile(f:FileUtils.File) -> "FileTemplate":
        '''
        Create template from file.
        '''
        with f.openFile('rt') as f_opened:
            template = f_opened.readAny()
        return FileTemplate(template)
    
    def createFormatter(self) -> "FileTemplate.Formatter":
        '''
        Creates a formatter object, to be used to format the template into a file.
        
        As many formatter object(s) may be created.
        '''
        return FileTemplate.Formatter(self.template)

    class Formatter:
        
        def __init__(self, template:str):
            self.template = template
        
        def assertSection(self, sectionName:str, params:dict=None):
            '''
            Assert a section, asserting contained parameter value(s).
            '''
            params = {} if (params == None) else params
            self.template = FileTemplate.Formatter.INTERNAL_Utils.assertSection(sectionName, params, self.template)
        
        def assertParameter(self, paramName:str, paramValue:str):
            '''
            Assert parameter value.
            '''
            self.template = FileTemplate.Formatter.INTERNAL_Utils.assertParameter(paramName, paramValue, self.template)
        
        def excludeSection(self, sectionName:str):
            '''
            Remove a section.
            '''
            self.template = FileTemplate.Formatter.INTERNAL_Utils.excludeSection(sectionName, self.template)
        
        def __str__(self):
            return self.template
        
        def __repr__(self):
            return str(self)
        
        def saveAs(self, f:FileUtils.File):
            '''
            Save to file.
            '''
            if f.isExists():
                raise ExceptionUtils.ValidationError('Destination file must not exist.')

            with f.openFile('wt') as f_opened:
                f_opened.writeAny(str(self))
    
        class INTERNAL_Utils:
            
            class Regex:
                
                @staticmethod
                def formatSectionExpression(sectionName:str):
                    '''
                    Format a section Regex match expression.
                    '''
                    return r'{{{' + sectionName.upper() + ':' + r'([\s\S]*?)' + r':}}}'
                
                @staticmethod
                def formatParameterExpression(paramName:str):
                    '''
                    Format a parameter Regex match expression.
                    '''
                    return r'{{{' + paramName.upper() + r'}}}'
                
            @staticmethod
            def assertParameter(paramName:str, paramValue:str, txt):
                '''
                Assert parameter value.
                '''
                paramExpr = FileTemplate.Formatter.INTERNAL_Utils.Regex.formatParameterExpression(paramName)
                txt = StringUtils.Regex.replaceAll(paramExpr, paramValue, txt)
                return txt

            @staticmethod
            def assertSection(sectionName:str, params:dict, txt):
                '''
                Assert a section, asserting contained parameter value(s).
                '''
                sectionExpr = FileTemplate.Formatter.INTERNAL_Utils.Regex.formatSectionExpression(sectionName)
                sectionContent = StringUtils.Regex.findAll(sectionExpr, txt)[0]
                for paramName in params:
                    sectionContent = FileTemplate.Formatter.INTERNAL_Utils.assertParameter(paramName, params[paramName], sectionContent)
                txt = StringUtils.Regex.replaceAll(sectionExpr, sectionContent, txt)
                return txt
            
            @staticmethod
            def excludeSection(sectionName:str, txt):
                '''
                Remove a section.
                '''
                sectionExpr = FileTemplate.Formatter.INTERNAL_Utils.Regex.formatSectionExpression(sectionName)
                txt = StringUtils.Regex.replaceAll(sectionExpr, '', txt)
                return txt

class CommandTemplate:
    '''
    A command template.
    
    May include:
    - Section(s), represented as `{{{SECTION-NAME: ... :}}}`
    - Parameter(s), represented as `{{{PARAMETER-NAME}}}`
    
    Note that,
    - All name(s) must be upper-case.
    - Section name(s) must be unique (or, repeated, but identical in content).
    - When nesting, inner section(s) must be asserted first.
    '''
    
    def __init__(self, *args):
        self.template = ' '.join(args)
    
    def createFormatter(self):
        '''
        Creates a formatter object, to be used to format the template into a command.
        
        As many formatter object(s) may be created.
        '''
        return CommandTemplate.Formatter(self.template)

    class Formatter:
        
        def __init__(self, template:str):
            self.template = template
        
        def assertSection(self, sectionName:str, params:dict=None):
            '''
            Assert a section, asserting contained parameter value(s).
            '''
            params = {} if (params == None) else params
            self.template = CommandTemplate.Formatter.INTERNAL_Utils.assertSection(sectionName, params, self.template)
        
        def assertParameter(self, paramName:str, paramValue:str):
            '''
            Assert parameter value.
            '''
            self.template = CommandTemplate.Formatter.INTERNAL_Utils.assertParameter(paramName, paramValue, self.template)
        
        def excludeSection(self, sectionName:str):
            '''
            Remove a section.
            '''
            self.template = CommandTemplate.Formatter.INTERNAL_Utils.excludeSection(sectionName, self.template)
        
        def __str__(self):
            return StringUtils.Normalize.asSentence(self.template)
        
        def __repr__(self):
            return str(self)
    
        class INTERNAL_Utils:
            
            class Regex:
                
                @staticmethod
                def formatSectionExpression(sectionName:str):
                    '''
                    Format a section Regex match expression.
                    '''
                    return r'{{{' + sectionName.upper() + ':' + r'(.*?)' + r':}}}'
                
                @staticmethod
                def formatParameterExpression(paramName:str):
                    '''
                    Format a parameter Regex match expression.
                    '''
                    return r'{{{' + paramName.upper() + r'}}}'
                
            @staticmethod
            def assertParameter(paramName:str, paramValue:str, txt):
                '''
                Assert parameter value.
                '''
                paramExpr = CommandTemplate.Formatter.INTERNAL_Utils.Regex.formatParameterExpression(paramName)
                txt = StringUtils.Regex.replaceAll(paramExpr, paramValue, txt)
                return txt

            @staticmethod
            def assertSection(sectionName:str, params:dict, txt):
                '''
                Assert a section, asserting contained parameter value(s).
                '''
                sectionExpr = CommandTemplate.Formatter.INTERNAL_Utils.Regex.formatSectionExpression(sectionName)
                sectionContent = StringUtils.Regex.findAll(sectionExpr, txt)[0]
                for paramName in params:
                    sectionContent = CommandTemplate.Formatter.INTERNAL_Utils.assertParameter(paramName, params[paramName], sectionContent)
                txt = StringUtils.Regex.replaceAll(sectionExpr, sectionContent, txt)
                return txt
            
            @staticmethod
            def excludeSection(sectionName:str, txt):
                '''
                Remove a section.
                '''
                sectionExpr = CommandTemplate.Formatter.INTERNAL_Utils.Regex.formatSectionExpression(sectionName)
                txt = StringUtils.Regex.replaceAll(sectionExpr, '', txt)
                return txt

class Process:
    '''
    Representation of a (sub-)process.
    '''
    
    def __init__(self, *args):
        self.command = StringUtils.Split.asCommand(args)
        self.stdout = None
        self.stderr = None
    
    def run(self, STDOUT2DEVNULL=False, STDERR2DEVNULL=False) -> int:
        '''
        Executes command, synchronously.
        '''
        stdoutRedirection = subprocess.DEVNULL if STDOUT2DEVNULL else subprocess.PIPE
        stderrRedirection = subprocess.DEVNULL if STDERR2DEVNULL else subprocess.PIPE
        
        proc = subprocess.Popen(self.command, stdout=stdoutRedirection, stderr=stderrRedirection, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        self.stdout, self.stderr = proc.communicate()
        return proc.returncode
    
    def STDOUT(self):
        return self.stdout
    
    def STDERR(self):
        return self.stderr