# pytest-initry

Plugin for sending automation test data from Pytest to the [initry](https://github.com/initry/initry).

1. Install:
   ```
   pip install pytest-initry
   ```
2. Configure pytest.ini:
    ```ini
    [pytest]
    initry_host = localhost
    initry_grpc_port = 50051
    initry_batching = false
    ```
3. CLI can also be used, but it's not the preferred method. The arguments will be the same as those mentioned for the pytest.ini config file.
    ```bash
    pytest --initry-host=localhost --initry-batching=true
    ```

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
