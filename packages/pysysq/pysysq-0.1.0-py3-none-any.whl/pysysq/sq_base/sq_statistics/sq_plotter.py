import matplotlib.pyplot as plt
import pandas as pd
from ..sq_logger import SQLogger


class SQPlotter:
    def __init__(self, name: str, objs: [], **kwargs):
        self.name = name
        self.objs = objs
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.show_plot = kwargs.get('show_plot', False)
        self.output_file = kwargs.get('output_file', 'Statistics.png')

    def plot(self):
        plt.figure()
        for obj in self.objs:
            self.logger.debug(f'Plotting {obj.name}')
            properties = obj.read_statistics().get_all_property_names(obj.name)
            for property_name in properties:
                self.plot_property(property_name=property_name, obj=obj)
        plt.legend()
        plt.xlabel('Simulation Time')
        plt.ylabel('Property Value')
        plt.title(f'SQObject Properties')
        plt.savefig(self.output_file)
        if self.show_plot:
            plt.show()

    def generate_excel(self, filename):

        # Create a pandas ExcelWriter object
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')

        for obj in self.objs:
            properties = obj.read_statistics().get_all_property_names(obj.name)
            for property_name in properties:
                property_values = obj.read_statistics().get_property(name=property_name, owner=obj.name)
                x_values = [entry.sim_time for entry in property_values]
                y_values = [entry.value for entry in property_values]

                # Create a DataFrame for this property
                df = pd.DataFrame({
                    'Simulation Time': x_values,
                    'Property Value': y_values
                })

                # Write the DataFrame to a worksheet named after the object and property
                df.to_excel(writer, sheet_name=f'{obj.name}_{property_name}', index=False)

        # Save the Excel file
        writer.close()

    def plot_property(self, property_name: str, obj):
        self.logger.debug(f'Plotting {obj.name} [{property_name}]')
        property_values = obj.read_statistics().get_property(name=property_name, owner=obj.name)
        x_values = [entry.sim_time for entry in property_values]
        y_values = [entry.value for entry in property_values]
        plt.plot(x_values, y_values, label=f'{obj.name}[{property_name}]')
