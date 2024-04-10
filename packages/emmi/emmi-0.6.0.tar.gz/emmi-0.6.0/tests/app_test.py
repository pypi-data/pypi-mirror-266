#!/usr/bin/python

from emmi import app

import pytest, random, string, time, asyncio

def test_cfgFromEnv():
    flat = {
        'foo_var': 'foo_var',
        'foo_car': 'foo_car',
        'foo_bar_car': 'foo_bar_car',
        'bar_car': 'bar_car'
    }

    conf = app.cfgFromFlat(flat, prefix="foo")
    
    assert len(conf) == 3
    assert len(conf['bar']) == 1
    assert conf['car'] == 'foo_car'
    assert conf['var'] == 'foo_var'


def test_cfgFromEnv_prefix():
    assert app.cfgFromFlat({"foo_bar_moo": 3}, prefix='foo')['bar']['moo'] == 3

def test_cfgFromEnv_noprefix():
    assert app.cfgFromFlat({"foo_bar_moo": 3})['foo']['bar']['moo'] == 3
    


def test_cfgUnify_simple():
    m1 = { 'foo': 1 }
    m2 = { 'bar': 2 }
    m3 = { 'moo': 3 }
    m4 = { 'foo': 4 }
    
    u1 = app.cfgUnify(m1, m2, m3)
    assert u1.get('foo') == 1
    assert u1.get('bar') == 2
    assert u1.get('moo') == 3

    u2 = app.cfgUnify(m1, m2, m3, m4)
    assert u2.get('foo') == 4
    assert u2.get('bar') == 2
    assert u2.get('moo') == 3


def test_cfgUnify_nested():
    m1 = { 'foo': { 'bar': 1 } }
    m2 = { 'foo': { 'moo': 2 } }
    m3 = { 'bar': { 'moo': 3 } }
    m4 = { 'foo': { 'bar': 4 } }
    m5 = { 'foo': 5 }

    u1 = app.cfgUnify(m1, m2, m3)
    assert u1.get('foo').get('bar') == 1
    assert u1.get('foo').get('moo') == 2
    assert u1.get('bar').get('moo') == 3

    u2 = app.cfgUnify(u1, m4)
    assert u1.get('foo').get('bar') == 1
    assert u2.get('foo').get('bar') == 4
    assert u2.get('foo').get('moo') == 2
    assert u2.get('bar').get('moo') == 3

    u3 = app.cfgUnify(u1, m5)
    assert u3.get('foo') == 5
    assert u3.get('bar').get('moo') == 3


def test_cfgUnify_case():
    m1 = { 'fooBar': 1 }
    m2 = { 'FOOBAR': 2 }

    # all-caps FOOBAR will overwrite camel-case fooBar
    u1 = app.cfgUnify(m1, m2)
    assert u1.get('fooBar') == 2

    # all-caps FOOBAR is first, so will produce 'foobar'
    # then camel-case fooBar will be a new entry
    u2 = app.cfgUnify(m2, m1)
    assert u2.get('fooBar') == 1
    assert u2.get('foobar') == 2

    # no case mangling, all keys are kept verbatim
    u3 = app.cfgUnify(m1, m2, mangle_case=False)
    assert u3.get('fooBar') == 1
    assert u3.get('FOOBAR') == 2
    assert u3 == app.cfgUnify(m2, m1, mangle_case=False)

    # This should raise an exception because now we have keys
    # FooBar and fooBar that differ in camel-case, but would be
    # the same in upper-case, before we try to update data using
    # FOOBAR as a key.
    m3 = { 'FooBar': 3 }
    with pytest.raises(RuntimeError) as e:
        app.cfgUnify(m1, m3, m2)


def test_app_config():
    # Tests the addConfig/addNestedConfig/addFlatConfig parts of IocApplication

    cfg1 = { 'epics': { 'prefix': 'FOO' },
             'extra': { 'param': 'cfg1' } }
    
    obj1 = app.IocApplication(prefix='BAR', cfg=cfg1)

    # cfg object overrides __init__ parameter
    assert obj1.conf.get('epics').get('prefix') == 'FOO'
    
    obj2 = app.IocApplication()
    obj2.addNestedConfig(cfg1)

    assert obj2.conf == obj1.conf
    assert obj2.conf == cfg1
    
    cfg3 = { 'extra': { 'param': 'cfg3' } }

    obj2.addNestedConfig(cfg3)
    assert obj2.conf['extra'] == cfg3['extra']

    obj2.addFlatConfig({'extra/param': 'cfg4'}, separator='/')
    assert obj2.conf['extra']['param'] == 'cfg4'

    obj2.addFlatConfig({'extra/param': 'cfg4'}, separator='/', subsection='extra')
    assert obj2.conf['extra'].get('extra').get('param') == 'cfg4'

    # setupIoc() prefix does *not* override an already existing prefix
    # But we can't test now because we can't actually access the real
    # prefix :-( All we can do is access obj1.conf['epics']['prefix'],
    # and that won't actually confirm that setupIoc behaves correctly.
    #obj1.setupIoc(prefix='MOO')
    #assert obj1.prefix == 'FOO'
        
    
def test_app_testmode():
    obj1 = app.IocApplication(cfg={'epics': { 'prefix': 'FOO' }})
    obj2 = app.IocApplication(cfg={'epics': { 'prefix': 'FOOTEST' }})

    assert not obj1.testModeRequested()
    assert obj2.testModeRequested()


@pytest.fixture
def random_prefix():
    return ''.join(random.choice(string.ascii_letters) for i in range(32))
    

def _test_app_sync_defaultioc(random_prefix):
    # Runs the default IOC (i.e. one where only the heartbeat PV is active)
    a = app.IocApplication(prefix='yadda')
    a.setupIoc(prefix=random_prefix)
    a.startIoc()

    assert a.running

    tmax = 3
    tstart = time.time()
    while a.running:
        tdiff = time.time()-tstart
        if tdiff < tmax:
            print ("Exitting in %d..." % (tmax+1-tdiff,))
            time.sleep(1.0)
        else:
            a.stopIoc()

    assert (not a.running)


@pytest.mark.asyncio
async def test_app_async_defaultioc(random_prefix):
    a = app.IocApplication(prefix=random_prefix)
    a.setupIoc()
    a.startIoc()

    # ab hier...

    from caproto.sync import client

    tstart = time.time()
    while time.time()-tstart < 3.0:
        print (client.read(random_prefix+":heartbeat").data)
        await asyncio.sleep(0.5)

    a.stopIoc()


def test_app_moo():
    print("Moo!")
