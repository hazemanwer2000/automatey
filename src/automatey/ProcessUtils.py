
# Internal libraries
import automatey.StringUtils as StringUtils

# Standard libraries
import subprocess

class Utils:
    
    class Command:
        
        @staticmethod
        def normalize(inputCommand:str):
            strippedCommand = inputCommand.strip()
            normalizedCommand = StringUtils.Regex.replaceAll(r'\s+', ' ', strippedCommand)
            return normalizedCommand

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
            return Utils.Command.normalize(self.template)
        
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

class STD: pass
        
class STDOUT(STD): pass
class STDERR(STD): pass

class Process:
    
    def __init__(self, *args):
        self.command = args
        self.callouts = {
            STDOUT: None,
            STDERR: None,
        }
        self.proc = None
    
    def registerCallout(self, STDType:STD, calloutFcn):
        '''
        Register a callout, per STD, to be called with every line read.
        '''
        self.callouts[STDType] = calloutFcn
    
    def run(self) -> int:
        '''
        Creates process, and executes command, synchronously.
        '''
        self.proc = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        isSTDOUTCallout = self.callouts[STDOUT] != None
        isSTDERRCallout = self.callouts[STDERR] != None
        
        while (isSTDOUTCallout or isSTDERRCallout):
            
            if (isSTDOUTCallout):
                line = self.proc.stdout.readline()
                if (line):
                    self.callouts[STDOUT](line)
                else:
                    isSTDOUTCallout = False

            if (isSTDERRCallout):
                line = self.proc.stderr.readline()
                if (line):
                    self.callouts[STDERR](line)
                else:
                    isSTDERRCallout = False
        
        return self.proc.wait()
    
    def STDOUT(self):
        '''
        Get STDOUT. If a callout is configured, this must not be used.
        '''
        return self.proc.stdout.read()
    
    def STDERR(self):
        '''
        Get STDERR. If a callout is configured, this must not be used.
        '''
        return self.proc.stderr.read()