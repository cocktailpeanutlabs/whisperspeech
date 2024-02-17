module.exports = {
  "cmds": {
    "nvidia": "pip install torch torchvision torchaudio xformers --index-url https://download.pytorch.org/whl/cu118",
    "amd": "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6",
    "default": "pip3 install --pre torch torchvision torchaudio"
  },
//  "requires": [{
//    "type": "conda",
//    "name": "ffmpeg",
//    "args": "-c conda-forge"
//  }],
  "run": [{
    "method": "shell.run",
    "params": {
      "venv": "env",
      "message": [
        "{{(gpu === 'nvidia' ? self.cmds.nvidia : ((gpu === 'amd' && platform === 'linux') ? self.cmds.amd : self.cmds.default))}}",
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
