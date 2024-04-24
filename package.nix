{ buildPythonPackage,
 pytestCheckHook,
 pynacl
}:

buildPythonPackage {
  pname = "datachain";
  version = builtins.replaceStrings [ "\n" ] [ "" ] (builtins.readFile ./datachain/VERSION);

  src = ./.;

  shellHook = ''
  PYTHONPATH=$PYTHONPATH:$(pwd)
  '';

  nativeBuildInputs = [ pytestCheckHook ];

  buildInputs = [ pynacl ];
}
