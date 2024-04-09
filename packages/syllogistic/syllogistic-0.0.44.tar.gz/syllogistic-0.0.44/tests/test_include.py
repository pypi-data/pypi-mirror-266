import os
import pytest
import unittest

from syllogistic.processor import ProcessorContext, ProcessorException, process_lines


class TestInclude(unittest.TestCase):
    def test_include(self):
      code = "-- #include './sample.lua'"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """function sample()
  trace('sample')
end"""

    def test_include_absolute(self):
      path = os.path.abspath('tests/input/sample.lua')
      path = os.path.splitdrive(path)

      if (path[0] != ''):
        path = ('', path[1].replace('\\', '/'))

      code = f"-- #include '{path[1]}'"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """function sample()
  trace('sample')
end"""

    def test_include_index(self):
      code = "-- #include './lib/test'"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- lib/test/index.lua
-- aa.lua
aa={}

function aa.doA()
end
-- bb.lua
bb={
  doB=function()
  end
}
-- cc.lua
cc={
  doC=function ()
  end,
  doCGroupAOpt=function ()
  end,
}
"""

    def test_include_as(self):
      code = "-- #include './lib'"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- lib/index.lua
lib={__autogen=true}
-- lib/test/index.lua
-- lib.aa.lua
lib.aa={}

function lib.aa.doA()
end
-- lib.bb.lua
lib.bb={
  doB=function()
  end
}
-- lib.cc.lua
lib.cc={
  doC=function ()
  end,
  doCGroupAOpt=function ()
  end,
}

"""

    def test_include_groups_remove(self):
      code = "-- #include './groups.lua' -C"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- groups.lua
test={
  test=function ()
  end,
  testGroupA=function ()
  end,
}

"""

    def test_include_groups_remove2(self):
      code = "-- #include './groups.lua' -A"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- groups.lua
test={
  test=function ()
  end,
  testGroupC=function ()
  end,
}

"""

    def test_include_groups_add(self):
      code = "-- #include './groups.lua' +B"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- groups.lua
test={
  test=function ()
  end,
  testGroupA=function ()
  end,
  testGroupB=function ()
  end,
  testGroupC=function ()
  end,
}

function test.testGroupBStandalone()
end
"""

      code = "-- #include './groups.lua' +C"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- groups.lua
test={
  test=function ()
  end,
  testGroupA=function ()
  end,
  testGroupC=function ()
  end,
}


function test.testGroupCStandalone()
end"""

    def test_include_groups_add2(self):
      code = "-- #include './groups.lua' +B,C"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- groups.lua
test={
  test=function ()
  end,
  testGroupA=function ()
  end,
  testGroupB=function ()
  end,
  testGroupC=function ()
  end,
}

function test.testGroupBStandalone()
end

function test.testGroupCStandalone()
end"""

    def test_include_groups_add_remove_nest(self):
      code = "-- #include './groups.lua' -A +B"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- groups.lua
test={
  test=function ()
  end,
  testGroupC=function ()
  end,
}

function test.testGroupBStandalone()
end
"""

      code = "-- #include './groups.lua' +B -A"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == """-- groups.lua
test={
  test=function ()
  end,
  testGroupC=function ()
  end,
}

function test.testGroupBStandalone()
end
"""

    def test_include_package(self):
      code = "-- #include 'test'"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == "debug={value='success'}"

    def test_include_package_part(self):
      code = "-- #include 'test/debug.lua'"
      context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
      result = process_lines(context)

      assert result == "debug={value='success'}"

    def test_include_no_win_absolute(self):
      with pytest.raises(ProcessorException):
        code = "-- #include 'C:\\tests\\input\\sample.lua'"
        context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
        result = process_lines(context)

    def test_include_malformed_include(self):
      with pytest.raises(ProcessorException):
        code = "-- #include ./sample.lua"
        context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
        result = process_lines(context)

    def test_include_disallowed_prefix(self):
      with pytest.raises(ProcessorException):
        code = "-- #include '~sample.lua'"
        context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
        result = process_lines(context)

    def test_include_malformed_as(self):
      with pytest.raises(ProcessorException):
        code = "-- #include './sample.lua' as"
        context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
        result = process_lines(context)

    def test_include_unknown_package(self):
      with pytest.raises(ProcessorException):
        code = "-- #include 'thisisnotavalidpackagenameandlikelywontexist'"
        context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
        result = process_lines(context)

    def test_include_malformed_groups(self):
      with pytest.raises(ProcessorException):
        code = "-- #include ./groups-bad.lua"
        context = ProcessorContext('tests/input/fake.lua', code.split('\n'), strict=True);
        result = process_lines(context)
