class Pol:
    def po(self):
        return 6


def test_myfunction(mocker):
    # Crear un mock para 'function_to_mock'
    my_instance = Pol()

    # Mockear un método de esa instancia
    mocker.patch.object(my_instance, "po", return_value=8)

    # Ahora, al llamar a 'method_to_mock', se devolverá 'mocked response'
    result = my_instance.po()

    # Realizar aserciones
    assert result == 8
