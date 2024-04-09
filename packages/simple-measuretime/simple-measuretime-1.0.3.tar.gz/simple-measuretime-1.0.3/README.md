### Simple functions to measure times in functions and proccess

#### How to install


#### ` MeasureTime ` function decorator examples
- Debug a function when its finish
``` python
tempTimer = Timer()

@MeasureTime(
  measurekwarg=True,
  logOpts={'message': 'Function finished in {seconds}', 'method': print},
  finishDebug=True
)
def tester(count: float=1, measuretime: MeasureTime=None, timer: Timer=None):
  time.sleep(count)

tester(0.1, timer=tempTimer)
tester(0.2, timer=tempTimer)

Output:
Function finished in 0.1
Function finished in 0.3
```

- Debuging a function manually
``` python
@MeasureTime(measurekwarg=True)
def tester(count: float=1, measuretime: MeasureTime=None):
  time.sleep(count)
  measuretime.debug('First message debug {milliseconds}ms')
  time.sleep(count)
  measuretime.debug('Second message debug {milliseconds}ms')

tester(0.1)

Output:
First message debug 100.34ms
Second message debug 201.79ms
```