# BioHackRxiv for the 2nd SpatialData Hackathon
Padua, 2026
Pre-print published here: TBA

## How to Build

Instructions and examples are available [here](https://github.com/biohackrxiv/bhxiv-gen-pdf/).

1. **Build the required Docker container** (run the command inside the `bhxiv-gen-pdf` repo) (this process takes 5-10 minutes):
   ```bash
   docker build -t biohackrxiv/gen-pdf:local -f docker/Dockerfile .
   ```

2. **Build the .pdf** (run the command inside this folder):
   ```bash
   docker run --rm -it -v $(pwd):/work -w /work biohackrxiv/gen-pdf:local gen-pdf .
   ```
