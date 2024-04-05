try:
    from sage_lib.partition.PartitionManager import PartitionManager
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing PartitionManager: {str(e)}\n")
    del sys

try:
    import numpy as np
except ImportError as e:
    import sys
    sys.stderr.write(f"An error occurred while importing numpy: {str(e)}\n")
    del sys

class PositionEditor_builder(PartitionManager):
    def __init__(self, file_location:str=None, name:str=None, **kwargs):
        super().__init__(name=name, file_location=file_location)
        
    def handleRattle(self, values, file_location=None):
        containers = []

        for container_index, container in enumerate(self.containers):
            for n in range(values['N']):
                container_copy = self.copy_and_update_container(container, f'/rattle/{container_index}_{n}', file_location)
                container_copy.AtomPositionManager.rattle(stdev=values['std'], seed=n)

                containers.append(container_copy)
        
        self.containers = containers 

        return containers

    def handleCompress(self, container, values, container_index, file_location=None):
        sub_directories, containers = [], []

        compress_vector = self.interpolate_vectors(values['compress_min'], values['compress_max'], values['N'])

        for v_i, v in enumerate(compress_vector): 
            container_copy = self.copy_and_update_container(container, f'/compress/{v_i}', file_location)
            container_copy.AtomPositionManager.compress(compress_factor=v, verbose=False)
                
            sub_directories.append(f'/{v_i}')
            containers.append(container_copy)
    
        return containers

    def handleWidening(self, values, file_location=None):
        sub_directories, containers = [], []

        for v_i, v in enumerate(values): 
            container_init = self.containers[ v['init_index'] ]
            container_mid  = self.containers[ v['mid_index'] ]
            container_end  = self.containers[ v['end_index'] ]
            
            container_copy = self.copy_and_update_container(container_init, f'/widening/{v_i}', file_location)

            for n in range(v['N']):
                container_copy.AtomPositionManager.stack(AtomPositionManager=container_mid.AtomPositionManager, direction=v['direction'] )
            container_copy.AtomPositionManager.stack(AtomPositionManager=container_end.AtomPositionManager, direction=v['direction'] )

            sub_directories.append(f'/{v_i}')
            containers.append(container_copy)
    
        return containers

    def handleInterpolation(self, values, file_location=None):
        '''
        '''
        interpolation_data = np.zeros((self.containers[0].AtomPositionManager.atomCount, 3, len(self.containers) ), dtype=np.float64)

        for container_index, container in enumerate(self.containers):
            if values.get('first_neighbor', False): container.AtomPositionManager.wrap()
            interpolation_data[:,:,container_index] = container.AtomPositionManager.atomPositions_fractional

        if values.get('first_neighbor', False):
            diff = np.diff(interpolation_data, axis=2)
            interpolation_data[:,:,1:][diff > 0.5] -= 1
            interpolation_data[:,:,1:][diff < -0.5] += 1

        new_interpolated_data = self.interpolate_with_splines(interpolation_data, M=values['images'], degree=values['degree'])

        containers = [ self.copy_and_update_container(self.containers[0], f'/interpolation/init', file_location) ]
        for container_index, container in enumerate(self.containers[1:]):
            for n in range(values['images']+1):
                container_copy = self.copy_and_update_container(container, f'/interpolation/{container_index}_{n}', file_location)
                container_copy.AtomPositionManager.set_atomPositions_fractional( new_interpolated_data[:,:,container_index*(values['images']+1) + n + 1] ) 
                if values.get('first_neighbor', False): container_copy.AtomPositionManager.wrap()
                containers.append( container_copy )
        self.containers = containers

        return containers