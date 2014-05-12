pylivewire
==========

A crappy Python implementation of intelligent scissors/livewire
Mainly based on this paper

Mortensen E N, Barrett W A. Intelligent scissors for image composition[C]//Proceedings of the 22nd annual conference on Computer graphics and interactive techniques. ACM, 1995: 191-198.

==========
It was a verification script for a C++ module.

Todo:
1. Other method to replace min()
2. Other method(lookup table) to avoid arccos in gradient direction calculation, or don't use arccos based method at all
3. Rewrite get_neighbors()
4. Data structure with linear search time to replace the dict for path matrix, and other if needed
5. Use numpy more carefully
6. Path cooling
7. Dynamic training
