# thermal-storage
A program which simulates the behavior of a thermal storage

- To change properties: data &rarr; properties.txt
- To view used equations: equations &rarr; single-phase-model 

The directory has a following structure:
- data
  - properties.txt
- equations
  - single-phase-model
  - continuous-model (needs to be added)
- model
  - continuous-model
    - package
      - export.py
      - initialize.py
      - mapping.py
    - arrays.py
    - storage.py
  - single-phase-model
    - package
      - export.py
      - initialize.py
      - mapping.py
    - arrays.py
    - storage.py
  - properties.py
