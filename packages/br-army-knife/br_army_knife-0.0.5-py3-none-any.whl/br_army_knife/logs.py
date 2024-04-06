import datetime

class Log():
    # Simple log implementation
    def __init__(self, log_path:str, log_file:bool=True, log_terminal:bool=False, parallel:bool=False):
        self.log_path = log_path
        self.log_file = log_file
        self.log_path = log_terminal

    
    def log(self, msg:str):
        if self.log_terminal:
            print(msg, flush=True)
        if self.log_file:
            with open(self.log_path, 'a') as file:
                file.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}    {msg}\n')