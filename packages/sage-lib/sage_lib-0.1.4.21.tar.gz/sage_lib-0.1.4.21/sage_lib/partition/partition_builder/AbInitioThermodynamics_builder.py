try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del syss

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

try:
    import copy
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing copy: {str(e)}\n")
    del sys

try:
    import os
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing os: {str(e)}\n")
    del sys
    
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing matplotlib.pyplot: {str(e)}\n")
    del sys
    
try:
    import seaborn as sns
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while seaborn: {str(e)}\n")
    del sys


class AbInitioThermodynamics_builder(PartitionManager):
    """

    """

    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        """

        """
        super().__init__(name=name, file_location=file_location)
        self.uniqueAtomLabels = None
        self.composition_data = None
        self.energy_data = None 
        self.area_data = None

    def get_composition_data(self, ) -> dict:
        # 
        
        self.uniqueAtomLabels = set()
        for c_i, c in enumerate(self.containers):   
            self.uniqueAtomLabels.update( c.AtomPositionManager.uniqueAtomLabels )

        self.uniqueAtomLabels = list(self.uniqueAtomLabels)
        self.uniqueAtomLabels_order = { n:i for i, n in enumerate(self.uniqueAtomLabels) }

        composition_data, energy_data, area_data = np.zeros((len(self.containers), len(self.uniqueAtomLabels)), dtype=np.float64), np.zeros(len(self.containers), dtype=np.float64), np.zeros(len(self.containers), dtype=np.float64)
        for c_i, c in enumerate(self.containers):  
            comp = np.zeros_like( self.uniqueAtomLabels, dtype=np.int64 )
            for ual, ac in zip(c.AtomPositionManager.uniqueAtomLabels, c.AtomPositionManager.atomCountByType):
                comp[ self.uniqueAtomLabels_order[ual] ] = ac 

            composition_data[c_i,:] = comp
            energy_data[c_i] = c.AtomPositionManager.E
            area_data[c_i] = c.AtomPositionManager.get_area('z')

        self.composition_data, self.energy_data, self.area_data = composition_data, energy_data, area_data

        return {'composition_data': composition_data, 'energy_data':energy_data, 'area_data':area_data}

    def get_diagram_data(self, ID_reference:list, composition_data:np.array, energy_data:np.array, area_data:np.array, especie:str) -> np.array:
        composition_reference = composition_data[ID_reference, :] 
        energy_reference = energy_data[ID_reference] 
        self.uniqueAtomLabels_order

        for cr_i, cr in enumerate(composition_reference): 
            if np.sum(cr) == cr[ self.uniqueAtomLabels_order[especie] ]:
                reference_mu_index = cr_i

        mask = np.ones(len(energy_data), dtype=bool)
        mask[ID_reference] = False

        composition_relevant = composition_data[mask,:]
        energy_relevant = energy_data[mask]
        area_relevant = area_data[mask]

        diagram_data = np.zeros( (energy_relevant.shape[0], 2) )
        print(energy_relevant) 
        for mu in [0, 1]:
            for i, (E, C, A) in enumerate(zip(energy_relevant, composition_relevant, area_relevant)):
                E_ref_mask = np.zeros_like(energy_reference)
                E_ref_mask[reference_mu_index] = mu

                mu_value = np.linalg.solve(composition_reference, energy_reference+E_ref_mask)
                gamma = 1/A * E * np.sum( mu_value * C ) 

                diagram_data[i, mu] = gamma

        return diagram_data

    def plot_phase_diagram(self, diagram_data:np.array, mu_max:float, mu_min:float, output_path:str=None, window_size:tuple=(10, 6), save:bool=True, verbose:bool=True):
        """
        Plot a phase diagram with extrapolated lines from given points and highlight the lower envelope.

        Parameters:
        - diagram_data (np.ndarray): An Nx2 array with each row being [y-intercept, slope] for a line.
        - output_path (str, optional): Path to save the plot image.
        - window_size (tuple, optional): Size of the plotting window.
        - save (bool, optional): Whether to save the plot to a file.
        - verbose (bool, optional): Whether to print additional information.
        """
        # Define plot limits
        pd_min, pd_max = mu_min, mu_max  # Adjust as needed

        plt.figure(figsize=window_size)

        # For each line, calculate and plot
        for index, (x, y) in enumerate(diagram_data):
            # Calculate slope (m) and y-intercept (b) for the line
            m = (y - x) / (1 - 0)  # (y2-y1)/(x2-x1)
            b = y - m * 1  # y = mx + b => b = y - mx
            
            # Generate x values from pd_min to pd_max for plotting
            x_values = np.linspace(pd_min, pd_max, 100)
            # Calculate y values based on the line equation
            y_values = m * x_values + b
            
            # Plot each line
            plt.plot(x_values, y_values, alpha=0.5, label=f'Line {index}')

        opt_estructures = []
        # TODO: Identify and plot the lower envelope
        # This requires a custom implementation based on your criteria for the lower envelope.
        
        # Customize the plot
        plt.legend()
        plt.xlabel('X Axis')
        plt.ylabel('Y Axis')
        plt.title('Phase Diagram with Lower Envelope Highlighted')

        # Show or save the plot
        if save:
            if not output_path:
                output_path = '.'  # Use current directory if not specified
            plt.savefig(f'{output_path}/phase_diagram_plot.png', dpi=100)
        else:
            plt.show()

    def handleABITAnalysis(self, values:list, file_location:str=None):
        """
        Handle molecular dynamics analysis based on specified values.

        Args:
            values (list): List of analysis types to perform.
            file_location (str, optional): File location for output data.
        """
        ABIT_data = {}

        for abit in values:
            if abit.upper() == 'PHASE_DIAGRAM':
                composition_data = self.get_composition_data()
                diagram_data = self.get_diagram_data(ID_reference=values[abit].get('reference_ID', [0]), 
                                    composition_data=composition_data['composition_data'], energy_data=composition_data['energy_data'], area_data=composition_data['area_data'], 
                                     especie=values[abit].get('especie', None)) 
                self.plot_phase_diagram(diagram_data, output_path=values[abit].get('output_path', '.'), save=True, verbose=values[abit].get('verbose', True), mu_max=values[abit].get('mu_max', [0]), mu_min=values[abit].get('mu_min', [0]))


