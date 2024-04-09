from ward import test, raises

from packages.experimental.flask_cruddy.form_components import Checkbox


@test("checkbox has name")
def _():
    assert Checkbox.make("test").render()["name"] == "test"

@test("name is string")
def _():
    assert isinstance(Checkbox.make("test").render()["name"], str)

@test("name must be string")
def _():
    with raises(TypeError) as ex:
        Checkbox.make(1).render()
    assert str(ex.raised) == "Name must be a string"