import re, time


class TimeUnits:
  nanoseconds = 1
  microseconds = 1_000
  milliseconds = 1_000_000
  seconds = 1_000_000_000

  obj = {
    'nanoseconds': nanoseconds,
    'microseconds': microseconds,
    'milliseconds': milliseconds,
    'seconds': seconds
  }


class PerformanceTime:
  def __init__(self, nanoPerf: float=-1, timeUnit = TimeUnits.nanoseconds):
    if nanoPerf == -1: self.nanoPerf = time.perf_counter_ns()
    else: self.nanoPerf = nanoPerf
    self.timeUnit = timeUnit
  
  def __str__(self):
    return str(self.nanoPerf)

  def transform(self, varation: int=TimeUnits.milliseconds, replace: bool=False) -> float:
    if varation == TimeUnits.nanoseconds:
      return self.nanoPerf * self.timeUnit
    if self.timeUnit != TimeUnits.nanoseconds:
      temp = self.transform(TimeUnits.nanoseconds)
    else: temp = self.nanoPerf

    if replace == True:
      self.nanoPerf = temp / varation
      self.timeUnit = varation
      return self
    return temp / varation

  def replaceText(self, text: str, ndigits: int=2, pattern: str= '{timeunit}'):
    for i in TimeUnits.obj:
      auxPattern = pattern.replace('timeunit', i)
      
      varationNumber = round(self.transform(TimeUnits.obj[i]), ndigits)
      if ndigits == 0: varationNumber = int(varationNumber)

      text = re.sub(auxPattern, str(varationNumber), text)
    return text

  def __sub__(self, other):
    if self.timeUnit == other.timeUnit:
      return PerformanceTime(self.nanoPerf - other.nanoPerf)
    return PerformanceTime(self.transform(TimeUnits.nanoseconds) - other.transform(TimeUnits.nanoseconds))
  def __add__(self, other):
    if self.timeUnit == other.timeUnit:
      return PerformanceTime(self.nanoPerf + other.nanoPerf)
    return PerformanceTime(self.transform(TimeUnits.nanoseconds) + other.transform(TimeUnits.nanoseconds))
  def __mul__(self, other):
    return PerformanceTime(self.nanoPerf * other)
  def __truediv__(self, other):
    return PerformanceTime(self.nanoPerf / other)
  def __floordiv__(self, other):
    return PerformanceTime(self.nanoPerf // other)
  def __eq__(self, other):
    return self.nanoPerf == other.nanoPerf
  def __ne__(self, other):
    return self.nanoPerf != other.nanoPerf
  def __lt__(self, other):
    return self.nanoPerf < other.nanoPerf
  def __le__(self, other):
    return self.nanoPerf <= other.nanoPerf


class Timer:
  def __init__(self):
    self.start()
    self.stop()
    self.breaks = []

  def start(self) -> PerformanceTime:
    self.startTime = PerformanceTime()
    return self.startTime

  def stop(self) -> PerformanceTime:
    self.stopTime = PerformanceTime()
    return self.stopTime

  def reset(self):
    self.start()
    self.stop()

  def breakTime(self):
    self.breaks.append(PerformanceTime() - self.startTime)
  
  def gap(self, perfTime: PerformanceTime|None=None) -> PerformanceTime:
    if perfTime == None:
      self.stop()
      return self.stopTime - self.startTime
    return perfTime - self.startTime


class MeasureTime:
  kwargs = {
    'measureTime': 'measuretime',
    'timer': 'timer'
  }

  def __init__(self,
    measurekwarg: bool|None=None,
    finishDebug: bool|None=None,
    logOpts: dict={
      'message': None,
      'method': None
    },
    timer: Timer=None
  ):
    self.logOpts = logOpts
    if logOpts['method'] != None and not callable(logOpts['method']):
      raise TypeError('Log method must be callable')
    elif logOpts['method'] == None:
      self.logOpts['method'] = print

    self.measurekwarg = measurekwarg
    self.finishDebug = finishDebug
    if timer == None: self.timer = Timer()
    else: self.timer = timer

  def setAttrs(self, values: dict):
    for i in values:
      if values[i] is None:
        continue
      setattr(self, i, values[i])

  def debug(
    self,
    message: str|None=None,
    timer: Timer|None=None,
    replaceMessage: bool=False
  ):
    if message == None: message = self.logOpts['message']
    if timer == None: timer = self.timer

    if replaceMessage == True:
      self.logOpts['message'] = message

    self.logOpts['method'](timer.gap().replaceText(message))

  def __call__(self, func):
    def _logMessage(timer: Timer):
      if self.finishDebug and self.logOpts['message'] != 'None':
        self.debug(self.logOpts['message'], timer)

    def wrapper(*args, **kwargs):
      mainTimer = None

      if self.measurekwarg and MeasureTime.kwargs['timer'] in kwargs:
        if isinstance(kwargs[MeasureTime.kwargs['timer']], Timer):
          mainTimer = kwargs[MeasureTime.kwargs['timer']]

      if self.measurekwarg and MeasureTime.kwargs['measureTime'] in kwargs:
        if isinstance(kwargs[MeasureTime.kwargs['measureTime']], MeasureTime):
          self.setAttrs(kwargs[MeasureTime.kwargs['measureTime']].__dict__)
      elif self.measurekwarg and not MeasureTime.kwargs['measureTime'] in kwargs:
        kwargs[MeasureTime.kwargs['measureTime']] = self

      if mainTimer is None:
        mainTimer = Timer()

      self.timer = mainTimer
      result = func(*args, **kwargs)
      
      _logMessage(mainTimer)
      return result
    return wrapper
  