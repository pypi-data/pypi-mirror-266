#!/usr/bin/env bash
module add espresso/540-g-485-ompi-110
mpirun -np 1 pw.x -in pw-scf.in &> pw-scf.out
