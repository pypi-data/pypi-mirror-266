#!/usr/bin/python3

import pytest
from emmi.api import exports

def test_FindAccess():

    class Foo:

        def __init__(self):
            self.moo = True
        
        def func(self):
            return True

        bar = True

        def __call__(self):
            return True

        @property
        def prop(self):
            return True

    foo = Foo()

    assert type(exports.FindAccess(Foo, "bar")) == tuple
    assert getattr(*(exports.FindAccess(Foo, "bar")))

    assert type(exports.FindAccess(Foo, "prop")) == tuple
    assert getattr(*(exports.FindAccess(Foo, "prop")))    

    with pytest.raises(AttributeError):
        assert type(exports.FindAccess(Foo, "moo")) == tuple
        
    assert hasattr(exports.FindAccess(Foo, "func"), "__call__")
    
    assert type(exports.FindAccess(foo, "moo")) == tuple
    assert getattr(*(exports.FindAccess(foo, "moo")))

    assert type(exports.FindAccess(foo, "prop")) == tuple
    assert getattr(*(exports.FindAccess(foo, "prop")))    

    assert type(exports.FindAccess(foo, "bar")) == tuple
    assert getattr(*(exports.FindAccess(foo, "bar")))
    
    assert hasattr(exports.FindAccess(foo, "func"), "__call__")
    assert exports.FindAccess(foo, "func")()



# MappingValidator
def test_MappingValidator():
    
    foo_values={"ON": 1, True: 1, 1: 1,
                "OFF": 0, False: 0, 0: 0}
    
    foo_MappingValidator = exports.MappingValidator(foo_values)
    
    # Test mapping 
    assert foo_MappingValidator["ON"] == 1
    assert foo_MappingValidator["OFF"] == 0
    assert foo_MappingValidator[True] == 1
    assert foo_MappingValidator[False] == 0
    
    # Test mapping error
    with pytest.raises(AssertionError):
        assert foo_MappingValidator["OFF"] == 1

    with pytest.raises(AssertionError):
        assert foo_MappingValidator[False] == 1
    
    with pytest.raises(ValueError):   
        assert foo_MappingValidator["foo"] == 0
        
    with pytest.raises(ValueError, match=": invalid value"): 
        assert foo_MappingValidator["foo"] == 0
    
        
# SetValidator
def test_SetValidator():
    
    foo_values=['foo', 'bar', '1', 0]
    
    foo_SetValidator = exports.SetValidator(values=foo_values)
    
    # Test mapping 
    assert foo_SetValidator['foo'] == 'foo'
    assert foo_SetValidator['bar'] == 'bar'
    assert foo_SetValidator['1'] == '1'
    assert foo_SetValidator[0] == 0
    
    with pytest.raises(ValueError):    
        assert foo_SetValidator['Foo'] == 'Foo'
        
    with pytest.raises(ValueError):    
        assert foo_SetValidator['Foo'] == 'foo'
        
                      
# BoundaryValidator
def test_BoundaryValidator():
    
    foo_limits=[-1, 1]
    foo_inclusiveTT=[True, True]
    foo_inclusiveFT=[False, True]
    foo_inclusiveTF=[True, False]
    foo_inclusiveFF=[False, False]
    
    
    #TT
    foo_BoundaryValidatorTT = exports.BoundaryValidator(limits=foo_limits, inclusive=foo_inclusiveTT, invert=False)
    
    assert foo_BoundaryValidatorTT[-1] == -1
    assert foo_BoundaryValidatorTT[-0.9] == -0.9
    assert foo_BoundaryValidatorTT[1] == 1
    
    with pytest.raises(ValueError):
        assert foo_BoundaryValidatorTT[-1.1] == -1.1
        assert foo_BoundaryValidatorTT[1.1] == 1.1
    
    
    #FT    
    foo_BoundaryValidatorFT = exports.BoundaryValidator(limits=foo_limits, inclusive=foo_inclusiveFT, invert=False)
    
    assert foo_BoundaryValidatorFT[-0.9] == -0.9
    assert foo_BoundaryValidatorFT[1] == 1
    
    with pytest.raises(ValueError):
        assert foo_BoundaryValidatorFT[-1] == -1
        assert foo_BoundaryValidatorFT[1.1] == 1.1
        
        
    #TF    
    foo_BoundaryValidatorTF = exports.BoundaryValidator(limits=foo_limits, inclusive=foo_inclusiveTF, invert=False)
    
    assert foo_BoundaryValidatorTF[-1] == -1
    assert foo_BoundaryValidatorTF[0.9] == 0.9
    
    with pytest.raises(ValueError):
        assert foo_BoundaryValidatorTF[1] == 1
        assert foo_BoundaryValidatorTF[-1.1] == -1.1
        
        
    #FF    
    foo_BoundaryValidatorFF = exports.BoundaryValidator(limits=foo_limits, inclusive=foo_inclusiveFF, invert=False)
    
    assert foo_BoundaryValidatorFF[-0.9] == -0.9
    assert foo_BoundaryValidatorFF[0.9] == 0.9
    
    with pytest.raises(ValueError):
        assert foo_BoundaryValidatorFF[1] == 1
        assert foo_BoundaryValidatorFF[-1] == -1   
        
                
# SliceValidator            
def test_SliceValidator():
    
    foo = ('foofoofoofoofoofoo')
    
    foo_SliceValidator = exports.SliceValidator(start=3, stop=6, step=1)
    assert foo_SliceValidator[foo] == 'foo'
    
    foo_SliceValidator2 = exports.SliceValidator(start=2, stop=8, step=2)
    assert foo_SliceValidator2[foo] == 'oof'
    
    foo_SliceValidator30 = exports.SliceValidator(start=0, stop=30, step=3)
    assert foo_SliceValidator30[foo] == 'ffffff'
    
    
# IdentityValidator
def test_IdentityValidator():
    foo = 2
    bar = 'bar'
    moo = True

    foo_identityValidator = exports.IdentityValidator()
    assert foo_identityValidator[foo] == 2
    assert foo_identityValidator[bar] == 'bar'
    assert foo_identityValidator[moo] == True
    
    
# PropertySetter
# This is difficult - NOT finished!
def test_PropertySetter():
    
    foo_PropertySetter = exports.PropertySetter(name='FOO', setter='foo')

    assert foo_PropertySetter.setter == 'foo'   