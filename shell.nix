{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    buildInputs = [
      (pkgs.python3.withPackages (ps: with ps; [
        aiohttp
        black
        click
        h5py
        hypothesis
        ipdb
        ipython
        isort
        jupyter-core
        keras
        librosa
        notebook
        numpy
        pylsp-mypy
        pytest
        python-lsp-ruff
        python-lsp-server
        scikit-learn
        seaborn
        soundfile
        tensorflow
        termcolor
        tqdm
      ]))
    ];

  # Workaround for broken matplotlib package
  shellHook = ''
    export TK_LIBRARY="${pkgs.tk}/lib/${pkgs.tk.libPrefix}"
    export TF_CPP_MIN_LOG_LEVEL=1
  '';

}
