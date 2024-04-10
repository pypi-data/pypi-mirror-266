import RobotRaconteur as RR
RRN = RR.RobotRaconteurNode.s
import threading
import traceback


class RobustPollingAsyncFunctionCaller:
    """
    Class to call function that is polled periodically, or
    when requested

    :param f: The function to call
    :type f: callable
    :param f_args: The arguments to pass to the function
    :type f_args: list
    :param retry_backoff: The time to wait before retrying a failed call
    :type retry_backoff: float
    :param max_retry_attempts: The maximum number of retry attempts
    :type max_retry_attempts: int
    :param poll_interval: The polling interval in seconds
    :type poll_interval: float
    :param call_timeout: The timeout for the function call
    :type call_timeout: float
    :param error_handler: The error handler to call if the function call fails
    :type error_handler: callable
    :param node: (optional) The Robot Raconteur node to use for parsing. Defaults to RobotRaconteurNode.s
    :type node: RobotRaconteur.RobotRaconteurNode
    :param client_obj: (optional) The client object to use for finding types. Defaults to None
    :type client_obj: RobotRaconteur.ClientObject
    """

    def __init__(self, f, f_args, retry_backoff=1, max_retry_attempts=10, poll_interval=30, call_timeout=1, error_handler=None, node=None, client_obj=None):
        if node is None:
            self._node = RRN
        else:
            self._node = node
        self._client_obj = client_obj

        self._f = f
        self._f_args = f_args
        self._retry_backoff = retry_backoff
        self._max_retry_attempts = max_retry_attempts
        self._poll_interval = poll_interval
        self._lock = threading.RLock()
        self._error_handler = error_handler
        self._call_timeout = call_timeout
        self._refresh_timer = None
        self._retry_attempts = 0

        self._refreshing = False
        self._refresh_requested = False

        self._poll_data = RR.EventHook()

        self._poll_timer = self._node.CreateTimer(self._poll_interval, self._handle_poll_timer)
        self._poll_timer.Start()
        with self._lock:
            self._refresh_retry()

    @property
    def poll_data(self):
        """
        Returns the current polled data
        """
        return self._poll_data

    @poll_data.setter
    def poll_data(self, value):
        assert value == self._poll_data

    def request_poll(self):
        """
        Call to request a poll
        """

        with self._lock:
            if self._refreshing:
                self._refresh_requested = True
                return
            else:
                self._do_refresh()

    def _do_refresh(self):
        try:
            if len(self._f_args) == 0:
                self._f(self._refresh_handler, self._call_timeout)
            else:
                self._f(*self._f_args, self._refresh_handler, self._call_timeout)

            self._refreshing = True
        except Exception as e:
            try:
                if self._error_handler is not None:
                    self._error_handler(e)
            except:
                traceback.print_exc()
            try:
                self._refresh_retry()
            except RR.InvalidOperationException:
                pass

    def _refresh_handler(self, val, err):
        with self._lock:
            if err is not None:
                # TODO: log internal error
                self._refresh_retry()
                return
            self._retry_attempts = 0

        try:
            self._poll_data.fire(val)
        except Exception as e:
            try:
                if self._error_handler is not None:
                    self._error_handler(e)
            except:
                traceback.print_exc()

        with self._lock:
            if self._refresh_requested:
                self._refresh_retry()
            else:
                self._refreshing = False

    def _refresh_retry(self):
        if self._retry_attempts >= self._max_retry_attempts:
            return
        self._refresh_requested = False
        self._refresh_timer = self._node.CreateTimer(self._retry_backoff, self._refresh_timer_handler, oneshot=True)
        self._refresh_timer.Start()
        self._retry_attempts += 1

    def _refresh_timer_handler(self, timer_evt):
        with self._lock:
            self._refresh_timer = None
            self._do_refresh()

    def _handle_poll_timer(self, timer_evt):
        if timer_evt.stopped:
            return
        with self._lock:
            self._retry_attempts = 0
        self.request_poll()

    def close(self):
        """
        Close the polling function caller
        """
        self._poll_timer.Stop()
        self._poll_timer = None
