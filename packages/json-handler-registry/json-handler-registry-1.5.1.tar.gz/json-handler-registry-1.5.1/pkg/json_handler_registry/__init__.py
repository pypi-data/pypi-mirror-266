#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright by: P.J. Grochowski

import logging

__version_info__ = (1, 5, 1)
__version__ = '.'.join([str(i) for i in __version_info__])
__package_name__ = str(__package__).replace('_', '-')

__logger = logging.getLogger(__package__)
