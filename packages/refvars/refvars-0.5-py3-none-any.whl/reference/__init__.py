from typing import Any, Generic, TypeVar

T_PYTHON_REFERENCE = TypeVar('T_PYTHON_REFERENCE')

class Reference(Generic[T_PYTHON_REFERENCE]):
	def __init__(self, value:"T_PYTHON_REFERENCE"):
		self.value = value

	def set(self, value:"T_PYTHON_REFERENCE"):
		self.value = value

	def __call__(self, *args:"Any", **kwds:"Any") -> "T_PYTHON_REFERENCE":
		if not (len(args) == 0 and len(kwds) == 0):
			raise Exception("`Reference` must be called with zero arguments.")
		return self.value

