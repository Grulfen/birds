{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    nativeBuildInputs = with pkgs.buildPackages; [
        python310Packages.black
        python310Packages.click
        python310Packages.hypothesis
        python310Packages.ipdb
        python310Packages.ipython
        python310Packages.jupyter-core
        python310Packages.keras
        python310Packages.librosa
        python310Packages.notebook
        python310Packages.numpy
        python310Packages.pylsp-mypy
        python310Packages.pytest
        python310Packages.python-lsp-ruff
        python310Packages.python-lsp-server
        python310Packages.requests
        python310Packages.scikit-learn
        python310Packages.seaborn
        python310Packages.soundfile
        python310Packages.tensorflow
        python310Packages.tqdm
        python310Packages.types-requests
    ];
  # Workaround for broken matplotlib package
  shellHook = ''
    export TK_LIBRARY="${pkgs.tk}/lib/${pkgs.tk.libPrefix}"
  '';

}
