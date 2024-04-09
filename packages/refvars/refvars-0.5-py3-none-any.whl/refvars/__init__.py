from typing import Any, Generic, TypeVar
import inspect



T_PYTHON_REFERENCE = TypeVar('T_PYTHON_REFERENCE')
_REF_VARS_SPECIAL_SAUCE = False



class Reference_Instance (Generic[T_PYTHON_REFERENCE]):
	def __init__(self, type_:"str", value_:"T_PYTHON_REFERENCE"):
		global _REF_VARS_SPECIAL_SAUCE
		if _REF_VARS_SPECIAL_SAUCE == True:
			self.type = type_
			self.value = value_
		else:
			err_msg = "\n\n[[[ ERROR FROM `refvars`! ]]]\n"
			err_msg += f"Do not instantiate the class `ReferenceInstance` directly.\n"
			err_msg += f"Instead, use the class `Make_Reference`.\n"
			raise SyntaxError(err_msg)

	def get(self) -> "T_PYTHON_REFERENCE":
		return self.value

	def set(self, value_:"T_PYTHON_REFERENCE"):
		if value_.__class__.__name__ != self.type:
			err_msg = "\n\n[[[ ERROR FROM `refvars`! ]]]\n"
			err_msg += f"Argument 1 of `ReferenceInstance.set` is not of type [{self.type}].\n"
			raise TypeError(err_msg)
		self.value = value_



class Make_Reference (Generic[T_PYTHON_REFERENCE]):
	@property
	def reference(self) -> "Reference_Instance[T_PYTHON_REFERENCE]":
		return self._reference

	def __validate_type(self, line:str, file:str, line_no:int):
		# Need to get the type of the class.
		# The type is the part of the line after the square brackets.
		s = line.split("=")[1].strip()
		s = s.split("[")[1].strip()
		s = s.split("]")[0].strip()
		if self._type != s:
			err_msg = "\n\n[[[ ERROR FROM `refvars`! ]]]\n"
			err_msg += f"For the class `Make_Reference`, the value passed in must match the generic.\n"
			err_msg += f"Example of incorrect:  `my_ref = Make_Reference[bool](\"x\").reference`.\n"
			err_msg += f"Example of correct:    `my_ref = Make_Reference[bool](True).reference`.\n"
			err_msg += f"> Notice the `True` is a correct value for the generic `bool`.\n\n"
			err_msg += f"Error occurred at line [{line_no}] in file [{file}].\n"
			err_msg += f"> You tried to match the value type of [{self._type}]"
			err_msg += f" with the generic type of [{s}].\n"
			raise SyntaxError(err_msg)

	def _validate(self):
		# Need to get the line where the class was instantiated.
		stack = inspect.stack()
		caller = stack[3]
		line_no = caller.lineno
		file = caller.filename
		with open(file, "r") as f:
			lines = f.readlines()
		_line = lines[line_no-1]
		line = _line.strip().split("#")[0]
		if not line.endswith(".reference"):
			err_msg = "\n\n[[[ ERROR FROM `refvars`! ]]]\n"
			err_msg += f"For the class `Make_Reference`, the class instantiation must be assigned"
			err_msg += f" using the syntax `my_ref = Make_Reference[< type >](< initial value >).reference`.\n"
			err_msg += f"> Notice the `.reference` at the end of the instantiation.\n"
			err_msg += f"Error occurred at line [{line_no}] in file [{file}].\n"
			raise SyntaxError(err_msg)
		self.__validate_type(line, file, line_no)

	def __init__(self, value_:"T_PYTHON_REFERENCE"):
		global _REF_VARS_SPECIAL_SAUCE
		self._value = value_
		self._type = value_.__class__.__name__
		self._validate()
		try:
			_REF_VARS_SPECIAL_SAUCE = True
			self._reference = Reference_Instance[type(value_)](self._type, value_)
		finally:
			_REF_VARS_SPECIAL_SAUCE = False



print("HERE", flush=True)
my_ref = Make_Reference[bool](True).reference

def parse(ref:"Reference_Instance[bool]"):
	if ref.get() == True:
		print("The reference is True.")
	else:
		print("The reference is False.")
	
parse(my_ref)
my_ref.set(False)
parse(my_ref)

