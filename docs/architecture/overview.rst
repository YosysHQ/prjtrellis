.. _architecture_overview-label:

Overview
========

The ECP5 FPGA is arranged internally as a grid of :doc:`Tiles <tiles>`. Each tile contains bits that configure routing
and/or the tile's functionality.

Inside the ECP5 there is both :doc:`general routing <general_routing>`, which connects nearby tiles together
(spanning up to 12 tiles) and :doc:`global routing <global_routing>`, which allows high fanout signals to connect to all
tiles within a :term:`quadrant` (such as clocks).
