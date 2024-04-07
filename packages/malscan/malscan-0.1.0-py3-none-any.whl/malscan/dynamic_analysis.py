import frida
import sys


def on_message(message, data):
    """
    Callback function to handle messages sent from the Frida script.

    Parameters
    ----------
    message : dict
        The message received from the Frida script.
    data : bytes
        The data received with the message.
    """
    if message['type'] == 'send':
        print("[*] {0}".format(message['payload']))


class DynamicAnalyser:
    """
    A class used to perform dynamic analysis on a process by attaching to it and intercepting function calls.

    Attributes
    ----------
    process_name : str
        The name of the process to attach to.
    function_name : str
        The name of the function to trace.
    session : frida.core.Session
        The Frida session used to attach to the process and inject the JavaScript script.

    Methods ------- analyse_api_calls() Attach to the specified process and trace the specified function.
    The function uses Frida to attach to the process and inject a JavaScript script that traces the function.
    """

    def __init__(self, process_name, function_name):
        """
            Initialize the DynamicAnalyser class.

            Parameters
            ----------
            process_name : str
                The name of the process to attach to.
            function_name : str
                The name of the function to trace.
            """
        self.process_name = process_name
        self.function_name = function_name
        self.session = None

    def analyse_api_calls(self, script_code):
        """
        Attach to the specified process and trace the specified function.

        Parameters
        ----------
        script_code : str
            The JavaScript code to be injected into the process for tracing the function.

        The function uses Frida to attach to the process and inject the provided JavaScript script that traces the function.
        """
        try:
            self.session = frida.attach(self.process_name)
            print("[*] Attached to process: {}".format(self.process_name))

            script = self.session.create_script(script_code)
            script.on('message', on_message)
            script.load()
            print("[*] Frida script loaded successfully.")
            sys.stdin.read()
        except frida.ProcessNotFoundError:
            print("[!] Process with name '{}' not found.".format(self.process_name))
        except Exception as e:
            print("[!] An error occurred:", str(e))
        finally:
            if self.session:
                self.session.detach()
