# Integrated-Digital-PCR

This project utilizes integrated digital PCR based on Raspberry Pi 4

Step 1) Thermal cycling
    This step is for DNA amplification.
    By the 3 thermal steps,(1) denaturation, (2) annealing (3) extension activate.
    
Step 2) Fluorescence imaging
    This step is for fluorescence imaging of micropartition chip (self-priming chip)
    Using multi-color LED and multi bandpass filter, 3 fluorescence images are taken
    
Step 3) Digital PCR analysis
    This step is for quantitative analysis of DNA copies
    By detecting intensity of fluorescence images, positive/negative calls are analyzed.
    Then, DNA copy number is calculated via Poisson's distribution
