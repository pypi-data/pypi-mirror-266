# Python Reference

This repository contains but one simple but extremely useful Python class, `Make_Reference` and `Reference_Instance`.

This holy grail of simple python hacks, `refvars` provides a convenient way to work with references to objects. It allows you to set and get the value of the reference using simple methods.

## Usage

To use the `refvars` class, simply import it into your Python script:

```python
from refvars import Make_Reference, Reference_Instance
```

Then use `Make_Reference` to create a reference to an object:

```python
# Create a reference
ref = Make_Reference[int](0).reference
```

> Note that `Make_Reference` will run a variety of runtime AND intellisense time checks to ensure that the reference is being used correctly.

Now, you can use the `Reference_Instance` to get and set the value of the reference:

```python
# To ensure that the initial value does actually change.
print(ref.get())  # 0

# If we want a function to modify the reference, we can pass the reference to the function.
def modify_reference(ref:"Reference_Instance[int]"):
    ref.set(1)

modify_reference(ref)

# Now the getting is a bit different.
print(ref.get())  # 1
```

## Installation

To install the `refvars`, use pip:

```bash
pip install refvars
```

## Confirmed versions of Python

- [x] 3.11 - Works perfectly.
- [ ] 3.12 - Not tested.

## License

Covered under the GNU General Public License v2.0.
