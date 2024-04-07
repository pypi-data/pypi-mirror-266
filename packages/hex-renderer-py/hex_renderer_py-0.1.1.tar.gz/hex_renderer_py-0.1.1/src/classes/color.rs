use hex_renderer::options::Color;
use interface_macros::py_gen;
use pyo3::{types::PyModule, PyResult, Python};

pub fn add_class(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyColor>()?;

    Ok(())
}

#[py_gen(bridge = Color)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
///Color struct, using RGBA
pub struct PyColor(
    #[py_gen(name = "r")]
    ///Amount of red (0-255)
    u8,
    #[py_gen(name = "g")] 
    ///Amount of red (0-255)
    u8, 
    #[py_gen(name = "b")]
    ///Amount of red (0-255)
    u8, 
    #[py_gen(name = "a")]
    ///Amount of red (0-255)
    u8
);