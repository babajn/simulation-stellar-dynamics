"""Shared quadtree and Newtonian force calculation for ex06a and ex06b."""
import numpy as np

# Body class representing a particle with position and mass
class Body:
    def __init__(self, position, mass):
        self.position = np.array(position)
        self.mass = mass

# QuadNode class representing each node in the QuadTree
class QuadNode:
    _id_counter = 0  # Class variable to assign unique IDs to nodes

    @classmethod
    def reset_id_counter(cls):
        cls._id_counter = 0
        
    def __init__(self, boundary, parent=None, max_depth=64, verbose=False):
        """
        Initializes a QuadNode.
        
        Parameters:
        - boundary: Tuple representing the node's boundaries (x_min, x_max, y_min, y_max)
        - parent: Reference to the parent QuadNode
        - max_depth: Maximum allowed depth to prevent infinite subdivisions
        """
        self.verbose = verbose
        self.id = QuadNode._id_counter
        QuadNode._id_counter += 1
        if self.verbose: print(f"QuadNode created with ID: {self.id}")  # Debugging line

        self.boundary = boundary  # Node boundary (x_min, x_max, y_min, y_max)
        self.mass = 0
        self.center_of_mass = np.zeros(2)
        self.body = None
        self.children = [None, None, None, None]  # SW, NW, SE, NE
        self.is_divided = False  # Indicates whether the node has been subdivided
        self.parent = parent  # Reference to the parent node
        self.depth = parent.depth + 1 if parent else 0  # Current depth in the tree
        self.max_depth = max_depth  # Maximum allowed depth

    def insert(self, body):
        """
        Inserts a Body into the QuadTree.
        
        Parameters:
        - body: Instance of Body to be inserted
        
        Returns:
        - True if insertion was successful, False otherwise
        """
        if not self.contains(body.position):
            return False

        # If the node is empty and not divided, place the body here
        if self.body is None and not self.is_divided:
            self.body = body
            self.mass += body.mass
            self.center_of_mass = body.position
            if self.verbose: print(f"Inserting body into node {self.id}")  # Debugging line
            return True

        # If the node already contains a body and is not divided, subdivide
        if self.body is not None and not self.is_divided:
            if self.depth >= self.max_depth:
                # Prevent infinite subdivision by not inserting additional bodies
                if self.verbose: print(f"Maximum depth reached at node {self.id}. Cannot insert body at position {body.position}.")
                return False
            self.subdivide()
            # Re-insert the existing body into the appropriate child node
            index = self.get_child_index(self.body.position)
            inserted = self.children[index].insert(self.body)
            if not inserted:
                if self.verbose: print(f"Failed to re-insert body at position {self.body.position} into child {index} of node {self.id}.")
            self.body = None  # Current node no longer holds the body
            self.is_divided = True

        # Insert the new body into the appropriate child node
        index = self.get_child_index(body.position)
        inserted = self.children[index].insert(body)
        if not inserted:
            if self.verbose: print(f"Failed to insert body at position {body.position} into child {index} of node {self.id}.")
            return False

        # Update the center of mass and mass
        self.update_center_of_mass(body)
        return True

    def get_child_index(self, position):
        """
        Determines which child node the position belongs to.
        
        Returns:
        - Index (0: SW, 1: NW, 2: SE, 3: NE)
        """
        x_min, x_max, y_min, y_max = self.boundary
        mid_x = (x_min + x_max) / 2
        mid_y = (y_min + y_max) / 2

        if position[0] < mid_x:
            if position[1] < mid_y:
                return 0  # SW
            else:
                return 1  # NW
        else:
            if position[1] < mid_y:
                return 2  # SE
            else:
                return 3  # NE

    def subdivide(self):
        """
        Subdivides the current node into four child nodes: SW, NW, SE, NE.
        """
        x_min, x_max, y_min, y_max = self.boundary
        mid_x = (x_min + x_max) / 2
        mid_y = (y_min + y_max) / 2

        # Define child node boundaries in the order SW, NW, SE, NE
        self.children[0] = QuadNode((x_min, mid_x, y_min, mid_y), parent=self, max_depth=self.max_depth, verbose=self.verbose)  # SW
        self.children[1] = QuadNode((x_min, mid_x, mid_y, y_max), parent=self, max_depth=self.max_depth, verbose=self.verbose)  # NW
        self.children[2] = QuadNode((mid_x, x_max, y_min, mid_y), parent=self, max_depth=self.max_depth, verbose=self.verbose)  # SE
        self.children[3] = QuadNode((mid_x, x_max, mid_y, y_max), parent=self, max_depth=self.max_depth, verbose=self.verbose)  # NE

    def contains(self, position):
        """
        Checks if the position is within the node's boundary.
        
        Returns:
        - True if contained, False otherwise
        """
        x_min, x_max, y_min, y_max = self.boundary
        return x_min <= position[0] <= x_max and y_min <= position[1] <= y_max

    def update_center_of_mass(self, body):
        """
        Updates the node's center of mass and total mass.
        """
        total_mass = self.mass + body.mass
        if self.mass == 0:
            self.center_of_mass = body.position
        else:
            self.center_of_mass = (self.center_of_mass * self.mass + body.position * body.mass) / total_mass
        self.mass = total_mass

# BarnesHut class managing the QuadTree
class BarnesHutCore:
    def __init__(self, boundary, max_depth=64, verbose=False, gravitational_constant=1.0):
        """
        Initializes the BarnesHut QuadTree.
        
        Parameters:
        - boundary: Tuple representing the root node's boundaries (x_min, x_max, y_min, y_max)
        - max_depth: Maximum allowed depth for the QuadTree
        """
        QuadNode._id_counter = 0  # クラス変数をリセット
        self.G = float(gravitational_constant)
        self._positions = set()
        self.root = QuadNode(boundary, max_depth=max_depth, verbose=verbose)

    def insert(self, body):
        """
        Inserts a Body into the QuadTree.
        """
        if not self.root.contains(body.position):
            raise ValueError("Particle outside root boundary")
        position = tuple(body.position)
        if position in self._positions:
            raise ValueError("Coincident particles are unsupported without softening")
        if not self.root.insert(body):
            raise ValueError("Tree insertion failed (maximum depth)")
        self._positions.add(position)

    def calculate_gravitational_force(self, body, theta=0.5):
        """
        Calculates the gravitational force on a body using the Barnes-Hut algorithm.
        
        Parameters:
        - body: Instance of Body for which to calculate the force
        - theta: Threshold parameter for approximation
        
        Returns:
        - Numpy array representing the gravitational force vector
        """
        return self._calculate_force(self.root, body, theta)

    def _calculate_force(self, node, body, theta):
        """
        Recursive helper function to calculate gravitational force.
        """
        if node.mass == 0 or (node.body is body and not node.is_divided):
            return np.zeros(2)  # No force from self

        distance = np.linalg.norm(body.position - node.center_of_mass)

        # Calculate the size of the node
        x_min, x_max, y_min, y_max = node.boundary
        node_size = max(x_max - x_min, y_max - y_min)

        if not node.is_divided or (not node.contains(body.position) and distance > 0 and node_size / distance < theta):
            # Use this node as an approximation
            force = self.calculate_force_between(body, node)
            return force
        else:
            # Subdivide and calculate force from child nodes
            force = np.zeros(2)
            for child in node.children:
                if child is not None:
                    force += self._calculate_force(child, body, theta)
            return force

    def calculate_force_between(self, body, node):
        """
        Calculates the gravitational force between a body and a node.
        """
        r = node.center_of_mass - body.position
        distance = np.linalg.norm(r)
        if distance == 0:
            return np.zeros(2)  # Avoid division by zero
        force_magnitude = self.G * body.mass * node.mass / distance**3
        force = force_magnitude * r
        return force

