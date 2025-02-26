{ pkgs ? import <nixpkgs> {} }:

let
  dc-schema = pkgs.python312Packages.buildPythonPackage rec {
      pname = "dc_schema";
      version = "0.0.8";

      src = pkgs.python312Packages.fetchPypi {
        inherit version;
        inherit pname;
        sha256 = "sha256-if7XksY7gKkdT+9yP5rvvKg5UuthH7wWjvg4G/Yqy7U=";
      };
    };
in
  pkgs.mkShell {
    buildInputs = with pkgs; [
      deno
      python3
      python312Packages.dataclasses-json
      dc-schema
      nixfmt-rfc-style
    ];
  }
