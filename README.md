# library to interact with 9kw.eu

usage example:
```python
solver = nine_kw("Your API CODE", priority=0, timeout=300)
print(solver.credits)
solver.submit("test.gif")
result = solver.result_loop()
print(result)
if result is None:
    solver.result_feedback(None)
else:
    correct = (result == "kM7wuT")
    print(correct)
    solver.result_feedback(correct)
```