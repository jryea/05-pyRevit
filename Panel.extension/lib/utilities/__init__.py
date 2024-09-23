import time

def stopwatch(func):
  def wrapper():
    start = time.time()
    func()
    end = time.time()
    time_elapsed = end - start
    print('Function: ' + func.__name__ + ' took ' + time_elapsed +' to run' )
  return wrapper
