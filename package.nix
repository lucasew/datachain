{ buildPythonPackage,
 pytestCheckHook
}:

buildPythonPackage {
  pname = "datachain";
  version = builtins.readFile ./datachain/VERSION;

  src = ./.;

  nativeBuildInputs = [ pytestCheckHook ];
}
