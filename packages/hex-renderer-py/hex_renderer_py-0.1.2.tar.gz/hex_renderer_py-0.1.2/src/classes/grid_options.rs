use hex_renderer::options::{GridPatternOptions, Point, GridOptions};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::{grid_pattern_options::PyGridPatternOptions, point::PyPoint};

pub fn add_class(_py: Python, m: &PyModule) -> PyResult<()> {
    
    m.add_class::<PyGridOptions>()?;

    Ok(())
}

#[py_gen(bridge = GridOptions)]
#[derive(Clone, PartialEq, PartialOrd, Debug)]
///Main struct for all pattern rendering options
pub struct PyGridOptions {
    ///Thickness of line in relation to distance between points
    /// eg. if the line_thickness = 0.1, and the distance between points is 10 pixels,
    /// then the line_thickness would be 1 pixel
    pub line_thickness: f32,

    #[py_gen(bridge = PyGridPatternOptions)]
    ///Further options for how to render each pattern
    pub pattern_options: GridPatternOptions,

    #[py_gen(bridge = PyPoint)]
    ///Optional point to place in the center of each pattern (helps with determining pattern size at a glance)
    pub center_dot: Point,
}