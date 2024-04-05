from datetime import datetime
from decimal import Decimal
from typing import Optional

import pytest
from pydantic import Field, ValidationError

from dvcx.lib.feature import Feature, ShallowFeature
from dvcx.sql.types import JSON, Array, Binary, Boolean, DateTime, Int, String


class FileBasic(ShallowFeature):
    parent: str = Field(default="")
    name: str
    size: int = Field(default=0)


class FileInfo(FileBasic):
    location: dict = Field(default={})


class FileInfoEx(ShallowFeature):
    f_info: FileInfo
    type_id: int


class MyNestedClass(Feature):
    type: int
    Name: str = Field(default="test1")


class MyTest(Feature):
    ThisIsName: str
    subClass: MyNestedClass  # noqa: N815


def test_flatten_schema():
    schema = FileInfo._to_udf_spec()

    assert 4 == len(schema)
    assert [item[0] for item in schema] == ["parent", "name", "size", "location"]
    assert [item[1] for item in schema] == [String, String, Int, JSON]


def test_type_datatype():
    class Test1(Feature):
        d: datetime

    schema = Test1._to_udf_spec()
    assert schema[0][1] == DateTime


def test_type_optional_int():
    class Test1(Feature):
        d: Optional[int] = 23

    schema = Test1._to_udf_spec()
    assert schema[0][1] == Int


def test_type_bytes():
    class Test1(Feature):
        d: bytes

    schema = Test1._to_udf_spec()
    assert schema[0][1] == Binary


def test_type_array():
    class Test1(Feature):
        d: list

    schema = Test1._to_udf_spec()
    assert schema[0][1] == Array


def test_type_arrays():
    class Test1(Feature):
        d1: list[int]
        d2: list[float]

    schema = Test1._to_udf_spec()

    type1 = schema[0][1]
    assert list == type1.python_type
    assert int == type1.impl.item_type.python_type

    type2 = schema[1][1]
    assert list == type2.python_type
    assert float == type2.impl.item_type.python_type


def test_type_array_of_arrays():
    class Test1(Feature):
        d1: list[list[int]]

    schema = Test1._to_udf_spec()

    type1 = schema[0][1]
    assert list == type1.python_type
    assert list == type1.impl.item_type.python_type
    assert int == type1.impl.item_type.impl.item_type.python_type


def test_type_json():
    class Test1(Feature):
        d: dict

    schema = Test1._to_udf_spec()
    assert schema[0][1] == JSON


def test_type_bool():
    class Test1(Feature):
        d: bool

    schema = Test1._to_udf_spec()
    assert schema[0][1] == Boolean


def test_type_typed_json():
    class Test1(Feature):
        d: Optional[dict[str, int]]

    schema = Test1._to_udf_spec()
    assert schema[0][1] == JSON


def test_unknown_type():
    class Test1(Feature):
        d: Optional[Decimal]

    with pytest.raises(RuntimeError):
        Test1._to_udf_spec()


def test_flatten_nested_schema():
    schema = FileInfoEx._to_udf_spec()

    assert 5 == len(schema)
    assert [item[0] for item in schema] == [
        "parent",
        "name",
        "size",
        "location",
        "type_id",
    ]
    assert [item[1] for item in schema] == [String, String, Int, JSON, Int]


def test_flatten_nested_schema_shallow():
    class MyTest1(Feature):
        a: int = Field(default=33)

    class MyTest2(Feature):
        next2: MyTest1

    class MyTest3(Feature):
        next3: MyTest2

    schema = MyTest3(next3=MyTest2(next2=MyTest1()))._to_udf_spec()
    assert [item[0] for item in schema] == ["my_test3__next3__next2__a"]

    class MyTest3Shallow(ShallowFeature):
        next3: MyTest2

    shallow_schema = MyTest3Shallow(next3=MyTest2(next2=MyTest1()))._to_udf_spec()
    assert [item[0] for item in shallow_schema] == ["a"]


def test_flatten_schema_list():
    t1 = FileInfo(name="test1")
    t2 = FileInfo(name="t2", parent="pp1")
    res = Feature._features_to_udf_spec([t1, t2])
    assert len(t1.model_dump()) == len(res)


def test_flatten_basic():
    vals = FileBasic(parent="hello", name="world", size=123)._flatten()
    assert vals == ("hello", "world", 123)


def test_flatten_with_json():
    t1 = FileInfo(parent="prt4", name="test1", size=42, location={"ee": "rr"})
    assert t1._flatten() == ("prt4", "test1", 42, {"ee": "rr"})


def test_flatten_with_empty_json():
    with pytest.raises(ValidationError):
        FileInfo(parent="prt4", name="test1", size=42, location=None)


def test_flatten_with_accepted_empty_json():
    class Test1(Feature):
        d: Optional[dict]

    assert Test1(d=None)._flatten() == (None,)


def test_flatten_nested():
    t0 = FileInfo(parent="sfo", name="sf", size=567, location={"42": 999})
    t1 = FileInfoEx(f_info=t0, type_id=1849)

    assert t1._flatten() == ("sfo", "sf", 567, {"42": 999}, 1849)


def test_flatten_list():
    t1 = FileInfo(parent="p1", name="n4", size=3, location={"a": "b"})
    t2 = FileInfo(parent="p2", name="n5", size=2, location={"c": "d"})

    vals = t1._flatten_list([t1, t2])
    assert vals == ("p1", "n4", 3, {"a": "b"}, "p2", "n5", 2, {"c": "d"})


@pytest.mark.parametrize("feature_class", [Feature, ShallowFeature])
def test_inheritance(feature_class):
    class SubObject(feature_class):
        subname: str

    class MyTest(feature_class):
        name: str
        sub: SubObject

    class MyTest2(MyTest):
        pass

    with pytest.raises(ValueError):
        MyTest2()

    obj = MyTest2(name="name", sub=SubObject(subname="subname"))
    assert obj._flatten() == ("name", "subname")


def test_naming_transform():
    assert [name for name, _ in MyTest._to_udf_spec()] == [
        "my_test__this_is_name",
        "my_test__sub_class__type",
        "my_test__sub_class__name",
    ]


def test_capital_letter_naming():
    class CAPLetterTEST(Feature):
        AAA_id: str

    vals = [name for name, _ in CAPLetterTEST._to_udf_spec()]
    assert vals == ["cap_letter_test__aaa_id"]


def test_delimiter_in_name():
    with pytest.raises(RuntimeError):

        class MyClass(Feature):
            var__name: str


def test_delimiter_in_name_is_allowed_for_shallow_class():
    class MyClass(ShallowFeature):
        var__name: str

    MyClass._to_udf_spec()

    obj = MyClass(var__name="some stuff")
    dump = obj.model_dump()
    obj._unflatten(dump)


def test_custom_delimiter_in_name():
    with pytest.raises(RuntimeError):

        class MyClass(Feature):
            _delimiter = "EE"
            is_ieee_member: bool


def test_naming_delimiter():
    class MyNestedClassNew(MyNestedClass):
        _delimiter = "+++"

    class MyTestNew(MyTest):
        _delimiter = "+++"

        ThisIsName: str
        subClass: MyNestedClassNew  # noqa: N815

    schema = MyTestNew._to_udf_spec()

    assert [name for name, _ in schema] == [
        "my_test_new+++this_is_name",
        "my_test_new+++sub_class+++type",
        "my_test_new+++sub_class+++name",
    ]


def test_deserialize_nested():
    class Child(Feature):
        type: int
        name: str = Field(default="test1")

    class Parent(Feature):
        name: str
        child: Child

    in_db_map = {
        "parent__name": "a1",
        "parent__child__type": 42,
        "parent__child__name": "a2",
    }

    p = Parent._unflatten(in_db_map)

    assert p.name == "a1"
    assert p.child.type == 42
    assert p.child.name == "a2"


def test_deserialize_shallow():
    class Child(ShallowFeature):
        type: int
        child_name: str = Field(default="test1")

    class Parent(ShallowFeature):
        name: str
        child: Child

    in_db_map = {
        "child_name": "a1",
        "type": 42,
        "name": "a2",
    }

    p = Parent._unflatten(in_db_map)

    assert p.name == "a2"
    assert p.child.type == 42
    assert p.child.child_name == "a1"


def test_deserialize_nested_with_name_normalization():
    class ChildClass(Feature):
        type: int
        name: str = Field(default="test1")

    class Parent(Feature):
        name: str
        childClass11: ChildClass  # noqa: N815

    in_db_map = {
        "parent__name": "name1",
        "parent__child_class11__type": 12,
        "parent__child_class11__name": "n2",
    }

    p = Parent._unflatten(in_db_map)

    assert p.name == "name1"
    assert p.childClass11.type == 12
    assert p.childClass11.name == "n2"


def test_type_array_of_floats():
    class Test1(Feature):
        d: list[float]

    dict_ = {"d": [1, 3, 5]}
    t = Test1(**dict_)
    assert t.d == [1, 3, 5]


def test_class_attr_resolver_basic():
    class MyTest6(Feature):
        val1: list[float]
        pp: int

    assert MyTest6.val1.name == "my_test6__val1"
    assert MyTest6.pp.name == "my_test6__pp"


def test_class_attr_resolver_shallow():
    class MyTest6(ShallowFeature):
        val1: list[float]
        pp: int

    assert MyTest6.val1.name == "val1"
    assert MyTest6.pp.name == "pp"


def test_class_attr_resolver_nested():
    assert MyTest.subClass.type.name == "my_test__sub_class__type"
    assert MyTest.subClass.Name.name == "my_test__sub_class__name"


def test_class_attr_resolver_nested_3levels():
    class MyTest1(Feature):
        a: int

    class MyTest2(Feature):
        b: MyTest1

    class MyTest3(Feature):
        c: MyTest2

    assert MyTest3.c.b.a.name == "my_test3__c__b__a"
