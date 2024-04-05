import json
import subprocess
import os
from superide import __container_engine__, exception

class Toolchain:
    check_image_flag = False

    def __init__(self, image_name, project_directory):
        check_container_engine_availability()
        self.image_name = image_name
        self.project_directory = project_directory
        self.contain_project_directory = "/app/project"
        self.check_image()
        
        
    def check_image(self):
        if(Toolchain.check_image_flag):
            return
        try:
            print('check image...')
            if(__container_engine__ == 'docker'):
                output = subprocess.check_output(["docker", "images", "-q", self.image_name])
                if output:
                    Toolchain.check_image_flag = True
                    return
            subprocess.run([__container_engine__, 'pull', self.image_name], stderr=subprocess.DEVNULL)
            Toolchain.check_image_flag = True
        except subprocess.CalledProcessError:
            raise exception.ImageNotGet()

    def init_project(self):
        # 文件夹非空则不能创建项目
        if(len(os.listdir(self.project_directory)) != 0):
            print("can't init project in Non empty folder")
            raise exception.InitProjectError()
        
        source_path = '/app/ExampleProject/.'
        destination_path = self.contain_project_directory
        try:
            command = [__container_engine__, "run","-it","--rm", "-v", self.project_directory+":"+self.contain_project_directory, self.image_name, 
                       'cp', '-r', source_path, destination_path];
            subprocess.run(command)
        except Exception:
            print("init project failed")
            raise exception.InitProjectError()

    def _get_tools(self):
        with open(f'{self.project_directory}/.vscode/tasks.json') as file:
            config = json.load(file)
        for task in config['tasks']:
            if task['label'] == 'Build':
                self.build_task = task
            if task['label'] == 'Check':
                self.check_task = task
            if task['label'] == 'Run':
                self.run_task = task

    def build(self):
        self._get_tools()
        build_command = self.build_task["command"]+ " " + " ".join(self.build_task["args"])
        return self.container_command(build_command)

    def check(self):
        self._get_tools()
        check_command = self.check_task["command"]+ " " + " ".join(self.check_task["args"])
        return self.container_command(check_command)
    
    def run(self):
        self._get_tools()
        run_command = self.run_task["command"]+ " " + " ".join(self.run_task["args"])
        return self.container_command(run_command)

    def container_command(self, command):
        return " ".join([__container_engine__, "run","-it","--rm", "-v", self.project_directory+":"+self.contain_project_directory, self.image_name, command])
    

def get_container_engine_path():
    try:
        path = subprocess.check_output(['which', __container_engine__]).decode().strip()
        return path
    except subprocess.CalledProcessError:
        return None

def check_container_engine_availability():
    path = get_container_engine_path()
    if path:
        try:
            subprocess.run([path, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            raise exception.ContainerEngineNotFound()
    else:
        raise exception.ContainerEngineNotFound()