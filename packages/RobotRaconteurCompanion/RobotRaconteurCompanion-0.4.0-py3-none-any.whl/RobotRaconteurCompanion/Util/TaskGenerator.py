import RobotRaconteur as RR
import threading


class AsyncTaskGenerator:
    """
    Base class for asynchronous task generators

    Base class for asynchronous task generators. This utility class is used
    to help implement generators that represent long running operations.

    Subclasses should override the following functions:

    * StartTask() - Called when the generator is started
    * FillStatus() - Called to fill the next intermediate status report
    * CloseRequested() - Called when the generator is closed
    * AbortRequested() - Called when the generator is aborted

    The operation should call SetResult() or SetResultException() when the
    operation is complete. The generator will then return the result to the
    caller.

    :param node: The Robot Raconteur node for the generator
    :type node: RobotRaconteur.RobotRaconteurNode
    :param status_type: The status type for the generator. Used to create the status report structure
    :type status_type: type
    :param next_timeout: The timeout to return from the Next() function in seconds
    :type next_timeout: float
    :param watchdog_timeout: The timeout for the watchdog in seconds. -1 to disable.
    :type watchdog_timeout: float
    """

    def __init__(self, node, status_type, next_timeout, watchdog_timeout):
        self._node = node
        self._status_type = status_type
        self._next_timer = None
        self._watchdog_timer = None
        self._started = False
        self._closed = False
        self._aborted = False
        self._completed = False
        self._task_completed = False
        self._next_timeout = next_timeout
        self._watchdog_timeout = watchdog_timeout
        self._this_lock = threading.Lock()
        self._next_handler = None
        self._result = None
        self._exception_result = None
        self._send_update = False
        self._action_const = node.GetConstants("com.robotraconteur.action")

    def AsyncNext(self, handler):
        with self._this_lock:
            if self._watchdog_timeout is not None:
                try:
                    self._watchdog_timer.Stop()
                except Exception:
                    pass
                self._watchdog_timer = None
            if self._aborted:
                raise RR.OperationAbortedException("Operation aborted")
            if (self._closed and not self._started) or self._completed:
                raise RR.StopIterationException("")
            if not self._started:
                self.StartTask()
                self._started = True
                ret = self._status_type()
                ret.action_status = self._action_const["ActionStatusCode"]["running"]
                handler(ret, None)
                return

            if self._next_handler is not None:
                raise RR.InvalidOperationException("Next call already in progress")

            if self._task_completed:
                self._complete_gen(handler)
                return

            if (self._send_update):
                self._send_update = False
                ret = self._status_type()
                ret.action_status = self._action_const["ActionStatusCode"]["running"]
                self.FillStatus(ret)
                handler(ret, None)
                return

            self._next_handler = handler
            self._next_timer = self._node.CreateTimer(self._next_timeout, self._next_timer_handler, True)
            self._next_timer.Start()

            if self._watchdog_timeout > 0:
                self._watchdog_timer = self._node.CreateTimer(
                    self._watchdog_timeout, self._watchdog_timer_handler, True)
                self._watchdog_timer.Start()

    def AsyncAbort(self, handler, timeout):
        with self._this_lock:
            if self._closed or self._aborted:
                handler(None)
                return
            self._aborted = True
            if self._started:
                self.AbortRequested()
        handler(None)

    def AsyncClose(self, handler, timeout):
        with self._this_lock:
            if self._closed or self._aborted:
                handler(None)
                return
            self._closed = True
            if self._started:
                self.CloseRequested()
        handler(None)

    def SetResult(self, result):
        """
        Set the result of the generator

        This method sets the result of the generator. The generator will return
        the result to the caller.

        :param result: The result to return
        """
        with self._this_lock:
            if self._task_completed:
                return
            self._result = result
            self._do_result()

    def SetResultException(self, exp):
        """
        Set the exception result of the generator

        This method sets the exception result of the generator. The generator will return
        the exception to the caller.

        :param exp: The exception to return
        """
        with self._this_lock:
            if self._task_completed:
                return
            self._exception_result = exp
            self._do_result()

    def _do_result(self):
        self._task_completed = True
        h = self._next_handler
        self._next_handler = None
        if h is not None:
            try:
                self._next_timer.Stop()
            except Exception:
                pass
            self._next_timer = None
            self._complete_gen(h)
            return

    def _complete_gen(self, handler):
        self._completed = True
        if self._exception_result is not None:
            exp = self._exception_result
            self._exception_result = None
            handler(None, exp)
            return
        ret = self._result
        self._result = None
        handler(ret, None)

    def SendUpdate(self):
        """
        Send an update to the caller

        This method triggers Next() to return an intermediate status report. Override
        FillStatus() to fill the status report.
        """
        with self._this_lock:
            if self._task_completed or self._aborted or self._closed:
                return

            if self._next_handler is None:
                self._send_update = True
                return

            try:
                self._next_timer.Stop()
            except Exception:
                pass

            self._do_send_update()

    def StartTask(self):
        """
        Start the task

        This method is called when the generator is started. Subclasses should
        override this method to start the task.
        """
        raise NotImplementedError("")

    def CloseRequested(self):
        """
        This method is called when a close request is received.
        """
        pass

    def AbortRequested(self):
        """
        This method is called when an abort request is received.
        """
        pass

    def FillStatus(self, status):
        """
        This method is called to fill the next status report

        This method is called to fill the next status report. Subclasses should
        override this method to fill the next status report.

        :param status: The status report to fill
        """
        pass

    def _next_timer_handler(self, evt):
        with self._this_lock:
            self._do_send_update()

    def _do_send_update(self):
        h = self._next_handler
        self._next_handler = None
        if h is not None:
            ret = self._status_type()
            ret.action_status = self._action_const["ActionStatusCode"]["running"]
            self.FillStatus(ret)
            h(ret, None)
            return

    def _watchdog_timer_handler(self, evt):
        with self._this_lock:
            if evt.stopped:
                return
            if self._task_completed:
                return
            self._aborted = True
            self.AbortRequested()


class SyncTaskGenerator(AsyncTaskGenerator):
    """
    Base class for synchronous task generators

    This class is derived from the AsyncTaskGenerator class and provides a framework for generating synchronous tasks.
    It allows the user to define a RunTask() function that performs the actual task and returns a result of type StatusType.
    The task is executed in a separate thread and the result is set using the SetResult() function.
    If an exception occurs during task execution, it is caught and converted to a RobotRaconteurException, which is then set as the result exception.

    The user should override the RunTask() function to perform the actual task. The StartTask(),
    SetResult(), and SetResultException() functions should not be called by the user.

    :param node: The Robot Raconteur node for the generator
    :type node: RobotRaconteur.RobotRaconteurNode
    :param status_type: The status type for the generator. Used to create the status report structure
    :type status_type: type
    :param next_timeout: The timeout to return from the Next() function in seconds
    :type next_timeout: float
    :param watchdog_timeout: The timeout for the watchdog in seconds. -1 to disable.
    :type watchdog_timeout: float
    """

    def __init__(self, node, status_type, next_timeout, watchdog_timeout):
        super().__init__(node, status_type, next_timeout, watchdog_timeout)

        self._thread = None

    def RunTask(self):
        """
        Pure virtual function to be implemented by the user.

        This function should perform the actual task and return a result of type StatusType.

        :return: The result of the task.
        :rtype: status_type
        """
        raise NotImplementedError("RunTask not implemented")

    def run_task_thread(self):
        try:
            ret = self.RunTask()
            self.SetResult(ret)
        except Exception as exp:
            self.SetResultException(exp)

    def StartTask(self):
        self._thread = threading.Thread(target=self.run_task_thread)
        self._thread.start()
