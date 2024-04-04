#****************************************************************************
# Copyright 2019-2022 Matthew Ballance and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created on Jun 28, 2022
#
# @author: mballance
#****************************************************************************
from .list_t import ListT


class RandListT(object):
    
    def __new__(cls, t=None, sz=0):
        if t is None:
            ret = cls.T()
        else:
            ret = ListT(t, sz)

        ret._modelinfo.set_rand()
        
        return ret