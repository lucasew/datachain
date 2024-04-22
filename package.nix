{ buildPythonPackage,
 pytestCheckHook
}:

buildPythonPackage {
  pname = "datachain";
  version = builtins.readFile ./datachain/VERSION;

  src = ./.;

  shellHook = ''
  PYTHONPATH=$PYTHONPATH:$(pwd)
  '';

  nativeBuildInputs = [ pytestCheckHook ];
}
