use hex_renderer::options::{Color, Triangle, CollisionOption, Lines};
use interface_macros::py_gen;
use pyo3::{Python, types::PyModule, PyResult};

use super::{color::PyColor, triangle::PyTriangle, collision_option::PyCollisionOption};

pub fn add_class(py: Python, m: &PyModule) -> PyResult<()> {
    let sub_m = PyModule::new(py, "Lines")?;
    sub_m.add_class::<PyLinesMonocolor>()?;
    sub_m.add_class::<PyLinesGradient>()?;
    sub_m.add_class::<PyLinesSegmentColors>()?;
    
    m.add_submodule(sub_m)?;

    Ok(())
}

#[py_gen(bridge = Lines)]
#[derive(Clone)]
pub enum PyLines {
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Monocolor draws the lines in a single color
    /// if bent = true, the corners will bend on the intersections
    Monocolor {
        #[py_gen(bridge = PyColor)]
        ///Color to draw the lines with
        color: Color,
        ///Whether or not it bends at intersection points
        bent: bool
    },
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Gradient slowly switches between colors (gradient)
    Gradient {
        #[py_gen(bridge = Vec<PyColor>)]
        ///Vec of colors to draw gradients between
        /// If the vec only has 1 item, it's treated as Monocolor
        colors: Vec<Color>,
        ///Minimum number of segments before adding another color to switch between
        /// Eg. if segments_per_color = 10,
        /// 1-9 segments - maximum of 2 colors
        /// 10-19 segments - maximum of 3 colors, 
        segments_per_color: usize,
        ///Whether or not to have the segments bend around corners
        bent: bool
    },
    #[derive(Clone, PartialEq, PartialOrd, Debug)]
    ///Changes colors whenever it reaches an intersection that's already had the current color
    SegmentColors {
        #[py_gen(bridge = Vec<PyColor>)]
        ///Colors to use
        colors: Vec<Color>,
        #[py_gen(bridge = PyTriangle)]
        ///Arrows/Triangles to draw at the start and when switching between colors
        triangles: Triangle,
        #[py_gen(bridge = PyCollisionOption)]
        ///Options for impossible patterns (when you get overlapping segments)
        collisions: CollisionOption,
    }
}