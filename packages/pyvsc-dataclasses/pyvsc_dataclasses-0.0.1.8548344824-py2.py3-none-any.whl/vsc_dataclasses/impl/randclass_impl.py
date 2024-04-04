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
# Created on Apr 6, 2022
#
# @author: mballance
#****************************************************************************

import logging
import typeworks
from .composite_val_closure import CompositeValClosure
from .ctor import Ctor
from .context import SolveFlags
from .rand_state import RandState
from .field_scalar_impl import FieldScalarImpl
from .modelinfo import ModelInfo
from .typeinfo_randclass import TypeInfoRandClass
from .context import TypeExprFieldRefKind

from .ctor import Ctor
from .expr import Expr


class RandClassImpl(object):
    """Implementation methods for @randclass-decorated classes"""

    @staticmethod
    def init(self, *args, **kwargs):
        self._logger = logging.getLogger(type(self).__name__)
        randclass_ti = TypeInfoRandClass.get(typeworks.TypeInfo.get(type(self)))
        randclass_ti.init(self, args, kwargs)
        

        pass
    
    @staticmethod
    def __setattr__(self, name, v):
        ctor = Ctor.inst()
        if ctor.raw_mode():
            object.__setattr__(self, name, v)
        else:
            try:
                fo = object.__getattribute__(self, name)
            except:
                object.__setattr__(self, name, v)
            else:
                if hasattr(fo, "set_val"):
                    fo.set_val(self._modelinfo, v)
                else:
                    object.__setattr__(self, name, v)

    @staticmethod
    def __getattribute__(self, name):
        ctor = Ctor.inst()
        ret = object.__getattribute__(self, name)

        if not ctor.raw_mode() and not name.startswith("__"):
            ctor.push_raw_mode()
            if ctor.expr_mode() or ctor.is_type_mode():
                # TODO: should transform into an expression proxy
                # TODO: must handle type mode
                pass
            elif hasattr(ret, "get_val"):
                # Value mode. 
                # The target is a vsc field. Calling get_val() either
                # returns the field value (ie if the field is a scalar),
                # or returns a closure that can be further queried
                # if the field is a composite
                ret = ret.get_val(self._modelinfo)
            ctor.pop_raw_mode()
        return ret

    @staticmethod
    def get_val(self, modelinfo_p : ModelInfo):
        # Obtain the appropriate field-info from the parent
        print("RandClass::get_val")
        return CompositeValClosure(
            self,
            modelinfo_p._subfield_modelinfo[self._modelinfo._idx]
        )
    
    @staticmethod
    def randomize(self, debug=0, lint=0, solve_fail_debug=0):
        modelinfo : ModelInfo = self._modelinfo
        ctxt = Ctor.inst().ctxt()

        if self._randstate is None:
            self._randstate = RandState.mk()

        modelinfo.pre_randomize()
        
        solver = ctxt.mkCompoundSolver()
        
        if debug > 0:
            pass

        solver.solve(
            self._randstate,
            [self._model],
            [],
            SolveFlags.Randomize+SolveFlags.RandomizeDeclRand+SolveFlags.RandomizeTopFields
            )
        
        modelinfo.post_randomize()
        if debug > 0:
            pass

    class RandomizeWithClosure(object):
        
        def __init__(self, obj):
            self._obj = obj
        
        def __enter__(self):
            return self._obj
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    @classmethod                
    def randomize_with(cls, self):
        return cls.RandomizeWithClosure(self)
        pass
    
    @staticmethod    
    def createPrimField(lib_field, name, idx, is_signed):
        typeinfo = None
        ctor = Ctor.inst()
        print("__createPrimField %s" % name, flush=True)

        field = FieldScalarImpl(name, typeinfo, lib_field, is_signed)
        field._modelinfo._idx = idx
        
        
        print("  field=%s" % str(lib_field))
        
#        ret = field_scalar_impl()
#        ret = t.createField(name, is_rand, iv)
#        print("__create: %d" % is_rand)
        return field

    @staticmethod 
    def _to_expr(self):
        ctor = Ctor.inst()

        if ctor.is_type_mode():
            self._logger.debug("FieldScalarImpl._to_expr (%s)" % self._modelinfo.name)
            mi = self._modelinfo
            self._logger.debug("is_topdown_scope: %d" % mi._is_topdown_scope)
            offset_l = []

            # Walk up the stack until we find the root
            last_parent = None
            while mi._parent is not None:
                last_parent = mi._parent
                self._logger.debug("  IDX: %d" % mi._idx)
                offset_l.insert(0, mi._idx)
                self._logger.debug("MI: %s" % str(mi))
                mi = mi._parent

            print("Last Parent: %s" % str(last_parent))

            bottom_up_offset = -1
            for ii,s in enumerate(ctor.bottom_up_scopes()[::-1]):
                if s is last_parent:
                    bottom_up_offset = ii
                    break
            
            print("bottom_up_offset: %d" % bottom_up_offset)
            offset = 0
            kind = TypeExprFieldRefKind.TopDownScope

            if bottom_up_offset != -1:
                offset = bottom_up_offset
                kind = TypeExprFieldRefKind.BottomUpScope

            ref = ctor.ctxt().mkTypeExprFieldRef(kind, offset, offset_l)
        else:        
            self._logger.debug("FieldScalarImpl._to_expr (%s)" % self.model().name())
            ref = ctor.ctxt().mkModelExprFieldRef(self.model())
        
        return Expr(ref)

    @classmethod
    def addMethods(cls, T):
        T.__init__ = cls.init
        T.randomize = cls.randomize
        T.randomize_with = cls.randomize_with
        T.__setattr__ = cls.__setattr__
        T.__getattribute__ = cls.__getattribute__
        T._to_expr = cls._to_expr
#        T.get_val = cls.get_val

        
