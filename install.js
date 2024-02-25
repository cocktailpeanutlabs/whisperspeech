module.exports = {
  "cmds": {
    "win32": {
      "nvidia": `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`,
      "amd": "pip install torch-directml",
      "none": "pip install torch torchvision torchaudio"
    },
    "darwin": "pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu",
    "linux": {
      "nvidia": `pip install torch torchvision torchaudio`,
      "amd": "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7",
      "none": "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    }
  },
  "run": [{
    "method": "shell.run",
    "params": {
      "venv": "env",
      "message": [
        "{{platform === 'darwin' ? self.cmds.darwin : self.cmds[platform][gpu]}}",
        "pip install -r requirements.txt",
      ]
    },
  }, {
    "method": "fs.share",
    "params": {
      "venv": "env"
    }
  }, {
    "method": "notify",
    "params": {
      "html": "Click the 'start' tab to get started!"
    }
  }]
}
