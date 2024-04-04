from typing import List, Optional, Tuple, Dict, Any

from EVMVerifier import certoraType as CT

STATEMUT = "stateMutability"

class Func:
    def __init__(self,
                 name: str,
                 fullArgs: List[CT.TypeInstance],
                 paramNames: List[str],
                 returns: List[CT.TypeInstance],
                 sighash: str,
                 notpayable: bool,
                 fromLib: bool,  # actually serialized
                 isConstructor: bool,  # not serialized
                 stateMutability: str,
                 visibility: str,
                 implemented: bool,  # does this function have a body? (false for interface functions)
                 overrides: bool,  # does this function override an interface declaration or super-contract definition?
                 contractName: str,
                 ast_id: Optional[int],
                 where: Optional[Tuple[str, str]] = None  # 1st element: source file name, 2nd element: location string
                 ):
        self.name = name
        self.fullArgs = fullArgs
        self.paramNames = paramNames
        self.returns = returns
        self.sighash = sighash
        self.notpayable = notpayable
        self.fromLib = fromLib
        self.isConstructor = isConstructor
        self.stateMutability = stateMutability
        self.visibility = visibility
        self.where = where
        self.implemented = implemented
        self.ast_id = ast_id
        self.overrides = overrides
        self.contractName = contractName

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "paramNames": self.paramNames,
            "fullArgs": list(map(lambda x: x.as_dict(), self.fullArgs)),
            "returns": list(map(lambda x: x.as_dict(), self.returns)),
            "sighash": self.sighash,
            "notpayable": self.notpayable,
            STATEMUT: self.stateMutability,
            "visibility": self.visibility,
            "isLibrary": self.fromLib,
            "contractName": self.contractName,
        }

    def name_for_contract(self, contract_name: str) -> str:
        return f"{contract_name}.{self.name}"

    def __repr__(self) -> str:
        return repr(self.as_dict())

    def __lt__(self, other: Any) -> bool:
        return self.source_code_signature() < other.source_code_signature()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Func):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.source_code_signature() == other.source_code_signature() and self.signature() == other.signature()

    def __hash__(self) -> int:
        return int(self.sighash, 16)

    def signature(self) -> str:
        """
        Returns the ABI-conforming version of the signature
        """
        return Func.compute_signature(self.name, self.fullArgs, lambda x: x.get_abi_canonical_string(self.fromLib))

    def signature_for_contract(self, contract_name: str) -> str:
        return f"{contract_name}.{self.signature()}"

    def source_code_signature(self) -> str:
        """
        Returns the signature of the function in non-ABI format; The argument types are not
        encoded to the ABI version (e.g. an argument of type 'struct S' will show the struct
        name, not the destructered tuple the ABI uses)
        """
        return Func.compute_signature(self.name, self.fullArgs, lambda x: x.get_source_str())

    @staticmethod
    def compute_signature(name: str, args: List[CT.TypeInstance], signature_getter: Any) -> str:
        return name + "(" + ",".join([signature_getter(x) for x in args]) + ")"

    def same_internal_signature_as(self, other: 'Func') -> bool:
        if self.name != other.name:
            return False
        args_match = (len(self.fullArgs) == len(other.fullArgs) and
                      all([my_arg.matches(other_arg) for my_arg, other_arg in zip(self.fullArgs, other.fullArgs)]))

        rets_match = (len(self.returns) == len(other.returns) and
                      all([my_ret.matches(other_ret) for my_ret, other_ret in zip(self.returns, other.returns)]))
        return args_match and rets_match

    @staticmethod
    def compute_getter_signature(variable_type: CT.TypeInstance) -> Tuple[List[CT.TypeInstance], List[CT.TypeInstance]]:
        return variable_type.compute_getter_signature()


class InternalFunc:
    def __init__(self, fileName: str, contractName: str, func: Func):
        self.canonical_id = f"{fileName}|{contractName}"
        self.declaringContract = contractName
        self.func = func

    def as_dict(self) -> Dict[str, Any]:
        return {
            "canonicalId": self.canonical_id,
            "declaringContract": self.declaringContract,
            "method": self.func.as_dict()
        }
