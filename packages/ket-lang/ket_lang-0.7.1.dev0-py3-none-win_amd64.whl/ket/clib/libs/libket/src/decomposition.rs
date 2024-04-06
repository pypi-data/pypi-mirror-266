// SPDX-FileCopyrightText: 2024 Evandro Chagas Ribeiro da Rosa <evandro@quantuloop.com>
//
// SPDX-License-Identifier: Apache-2.0

use num::complex::{Complex, ComplexFloat};

use crate::ir::Cf64;
use crate::ir::Matrix;
use crate::{Instruction, QuantumGate};

type Vector = (Cf64, Cf64);

fn extract_phase(matrix: Matrix) -> f64 {
    let ((a, b), (c, d)) = matrix;
    let det = a * d - b * c;
    1.0 / 2.0 * det.im.atan2(det.re)
}

fn is_close(a: f64, b: f64) -> bool {
    (a - b).abs() < 1e-10
}

pub fn zyz(matrix: Matrix) -> (f64, f64, f64, f64) {
    let phase = extract_phase(matrix);
    let e_phase = (-Complex::<_>::i() * phase).exp();

    let matrix = (
        (matrix.0 .0 * e_phase, matrix.0 .1 * e_phase),
        (matrix.1 .0 * e_phase, matrix.1 .1 * e_phase),
    );

    let matrix_0_1_abs = matrix.0 .0.abs().max(-1.0).min(1.0);

    let theta_1 = if matrix.0 .0.abs() >= matrix.0 .1.abs() {
        2.0 * matrix_0_1_abs.acos()
    } else {
        2.0 * matrix.0 .1.abs().asin()
    };

    let theta_1_2_cos = (theta_1 / 2.0).cos();
    let theta_0_plus_2 = if !is_close(theta_1_2_cos, 0.0) {
        let tmp = matrix.1 .1 / theta_1_2_cos;
        2.0 * tmp.im.atan2(tmp.re)
    } else {
        0.0
    };

    let theta_1_2_sin = (theta_1 / 2.0).sin();
    let theta_0_sub_2 = if !is_close(theta_1_2_sin, 0.0) {
        let tmp = matrix.1 .0 / theta_1_2_sin;
        2.0 * tmp.im.atan2(tmp.re)
    } else {
        0.0
    };

    let theta_0 = (theta_0_plus_2 + theta_0_sub_2) / 2.0;
    let theta_2 = (theta_0_plus_2 - theta_0_sub_2) / 2.0;

    (phase, theta_0, theta_1, theta_2)
}

pub fn eigen(matrix: Matrix) -> ((Complex<f64>, Vector), (Complex<f64>, Vector)) {
    let ((a, b), (c, d)) = matrix;

    let m = (a + d) / 2.0;
    let p = a * d - b * c;

    let lambda_1 = m + (m.powi(2) - p).sqrt();
    let lambda_2 = m - (m.powi(2) - p).sqrt();

    let v1 = (lambda_1 - d, c);
    let v2 = (b, lambda_2 - a);

    let p1 = (v1.0.abs().powi(2) + v1.1.abs().powi(2)).sqrt();
    let p2 = (v2.0.abs().powi(2) + v2.1.abs().powi(2)).sqrt();

    let v1 = (v1.0 / p1, v1.1 / p1);
    let v2 = (v2.0 / p2, v2.1 / p2);

    ((lambda_1, v1), (lambda_2, v2))
}

pub fn gate_u(
    matrix: Matrix,
    coef: f64,
    signal: i32,
) -> (f64, QuantumGate, QuantumGate, QuantumGate) {
    assert!(signal == -1 || signal == 1);

    let param = 1.0 / coef;

    let ((lambda1, v1), (lambda_2, v2)) = eigen(matrix);

    let value_1 = lambda1.powf(param);
    let gate_1 = (
        (value_1 * v1.0 * v1.0.conj(), value_1 * v1.0 * v1.1.conj()),
        (value_1 * v1.1 * v1.0.conj(), value_1 * v1.1 * v1.1.conj()),
    );

    let value_2 = lambda_2.powf(param);
    let gate_2 = (
        (value_2 * v2.0 * v2.0.conj(), value_2 * v2.0 * v2.1.conj()),
        (value_2 * v2.1 * v2.0.conj(), value_2 * v2.1 * v2.1.conj()),
    );

    let gate = (
        (gate_1.0 .0 + gate_2.0 .0, gate_1.0 .1 + gate_2.0 .1),
        (gate_1.1 .0 + gate_2.1 .0, gate_1.1 .1 + gate_2.1 .1),
    );

    let gate = if signal == -1 {
        (
            (gate.0 .0.conj(), gate.1 .0.conj()),
            (gate.0 .1.conj(), gate.1 .1.conj()),
        )
    } else {
        gate
    };

    let (phase, theta_0, theta_1, theta_2) = zyz(gate);

    (
        phase,
        QuantumGate::RotationZ(crate::Angle::Scalar(theta_2)),
        QuantumGate::RotationY(crate::Angle::Scalar(theta_1)),
        QuantumGate::RotationZ(crate::Angle::Scalar(theta_0)),
    )
}

pub fn c1c2(matrix: Matrix, qubits: &[usize], first: bool, step: i32) -> Vec<Instruction> {
    assert!(step == -1 || step == 1);

    let mut instructions = Vec::new();

    let start = if step == 1 { 0 } else { 1 };

    let mut qubit_pairs: Vec<(usize, usize)> = (0..qubits.len())
        .enumerate()
        .flat_map(|(i, t)| {
            if i > start {
                (start..i).map(|c| (c, t)).collect::<Vec<(usize, usize)>>()
            } else {
                vec![]
            }
        })
        .collect();

    qubit_pairs.sort_by_key(|(c, t)| c + t);
    if step == 1 {
        qubit_pairs.reverse();
    }

    for (control, target) in qubit_pairs {
        let exponent: i32 = target as i32 - control as i32;
        let exponent = if control == 0 { exponent - 1 } else { exponent };
        let param = 2.0.powi(exponent);
        let signal = if control == 0 && !first { -1 } else { 1 };
        let signal = signal * step;
        if target == qubits.len() - 1 && first {
            let (phase, gate_0, gate_1, gate_2) = gate_u(matrix, param, signal);
            instructions.push(Instruction::Gate {
                gate: QuantumGate::Phase(crate::Angle::Scalar(phase)),
                control: vec![],
                target: qubits[control],
            });
            instructions.push(Instruction::Gate {
                gate: gate_0,
                target: qubits[target],
                control: vec![qubits[control]],
            });
            instructions.push(Instruction::Gate {
                gate: gate_1,
                target: qubits[target],
                control: vec![qubits[control]],
            });
            instructions.push(Instruction::Gate {
                gate: gate_2,
                target: qubits[target],
                control: vec![qubits[control]],
            });
        } else {
            instructions.push(Instruction::Gate {
                gate: QuantumGate::RotationX(crate::Angle::Scalar(
                    std::f64::consts::PI * signal as f64 / param,
                )),
                target: qubits[target],
                control: vec![qubits[control]],
            });
        }
    }

    instructions
}

pub fn decompose_u2(gate: Instruction) -> Vec<Instruction> {
    let (gate, target, control) = if let Instruction::Gate {
        gate,
        target,
        control,
    } = gate
    {
        (gate, target, control)
    } else {
        panic!("Instruction is not a gate")
    };

    let matrix = gate.matrix();
    let mut control_target = control.clone();
    control_target.push(target);

    let mut instruction = Vec::new();

    instruction.append(&mut c1c2(matrix, &control_target, true, 1));
    instruction.append(&mut c1c2(matrix, &control_target, true, -1));
    instruction.append(&mut c1c2(matrix, &control, false, 1));
    instruction.append(&mut c1c2(matrix, &control, false, -1));

    instruction
}

#[cfg(test)]
mod tests {
    use crate::{Configuration, Process};

    use super::*;

    #[test]
    fn print_decomposition() {
        let mut p = Process::new(Configuration {
            allow_measure: true,
            allow_sample: true,
            allow_exp_value: true,
            allow_dump: true,
            valid_after_measure: true,
            continue_after_sample: true,
            continue_after_exp_value: true,
            continue_after_dump: true,
            decompose: true,
            live_quantum_execution: None,
            batch_execution: None,
            num_qubits: 100,
            execution_timeout: None,
        });

        let n = 3;

        let trt_qubit = p.allocate_qubit().unwrap();
        let ctr_qubits: Vec<usize> = (0..n - 1).map(|_| p.allocate_qubit().unwrap()).collect();

        p.ctrl_push(&ctr_qubits).unwrap();
        p.apply_gate(QuantumGate::PauliY, trt_qubit).unwrap();
        p.ctrl_pop().unwrap();

        println!("{:#?}", p.instructions)
    }
}
