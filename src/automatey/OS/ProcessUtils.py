
# Internal libraries
import automatey.Utils.StringUtils as StringUtils
import automatey.OS.FileUtils as FileUtils
import automatey.Utils.ExceptionUtils as ExceptionUtils

# Standard libraries
import subprocess
import shlex
import threading

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
    Creates and manages a process.
    '''
    
    def __init__(self, *args):

        command = StringUtils.Split.asCommand(*args)
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        self.status = None

        self.STDOUT_lines = []
        self.STDERR_lines = []
        self.stdout = None
        self.stderr = None
        
        self.STDOUT_thread = threading.Thread(target=Process.INTERNAL_runnable_PIPEReader, args=(self.process.stdout, self.STDOUT_lines), daemon=True)
        self.STDERR_thread = threading.Thread(target=Process.INTERNAL_runnable_PIPEReader, args=(self.process.stderr, self.STDERR_lines), daemon=True)
        self.STDOUT_thread.start()
        self.STDERR_thread.start()

    @staticmethod
    def INTERNAL_runnable_PIPEReader(pipe, lines):
        for line in iter(pipe.readline, ''):
            lines.append(line)
        pipe.close()

    def wait(self) -> int:
        '''
        Waits for process to complete, and returns status.
        '''
        if self.status is None:
            self.status = self.process.wait()
        return self.status
    
    def poll(self) -> int:
        '''
        Polls process for status.

        Note: If process is not complete (yet), it returns `None`.
        '''
        if self.status is None:
            self.status = self.process.poll()
        return self.status
    
    def terminate(self, SIGKILL:bool=False):
        '''
        Requests process termination, and waits for it to complete.

        Note: This allows for graceful termination.
        '''
        if self.status is None:
            handler = self.process.kill if SIGKILL else self.process.terminate
            handler()
            self.process.wait()

    def STDOUT(self) -> str:
        if self.stdout is None:
            self.stdout = ''.join(self.STDOUT_lines)
            self.STDOUT_lines = None
        return self.stdout
    
    def STDERR(self) -> str:
        if self.stderr is None:
            self.stderr = ''.join(self.STDERR_lines)
            self.STDERR_lines = None
        return self.stderr
