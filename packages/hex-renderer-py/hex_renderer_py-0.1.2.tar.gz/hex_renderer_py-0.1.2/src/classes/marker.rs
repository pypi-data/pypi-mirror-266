use hex_renderer::options::{Color, Marker};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::color::PyColor;

pub fn add_class(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyMarker>()?;

    Ok(())
}

#[py_gen(bridge = Marker)]
#[derive(Clone, PartialEq, PartialOrd, Debug)]
///Specifier for how to draw a shape (not necessarily a circle)
pub struct PyMarker {
    #[py_gen(bridge = PyColor)]
    ///The color to draw it with
    color: Color,
    ///The radius of the shape
    radius: f32
}