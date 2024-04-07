import json
import os
import shutil

from .sq_sim_data_gen_ctx import SQSimDataGenCtx
from jinja2 import FileSystemLoader, Environment
from .sq_code_gen_model import SQCodeGenModel

_default_json_file = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config'), "input.json")


class SQSimSetupGen:
    def __init__(self, json_file: str = _default_json_file):
        with open(json_file, 'r') as file:
            self.data = json.load(file)
        self.gen_ctx = SQSimDataGenCtx()
        self.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        file_loader = FileSystemLoader(self.template_folder)
        self.env = Environment(loader=file_loader, trim_blocks=True, lstrip_blocks=True)

    def generate(self, output_folder: str):
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder)
        simulators = self.data['Simulators']
        for simulator in simulators:
            data = self.gen_ctx.generate(simulator)
            code_data_model = SQCodeGenModel(data)
            template = self.env.get_template('sim_setup.py.j2')
            output = template.render(model=code_data_model)
            self.create_file(data=output, output_folder=output_folder, file=f'{simulator["name"].lower()}_setup.py')
        print("Done")

    @staticmethod
    def create_file(data, output_folder, file):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        file_name = os.path.join(output_folder, file)
        f = open(file_name, "w")
        f.write(data)
        f.write('\n')
        f.close()
