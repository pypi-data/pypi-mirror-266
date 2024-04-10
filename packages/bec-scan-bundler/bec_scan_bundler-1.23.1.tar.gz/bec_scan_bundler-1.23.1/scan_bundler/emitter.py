import threading
import time
from queue import Queue

from bec_lib import messages


class EmitterBase:
    def __init__(self, connector) -> None:
        self._send_buffer = Queue()
        self.connector = connector
        self._buffered_connector_thread = None
        self._buffered_publisher_stop_event = threading.Event()
        self._start_buffered_connector()

    def _start_buffered_connector(self):
        self._buffered_connector_thread = threading.Thread(
            target=self._buffered_publish, daemon=True, name="buffered_publisher"
        )
        self._buffered_connector_thread.start()

    def add_message(self, msg: messages.BECMessage, endpoint: str, public: str = None):
        self._send_buffer.put((msg, endpoint, public))

    def _buffered_publish(self):
        while not self._buffered_publisher_stop_event.is_set():
            self._publish_data()

    def _get_messages_from_buffer(self) -> list:
        msgs_to_send = []
        while not self._send_buffer.empty():
            msgs_to_send.append(self._send_buffer.get())
        return msgs_to_send

    def _publish_data(self) -> None:
        msgs_to_send = self._get_messages_from_buffer()

        if not msgs_to_send:
            time.sleep(0.1)
            return

        pipe = self.connector.pipeline()
        msgs = messages.BundleMessage()
        _, endpoint, _ = msgs_to_send[0]
        for msg, endpoint, public in msgs_to_send:
            msg_dump = msg
            msgs.append(msg_dump)
            if public:
                self.connector.set(public, msg_dump, pipe=pipe, expire=1800)
        self.connector.send(endpoint, msgs, pipe=pipe)
        pipe.execute()

    def on_init(self, scan_id: str):
        pass

    def on_scan_point_emit(self, scan_id: str, point_id: int):
        pass

    def on_baseline_emit(self, scan_id: str):
        pass

    def on_cleanup(self, scan_id: str):
        pass

    def shutdown(self):
        if self._buffered_connector_thread:
            self._buffered_publisher_stop_event.set()
            self._buffered_connector_thread.join()
            self._buffered_connector_thread = None
