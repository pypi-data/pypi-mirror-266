import pytest

from aleksis.core.mixins import RegistryObject


def test_registry_object_name():
    class ExampleRegistry(RegistryObject):
        pass

    class ExampleWithManualName(ExampleRegistry):
        name = "example_a"

    class ExampleWithAutomaticName(ExampleRegistry):
        pass

    class ExampleWithOverridenAutomaticName(ExampleWithManualName):
        name = "example_b"

    class ExampleWithOverridenManualName(ExampleWithAutomaticName):
        name = "example_bb"

    assert ExampleRegistry.name == ""
    assert ExampleWithManualName.name == "example_a"
    assert ExampleWithAutomaticName.name == "ExampleWithAutomaticName"
    assert ExampleWithOverridenAutomaticName.name == "example_b"
    assert ExampleWithOverridenManualName.name == "example_bb"


def test_registry_object_registry():
    class ExampleRegistry(RegistryObject):
        pass

    class ExampleA(ExampleRegistry):
        pass

    class ExampleB(ExampleRegistry):
        pass

    class ExampleAA(ExampleA):
        name = "example_aa"

    assert ExampleRegistry.registered_objects_dict == {
        "ExampleA": ExampleA,
        "ExampleB": ExampleB,
        "example_aa": ExampleAA,
    }
    assert ExampleRegistry.registered_objects_dict == ExampleRegistry._registry

    assert ExampleRegistry.registered_objects_list == [
        ExampleA,
        ExampleB,
        ExampleAA,
    ]

    assert ExampleRegistry.get_object_by_name("ExampleA") == ExampleA
    assert ExampleRegistry.get_object_by_name("ExampleB") == ExampleB
    assert ExampleRegistry.get_object_by_name("example_aa") == ExampleAA
