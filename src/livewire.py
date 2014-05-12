"""
A crappy implementation of intelligent scissors/livewire algorithm
"""

from __future__ import division
import cv2
import numpy as np

SQRT_0_5 = 0.70710678118654757

class Livewire():
    """
    A simple livewire implementation for verification using 
        1. Canny edge detector + gradient magnitude + gradient direction
        2. Dijkstra algorithm
    """
    
    def __init__(self, image):
        self.image = image
        self.x_lim = image.shape[0]
        self.y_lim = image.shape[1]
        # The values in cost matrix ranges from 0~1
        self.cost_edges = 1 - cv2.Canny(image, 85, 170)/255.0
        self.grad_x, self.grad_y, self.grad_mag = self._get_grad(image)
        self.cost_grad_mag = 1 - self.grad_mag/np.max(self.grad_mag)
        # Weight for (Canny edges, gradient magnitude, gradient direction)
        self.weight = (0.425, 0.425, 0.15)
        
        self.n_pixs = self.x_lim * self.y_lim
        self.n_processed = 0
    
    @classmethod
    def _get_grad(cls, image):
        """
        Return the gradient magnitude of the image using Sobel operator
        """
        rgb = True if len(image.shape) > 2 else False
        grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
        if rgb:
            # A very rough approximation for quick verification...
            grad_x = np.max(grad_x, axis=2)
            grad_y = np.max(grad_y, axis=2)
            
        grad_mag = np.sqrt(grad_x**2+grad_y**2)
        grad_x /= grad_mag
        grad_y /= grad_mag
        
        return grad_x, grad_y, grad_mag
    
    def _get_neighbors(self, p):
        """
        Return 8 neighbors around the pixel p
        """
        x, y = p
        x0 = 0 if x == 0 else x - 1
        x1 = self.x_lim if x == self.x_lim - 1 else x + 2
        y0 = 0 if y == 0 else y - 1
        y1 = self.y_lim if y == self.y_lim - 1 else y + 2
        
        return [(x, y) for x in xrange(x0, x1) for y in xrange(y0, y1) if (x, y) != p]
    
    def _get_grad_direction_cost(self, p, q):
        """
        Calculate the gradient changes refer to the link direction
        """
        dp = (self.grad_y[p[0]][p[1]], -self.grad_x[p[0]][p[1]])
        dq = (self.grad_y[q[0]][q[1]], -self.grad_x[q[0]][q[1]])
        
        l = np.array([q[0]-p[0], q[1]-p[1]], np.float)
        if 0 not in l:
            l *= SQRT_0_5
        
        dp_l = np.dot(dp, l)
        l_dq = np.dot(l, dq)
        if dp_l < 0:
            dp_l = -dp_l
            l_dq = -l_dq
        
        # 2/3pi * ...
        return 0.212206590789 * (np.arccos(dp_l)+np.arccos(l_dq))
    
    def _local_cost(self, p, q):
        """
        1. Calculate the Canny edges & gradient magnitude cost taking into account Euclidean distance
        2. Combine with gradient direction
        Assumption: p & q are neighbors
        """
        diagnol = q[0] == p[0] or q[1] == p[1]
        
        # c0, c1 and c2 are costs from Canny operator, gradient magnitude and gradient direction respectively
        if diagnol:
            c0 = self.cost_edges[p[0]][p[1]]-SQRT_0_5*(self.cost_edges[p[0]][p[1]]-self.cost_edges[q[0]][q[1]])
            c1 = self.cost_grad_mag[p[0]][p[1]]-SQRT_0_5*(self.cost_grad_mag[p[0]][p[1]]-self.cost_grad_mag[q[0]][q[1]])
            c2 = SQRT_0_5 * self._get_grad_direction_cost(p, q)
        else:
            c0 = self.cost_edges[q[0]][q[1]]
            c1 = self.cost_grad_mag[q[0]][q[1]]
            c2 = self._get_grad_direction_cost(p, q)
        
        if np.isnan(c2):
            c2 = 0.0
        
        w0, w1, w2 = self.weight
        cost_pq = w0*c0 + w1*c1 + w2*c2
        
        return cost_pq * cost_pq

    def get_path_matrix(self, seed):
        """
        Get the back tracking matrix of the whole image from the cost matrix
        """
        neighbors = []          # 8 neighbors of the pixel being processed
        processed = set()       # Processed point
        cost = {seed: 0.0}      # Accumulated cost, initialized with seed to itself
        paths = {}

        self.n_processed = 0
        
        while cost:
            # Expand the minimum cost point
            p = min(cost, key=cost.get)
            neighbors = self._get_neighbors(p)
            processed.add(p)

            # Record accumulated costs and back tracking point for newly expanded points
            for q in [x for x in neighbors if x not in processed]:
                temp_cost = cost[p] + self._local_cost(p, q)
                if q in cost:
                    if temp_cost < cost[q]:
                        cost.pop(q)
                else:
                    cost[q] = temp_cost
                    processed.add(q)
                    paths[q] = p
            
            # Pop traversed points
            cost.pop(p)
            
            self.n_processed += 1
        
        return paths
