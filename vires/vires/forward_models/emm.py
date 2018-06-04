#-------------------------------------------------------------------------------
#
# EMM 2010 magnetic model
#
# Project: VirES
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
#-------------------------------------------------------------------------------
# Copyright (C) 2014 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-------------------------------------------------------------------------------

from eoxmagmod import load_model_emm
from eoxmagmod.data import EMM_2010_STATIC, EMM_2010_SECVAR
from vires.forward_models.base import BaseForwardModel
from vires.util import cached_property


class EMM2010ForwardModel(BaseForwardModel):
    """ Forward model calculator for the EMM2010.
    """
    identifier = "EMM2010"

    @cached_property
    def model(self):
        return load_model_emm(EMM_2010_STATIC, EMM_2010_SECVAR)


class EMMForwardModel(EMM2010ForwardModel):
    """ Forward model calculator for the EMM.
    """
    identifier = "EMM"
