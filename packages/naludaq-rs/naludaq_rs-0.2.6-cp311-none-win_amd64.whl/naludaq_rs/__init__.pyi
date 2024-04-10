class Server:
    def __init__(
        self,
        addr: tuple[str, int],
        output: str,
    ) -> None:
        """Create a new hardware server with the given configuration.

        The server is not started initial until the `start()` function is called.
        Error reporting is extremely limited, so it is recommended to check the
        log file for any errors.

        Args:
            addr (tuple[str, int]): The address to bind to as (host, port)
            output (str): The storage directory for acquisitions.
        """
    @property
    def address(self) -> tuple[str, int]:
        """Get the address the server is bound to.

        Returns:
            tuple[str, int]: The address the server is bound to as
                (host, port).
        """
    @property
    def output_directory(self) -> str:
        """Get the output directory for acquisitions.

        Returns:
            str: The output directory for acquisitions.
        """
    def start(self) -> None:
        """Start the server in a new thread.

        A check is performed after starting to ensure the server is alive.
        If successful, the server may be reached at the address given in
        the constructor.

        Raises:
            OSError: If the server could not be started.
            TimeoutError: If the server cannot not be accessed after starting.
        """
    def stop(self) -> None:
        """Stop the server.

        This function blocks until the server has received the request to
        stop, but not necessarily until it has terminated; the address may
        be held by the server for a short time after this function returns
        until the server has finished cleanup.
        """
    def is_running(self) -> bool:
        """Check if the server is running.

        Returns:
            bool: True if the server is running, False otherwise.
        """
