use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn start_server() -> PyResult<()> {
    println!("Starting server...");
    Ok(())
}

/// A Python module implemented in Rust.
#[pymodule]
fn axumapi(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(start_server, m)?)?;
    Ok(())
}
