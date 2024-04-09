import numpy as np
from gymnasium import Env
from gymnasium import spaces

from jsspetri.envs.mono.petri_simulator import JSSPSimulator
from jsspetri.render.solution_plot import plot_solution


class JsspetriEnv(Env):
    """
    Custom Gym environment for Job Shop Scheduling using a Petri net simulator.
    """
    metadata = {"render_modes": ["solution"]}

    def __init__(self, 
                 instance_id :str ,
                 render_mode: bool =None,
                 observation_depth:int =1, 
                 dynamic: bool=False,
                 standby:bool=False,
                 ):
        """
        
        Initializes the JsspetriEnv.
        if the JSSP is flexible a maximum number of machines and jobs if predefined regardless le instance size 

        Parameters:
            render_mode (str): Rendering mode ("human" or "solution").
            instance_id (str): Identifier for the JSSP instance.
            observation_depth (int): Depth of observations in future.
        """
        
        
        self.dynamic=dynamic
        self.instance_id=instance_id

        self.sim = JSSPSimulator(self.instance_id,dynamic=self.dynamic,standby=standby)
        self.observation_depth = min(observation_depth, self.sim.n_machines)
   
         
        observation_size= 3 * self.sim.n_machines + 2 * (self.sim.n_jobs * self.observation_depth)  
        self.observation_space= spaces.Box(low=-1, high=self.sim.max_bound,shape=(observation_size,),dtype=np.int64)
        self.action_space = spaces.Discrete(len (self.sim.action_map))   
      
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode


    def _get_obs(self):

        """
        Get the observation of the state.

        Returns:
            np.ndarray: Observation array.
        """
        observation = []
        # Get the state of the machines, i.e., remaining time :
        for m in range(self.sim.n_machines) :
           if len (self.sim.machines[m].token_container) == 0:
               observation.extend([self.sim.machines[m].color,0])
           else:
               in_process=self.sim.machines[m].token_container[0]
               remaining_time =in_process.process_time - in_process.logging[list(in_process.logging.keys())[-1]][2]
               observation.extend([self.sim.machines[m].color, remaining_time if remaining_time  >=0  else 0])
               
        # Get the waiting operation in the jobs depending on the depth:
        for level in range(self.observation_depth):
           for j in range(self.sim.n_jobs) :
               if self.sim.jobs[j].token_container and level < len(self.sim.jobs[j].token_container):
                   observation.extend([self.sim.jobs[j].token_container[level].color[1], self.sim.jobs[j].token_container[level].process_time])
               else:
                   observation.extend([0, 0])
                                
        # Get the number of deliverd operation 
        for delivery in self.sim.delivery:
           observation.append(len ( delivery.token_container))
                  
        # if dynamic fill the rest of the observation with -1   
        if self.dynamic :
            for  i in range(len(observation),self.observation_space.shape[0]):  
               observation.append(-1)
               
        return np.array(observation, dtype=np.int64)

    def reset(self, seed=None, options=None):
        """
        Reset the environment.
        Returns:
            tuple: Initial observation and info.
        """
        self.sim.petri_reset()
        observation = self._get_obs()
        info = self._get_info(0,False,False)

        return observation, info

    def reward(self,action):
        """
        Calculate the reward.
        Parameters:
            advantage: Advantage given by the interaction.
        Returns:
            Any: Calculated reward .
        """
  
        if action == list (self.sim.action_map.keys())[-1] and self.sim.standby:
            return -0.1
        else :
            return self.sim.utilization_reward()

    def action_masks(self):
        """
        Get the action masks.
        Returns:
            list: List of enabled actions.
        """ 
        enabled_mask = self.sim.enabled_allocations()
        return enabled_mask
    
    def step(self, action):
        """
        Take a step in the environment.
        Parameters:
            action: Action to be performed.
        Returns:
            tuple: New observation, reward, termination status, info.
        """
        

        fired = self.sim.interact(action)  
        reward = self.reward(action)
        observation = self._get_obs()
        terminated= self.sim.is_terminal()
        info = self._get_info(reward,fired,terminated)
        
        return observation, reward, terminated, False, info

    def render(self,rank=False,format_="png",dpi=300):
        """
        Render the environment.
        """
        if self.render_mode == "solution":
            plot_solution(self.sim,show_rank=rank,format_=format_,dpi=dpi)
       

    def close(self):
        """
        Close the environment.
        """

    def _get_info(self, reward,fired, terminated):
        """
        Get information dictionary.
        """
        return {"Reward": reward,"Fired":fired ,"Terminated": terminated}

if __name__ == "__main__":
    
    env=JsspetriEnv("ta01",dynamic=False)
    
    print(env.action_space)
    print(env.sim.action_map)
    
  
    
    

    
   
