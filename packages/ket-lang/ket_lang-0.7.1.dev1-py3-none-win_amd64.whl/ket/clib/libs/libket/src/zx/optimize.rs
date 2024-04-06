// SPDX-FileCopyrightText: 2024 Gabriel da Silva Cardoso <cardoso.gabriel@grad.ufsc.br>
//
// SPDX-License-Identifier: Apache-2.0

use quizx::circuit::Circuit;
use quizx::extract::ToCircuit;

use crate::error::Result;
use crate::qasmv2::instruction_set::InstructionSet;
use crate::Process;
use quizx::hash_graph::Graph;

pub fn optimize(process: &mut Process) -> Result<()> {
    let qasm = process.to_qasmv2(false, InstructionSet::QELIB).unwrap();
    let c = Circuit::from_qasm(&qasm).unwrap();
    let mut g: Graph = c.clone().to_graph();
    quizx::simplify::clifford_simp(&mut g);
    let c_optmized = g.to_circuit().unwrap();
    let qasm_optimized = c_optmized.to_qasm();
    process.from_qasmv2(&qasm_optimized, InstructionSet::QELIB)
}
