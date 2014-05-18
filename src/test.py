import cv2
from livewire import Livewire

def test():   
    seed = 1, 1
    image = cv2.imread('..\Lena.png')
    lw = Livewire(image)
    path_matrix = lw.get_path_matrix(seed)
