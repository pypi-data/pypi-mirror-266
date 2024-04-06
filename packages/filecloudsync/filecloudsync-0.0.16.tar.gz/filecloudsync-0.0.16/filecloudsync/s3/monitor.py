from shutil import rmtree
from threading import Thread, Event
from typing import Set, Callable, List, Tuple

from filecloudsync import s3
from filecloudsync.s3.core import Location, Operation


class Monitor(Thread):
    """ A monitor to synchronize a bucket with a folder. """

    def __init__(
            self,
            bucket: str,
            folder: str,
            delay: int = 60,
            files: Set[str] = None,
            remove: bool = False,
            readonly: bool = False,
            **kwargs
    ) -> None:
        """ Create a monitor of a bucket or some files of that bucket and synchronize them with a given folder

        .. code-block:: python
            x = 1 # Testing embedded code
            print(x)

        :param bucket: The bucket name.
        :param folder: The folder path.
        :param delay: The delay between bucket checking
        :param files: A list of keys to watch in Unix file path format.
            If none is given, then check all the bucket/folder files.
        :param remove: Decide if the local synchronized folder is deleted when the monitor stops,
            and the synchronization data is also removed.
            This parameter is useful when the folder is created in a temporal directory.
        :param readonly: If the bucket is a readonly bucket.
        :param kwargs: The s3 connection credentials
        """
        super().__init__()
        self._client = s3.connect(**kwargs)
        self.bucket = bucket
        self.folder = folder
        self.delay = delay
        self.files = files
        self.remove = remove
        self._stop_event = False
        self._interrupt_event = Event()
        self._on_change_hooks = set()
        self._on_finish_hooks = set()
        self.readonly = readonly
        s3.sync(self._client, self.bucket, self.folder, self.files, readonly)

    def _trigger_on_change(self, file: str, operation: Operation, location: Location) -> None:
        """ Trigger an event to the on change hooks when a file is changed
        :param file: The file with the event
        :param operation: The operation realized in that file
        :param location: Where the file is, on the local folder or on the bucket
        """
        for hook in self._on_change_hooks:
            hook(file, operation, location)

    def _trigger_on_finish(self, changes: List[Tuple[str, Operation, Location]]) -> None:
        """ Trigger when the monitor finishes
        :param changes: The list of detected last changes if any.
            Each list element contains the bucket key, the operation (MODIFIED, ADDED or DELETED),
            and the location (LOCAL or BUCKET)
        """
        for hook in self._on_finish_hooks:
            hook(changes)

    def run(self) -> None:
        """ Execute the monitor """
        try:
            while not self._stop_event:
                changes = s3.sync(self._client, self.bucket, self.folder, self.files, self.readonly)
                for key, operation, location in changes:
                    self._trigger_on_change(key, operation, location)
                self._interrupt_event.wait(timeout=self.delay)
        finally:
            changes = s3.sync(self._client, self.bucket, self.folder, self.files, self.readonly)
            self._trigger_on_finish(changes)

    def add_on_change_handle(self, handle: Callable[[str, Operation, Location], None]) -> None:
        """ Add an on change event handle
        :param handle: The handle function to add.
            The handle will receive the bucket key, the operation (MODIFIED, ADDED or DELETED),
            and the location (LOCAL or BUCKET)
        """
        self._on_change_hooks.add(handle)

    def add_on_finish_handle(self, handle: Callable[[List[Tuple[str, Operation, Location]]], None]) -> None:
        """ Add an on finish event handle
        :param handle: The handle function to add.
            The handle will receive a list of each change if any or an empty set.
            Each list element contains the bucket key, the operation (MODIFIED, ADDED or DELETED),
            and the location (LOCAL or BUCKET)
        """
        self._on_finish_hooks.add(handle)

    def remove(self, handle: Callable[[str, Operation, Location], None]) -> None:
        """ Remove an event handle
        :param handle: The handle function to remove
        """
        self._on_change_hooks.remove(handle)

    def stop(self):
        """ Stops the monitor """
        self._stop_event = True
        self._interrupt_event.set()
        self.join()
        if self.remove:
            s3.remove_sync_status(self._client.meta.endpoint_url, self.bucket, self.folder)
            rmtree(self.folder, ignore_errors=True)

    def join(self, timeout: int = None):
        """ Wait until the thread finishes or the timeout is reached """
        self._interrupt_event.set()
        super().join(timeout)

    def __enter__(self):
        """ Starts the monitor """
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Stop the monitor """
        self.stop()
