class IdGen:
    """
    Class for generating unique IDs.
    """
    uid_counter = 0

    @classmethod
    def generate_uid(cls):     
        uid = cls.uid_counter
        cls.uid_counter += 1
        return str(uid)

class Place:
    """
    Class representing a place in a Petri net.

    Attributes:
        uid (str): Unique identifier for the place.
        label (str): Name or label of the place.
        type (str): Type or role of the place.
        parents (list): List of parent nodes (transitions).
        children (list): List of child nodes (transitions).
        token_container (list): List of tokens currently in the place.
        color: Color attribute for the place.
    """

    def __init__(self, label, role="", color=None):
        """
        Initialize a place.

        Parameters:
            label (str): Name or label of the place.
            role (str): Type or role of the place.
            color: Color attribute for the place.
        """
        self.uid = IdGen.generate_uid()
        self.label = label
        self.type = role
        self.parents = []
        self.children = []
        self.token_container = []
        self.color = color
        self.actif=False

    def add_arc(self, node, parent=True):
        """
        Add an arc (connection) between the place and a node.

        Parameters:
            node: The node to connect.
            parent (bool): True if the node is a parent (transition), False if a child.
        """
        if parent:
            self.parents.append(node)
        else:
            self.children.append(node)

    def __str__(self):
        """
        Get a string representation of the place.

        Returns:
            str: A string representing the place.
        """
        return f"Place name: {self.label}, type: {self.type}, Tokens: {len(self.token_container)}, color: {self.color}, parents: {self.parents}, children: {self.children}, id: {self.uid}"


class Transition:
    """
    Class representing a transition in a Petri net.

    Attributes:
        uid (str): Unique identifier for the transition.
        label (str): Name or label of the transition.
        type (str): Type or role of the transition.
        color: Color attribute for the transition.
        parents (list): List of parent nodes (places).
        children (list): List of child nodes (places).
        enabled (bool): Flag indicating whether the transition is enabled.
    """

    def __init__(self, label, role="", color=None):
        """
        Initialize a transition.

        Parameters:
            label (str): Name or label of the transition.
            role (str): Type or role of the transition.
            color: Color attribute for the transition.
        """
        self.uid = IdGen.generate_uid()
        self.label = label
        self.type = role
        self.color = color
        self.parents = []
        self.children = []
        self.enabled = True
        self.actif=False

    def add_arc(self, node, parent=True):
        """
        Add an arc (connection) between the transition and a node.

        Parameters:
            node: The node to connect.
            parent (bool): True if the node is a parent (place), False if a child.
        """
        if parent:
            self.parents.append(node)
        else:
            self.children.append(node)

    def __str__(self):  
        return f"Transition name: {self.label}, type: {self.type}, color: {self.color}, parents: {self.parents}, children: {self.children}, id: {self.uid}"



class Token:
    """
    Class representing a token in a Petri net.

    Attributes:
        uid (str): Unique identifier for the token.
        color (tuple): Tuple representing the color of the token (job_color, machine_color).
        features (list) : a list containing the features of the token feature [0] is reserved for processing time
        order (int): Order of  the operation in the job  .
        logging (dict): Dictionary for logging entry time, leave time, and elapsed time for each place.
    """

    def __init__(self, initial_place, color=(None, None), features=[] ,order=0):
        """
        Initialize a token.

        Parameters:
            initial_place: The initial place where the token is located.
            color (tuple): Tuple representing the color of the token (job_color, machine_color).
            process_time (int): Time taken for the token's process.
            order (int): Order of the token.
        """
        self.uid = IdGen.generate_uid()
        self.color = color
        self.process_time = features[0]
        self.features=features[1:]
        self.order = order
        self.logging = {initial_place: [0, 0, 0]}  # entry time, leave time, elapsed time
   

    def __str__(self):

        return f"id: {self.uid}, color: {self.color}, process_time: {self.process_time}, extra_features={self.features}, order: {self.order}, logging: {self.logging}"
