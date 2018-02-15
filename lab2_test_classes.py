"""lab1_test_classes.py

Champlain College CSI-235, Spring 2018
The following code was adapted by Joshua Auerbach (jauerbach@champlain.edu)
from the UC Berkeley Pacman Projects (see license and attribution below).

----------------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import test_classes

HOST = "hawk.champlain.edu" # change to "csi235.site" for off campus
ECHO_PORT = 9998
REQUEST_ID_PORT = 9999
BAD_PORT = 9000

class EvalTest(test_classes.TestCase):
    """Simple test case which evals an arbitrary piece of python code.
    
    The test is correct if the output of the code given the student's
    solution matches that of the instructor's.
    """

    def __init__(self, question, test_dict):
        super().__init__(question, test_dict)
        self.preamble = compile(test_dict.get('preamble', ""),
                                "%s.preamble" % self.get_path(), 'exec')
        self.test = compile(test_dict['test'], "%s.test" % self.get_path(),
                            'eval')
        self.success = test_dict['success']
        self.failure = test_dict['failure']

    def eval_code(self, module_dict):
        bindings = dict(module_dict)
        exec(self.preamble, bindings)
        return str(eval(self.test, bindings))

    def execute(self, grades, module_dict, solution_dict):
        result = self.eval_code(module_dict)
        if result == solution_dict['result']:
            grades.add_message('PASS: %s' % self.path)
            grades.add_message('\t%s' % self.success)
            return True
        else:
            grades.add_message('FAIL: %s' % self.path)
            grades.add_message('\t%s' % self.failure)
            grades.add_message('\tstudent result: "%s"' % result)
            grades.add_message('\tcorrect result: "%s"' %
                               solution_dict['result'])

        return False

    def write_solution(self, module_dict, file_path):
        handle = open(file_path, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write('# The result of evaluating the test must equal ')
        handle.write('the below when cast to a string.\n')

        handle.write('result: "%s"\n' % self.eval_code(module_dict))
        handle.close()
        return True


class Lab2Test(test_classes.TestCase):

    def __init__(self, question, test_dict):
        super().__init__(question, test_dict)
        self.test_cases = ['hello world', 'abcdefghijklmnop', 
                            'Beautiful is better than ugly.']

    def write_solution(self, module_dict, file_path):
        handle = open(file_path, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write('# This file is left blank intentionally.\n')
        handle.close()
        return True

    def timeout_test(self, grades, client, ex):
        grades.add_message("Testing timeout...")
        result = None
        try:
            # keep looping until timeout, the server will not respond to %
            while True:
                result = None
                result = client.send_message_by_character("%")
        except ex:
            grades.add_message('PASS: {}'.format(self.path))
            grades.add_message('\tProperly raised TimeOutError on timeout')
            return True
        else:        
            grades.add_message('FAIL: {}'.format(self.path))
            grades.add_message('\tDid not raise TimeOutError on timeout')
            return False
            
    def improper_port_test(self, grades, client, ex):
        grades.add_message("Testing incorrect port...")
        try:
            result = client.send_message_by_character(self.test_cases[0])
            
        except ex: #windows
            grades.add_message('PASS: {}'.format(self.path))
            grades.add_message('\tProperly timedout when no route to host')
            return True        
                    
        except OSError: #linux
            grades.add_message('PASS: {}'.format(self.path))
            grades.add_message('\tProperly let OSError through when no'
                                ' route to host')
            return True
        else:           
            grades.add_message('Fail: {}'.format(self.path))
            grades.add_message('\tNo OSError came through when there was '
                                'no route to host')
            return False
            
    def keep_retrying(self, grades, client, test, ex, n=10):
        for i in range(n):
            try:
                result = client.send_message_by_character(test)
            except ex:
                grades.add_message('Timed Out, Retrying')
            else:
                return result


class BasicUDPTest(Lab2Test):

    def execute(self, grades, module_dict, solution_dict):
        passing_all = True
        
        udp_client = module_dict["udp_client"]
        client = udp_client.UDPClient(HOST, BAD_PORT)
        passing_all = passing_all and self.improper_port_test(grades, client,
                         udp_client.TimeOutError)
        
        client = udp_client.UDPClient(HOST, ECHO_PORT)
        
        for test in self.test_cases:
            grades.add_message("Testing {}...".format(repr(test)))

            result = self.keep_retrying(grades, client, test, 
                                        udp_client.TimeOutError)
                    
            if not result:
                grades.add_message('FAIL: {}'.format(self.path))
                grades.add_message('\tTime out 10 times, giving up')     
                passing_all = False               
            
            elif type(result) != type(""):
                grades.add_message('FAIL: {}'.format(self.path))
                grades.add_message('\tReturn type of send_message_by_character '
                                    'must be str, but it is {}'.format(
                                    type(result)))
                passing_all = False

            elif len(result) == len(test) and result != test:
                grades.add_message('PASS: {}'.format(self.path))
                grades.add_message('\t{} properly sent, received {}'.format(
                                    repr(test), repr(result)))

            elif len(result) == len(test):
                grades.add_message('FAIL: {}'.format(self.path))
                grades.add_message(('\t{} should not have been '
                                    'received exactly').format(
                                    repr(test)))                
                passing_all = False
            else:
                grades.add_message('FAIL: {}'.format(self.path))
                grades.add_message(('\tIncorrect number of characters returned'
                                    'for {!r}.  Should have received {}, but '
                                    'received {}').format(test, len(test), 
                                        len(result)))           
                passing_all = False  
                
        passing_all = passing_all and self.timeout_test(grades, client, 
                                                        udp_client.TimeOutError)

                
        return passing_all

class RequestIDUDPTest(Lab2Test):

    def execute(self, grades, module_dict, solution_dict):
        passing_all = True
        
        udp_client = module_dict["udp_client"]
        
        client = udp_client.UDPClient(HOST, BAD_PORT)
        passing_all = passing_all and self.improper_port_test(grades, client,
                         udp_client.TimeOutError)
        
        client = udp_client.UDPClient(HOST, REQUEST_ID_PORT, True)
        
        for test in self.test_cases:
            grades.add_message("Testing {}...".format(repr(test)))        

            result = self.keep_retrying(grades, client, test, 
                                        udp_client.TimeOutError)
            
            if not result:
                grades.add_message('FAIL: {}'.format(self.path))
                grades.add_message('\tTime out 10 times, giving up')
                passing_all = False
            
            elif type(result) != type(""):
                grades.add_message('FAIL: {}'.format(self.path))
                grades.add_message('\tReturn type of send_message_by_character '
                                    'must be str, but it is {}'.format(
                                    type(result)))
                passing_all = False

            elif result == test:
                grades.add_message('PASS: {}'.format(self.path))
                grades.add_message('\t{} properly sent, received {}'.format(
                                    repr(test), repr(result)))

            else:
                grades.add_message('FAIL: {}'.format(self.path))
                grades.add_message(('\tIncorrect string returned'
                                    'for {!r}.  Should have received {!r}, but '
                                    'received {!r}').format(test, test, 
                                    result))
                passing_all = False        
                
        passing_all = passing_all and self.timeout_test(grades, client, 
                                                        udp_client.TimeOutError)                  
        return passing_all
