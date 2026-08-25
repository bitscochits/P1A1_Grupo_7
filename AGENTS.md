# Project

Laboratorio estructural digital 3D del Edificio de Ingeniería, Universidad de los Andes.

# Units

SI: metros (m), kilonewtons (kN), kPa (kN/m²).

# Structural model

- Global model: linear elastic 3D.
- Slabs are not FE modeled.
- Floor gravity load = slab self weight + uniform finishes.
- Slab loads are transferred through tributary areas.
- RC capacity analysis is separate from the global model.

# Architecture

- OpenSees owns structural analysis.
- Unity owns visualization/preprocessing/interaction.
- JSON is the contract between both.
- Mobile does not run OpenSees in the base project.

# Verification rules

- Check equilibrium: sum(F_applied) + sum(R) ≈ 0.
- Check units: always use m, kN, kPa.
- Check local axes: verify geomTransf orientation.
- Check superposition: R(A+B) = R(A) + R(B).
- Never modify reference benchmark results without justification.

# Python environment

- Use Python 3.12 (openseespy does not support 3.14).
- Path: C:\Users\edfev\AppData\Local\Programs\Python\Python312\python.exe
- Packages: openseespy, ezdxf

# File conventions

- benchmark_3d.py: main structural model
- extract_*.py: data extraction scripts
- error_*.py: deliberate error demonstrations
- results/*.json: model output data
- Planos/*.dxf: converted architectural drawings
