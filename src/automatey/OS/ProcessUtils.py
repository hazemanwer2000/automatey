
# Internal libraries
import automatey.Utils.StringUtils as StringUtils

# Standard libraries
import subprocess

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
            strippedText = self.template.strip()
            normalizedText = StringUtils.Regex.replaceAll(r'\s+', ' ', strippedText)
            return normalizedText
        
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
        # Joining all, then splitting again.
        self.command = (' '.join(args)).split(sep=' ')
        
        self.stdout = None
        self.stderr = None
    
    def run(self, STDOUT2DEVNULL=False, STDERR2DEVNULL=False) -> int:
        '''
        Executes command, synchronously.
        '''
        stdoutRedirection = subprocess.DEVNULL if STDOUT2DEVNULL else subprocess.PIPE
        stderrRedirection = subprocess.DEVNULL if STDERR2DEVNULL else subprocess.PIPE
        
        proc = subprocess.Popen(self.command, stdout=stdoutRedirection, stderr=stderrRedirection, text=True)
        self.stdout, self.stderr = proc.communicate()
        return proc.returncode
    
    def STDOUT(self):
        return self.stdout
    
    def STDERR(self):
        return self.stderr